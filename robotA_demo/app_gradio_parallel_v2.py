#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robot A + Robot B Parallel System - Academic UI
二重ロボット対話システム - 学術的インターフェース
"""

import os
import sys

# 设置 UTF-8 编码 (Windows 兼容性)
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    import io
    import codecs
    # 强制使用UTF-8输出，忽略编码错误
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', errors='replace', line_buffering=True)

# 抑制CUDA/cuDNN警告 (在导入任何深度学习库之前)
import warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# 抑制ONNX Runtime和CUDA警告
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 抑制TensorFlow警告
os.environ['CUDA_MODULE_LOADING'] = 'LAZY'  # 延迟加载CUDA模块
os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'  # 抑制Transformers警告

import gradio as gr
import numpy as np
from pathlib import Path
import time

# 纯文本对话模式
print("\n" + "=" * 70)
print("Text-Only Dialogue Mode")
print("=" * 70)
print("[INFO] ONNX Runtime CPU: Emotion Recognition (Text)")
print("[INFO] Pure Text Interaction - No TTS/ASR")
print("=" * 70 + "\n")

# 延迟导入受限模块，避免启动时加载失败
get_onnx_wrime_luke_recognizer = None
get_onnx_rag_retriever = None

# 基础模块可以直接导入
from core.llm_gemini import GeminiLLM
from core.agents import RobotAAgent, RobotBAgent, detect_advice_intent


class ParallelAgentSystem:
    """Parallel agent system with text emotion recognition (text-only mode)"""
    
    def __init__(self, scenario: str = "unified"):
        """
        Initialize the parallel agent system
        
        Args:
            scenario: 保留参数用于兼容旧调用（统一模式）
        """
        self.scenario = "unified"
        self.emotion_recognizer = None
        self.rag_retriever_a = None
        self.rag_retriever_b = None
        self.llm = None
        
        self.robot_a = RobotAAgent(scenario="unified")
        self.robot_b = RobotBAgent(scenario="unified")
        
        print("[OK] Text-only parallel agent system initialized: unified")
    
    def set_scenario(self, scenario: str):
        """
        保留旧接口：统一模式下忽略场景切换请求
        
        Args:
            scenario: ignored
        """
        self.scenario = "unified"
        self.robot_a = RobotAAgent(scenario="unified")
        self.robot_b = RobotBAgent(scenario="unified")
        # Clear RAG retrievers to force reload
        self.rag_retriever_a = None
        self.rag_retriever_b = None
        print("[OK] Unified mode active (scenario switch ignored)")
    
    def _ensure_complete_sentence(self, text: str) -> str:
        """
        Ensure text ends with a complete sentence (ends with proper punctuation)
        """
        if not text:
            return text
        
        # Japanese sentence ending punctuation
        sentence_endings = ['。', '？', '！', '.', '?', '!']
        
        # Check if already ends with proper punctuation
        if text[-1] in sentence_endings:
            return text
        
        # Find the last complete sentence
        last_pos = -1
        for ending in sentence_endings:
            pos = text.rfind(ending)
            if pos > last_pos:
                last_pos = pos
        
        # If found a sentence ending, truncate there
        if last_pos > 0:
            return text[:last_pos + 1]
        
        # If no sentence ending found, return as is
        return text
    
    def _b_has_given_suggestion(self, response_b: str) -> bool:
        """
        Check if Robot B's response contains concrete action suggestions (B5 stage)
        B5 is when B provides single actionable suggestion with 3 elements:
        - 下一步做什么 (action content)
        - 如何做 (execution method)
        - 做到什么算完成 (completion criteria)
        """
        suggestion_markers = [
            "試して", "やって", "してみ",
            "方法", "どうですか", "どうかな",
            "成功", "完了", "できたら",
            "明日", "今日", "今夜",  # Temporal markers for actionable suggestions
            "まず", "最初に"  # Action sequence markers
        ]
        return any(marker in response_b for marker in suggestion_markers)
    
    def _ensure_components(self, agent_type="A"):
        """Lazy load components as needed with graceful degradation"""
        global get_onnx_wrime_luke_recognizer, get_onnx_rag_retriever
        
        # 尝试加载情感识别模块（可能被 Windows 安全策略阻止）
        if self.emotion_recognizer is None:
            try:
                if get_onnx_wrime_luke_recognizer is None:
                    from core.emo_wrime_luke_onnx import get_onnx_wrime_luke_recognizer as loader
                    get_onnx_wrime_luke_recognizer = loader
                self.emotion_recognizer = get_onnx_wrime_luke_recognizer(use_gpu=False)
            except Exception as e:
                print(f"⚠ 文本情感识别模块加载失败: {str(e)[:60]}")
                self.emotion_recognizer = None
        
        if agent_type == "A" and self.rag_retriever_a is None:
            try:
                if get_onnx_rag_retriever is None:
                    from core.rag_onnx import get_onnx_rag_retriever as loader
                    get_onnx_rag_retriever = loader
                self.rag_retriever_a = get_onnx_rag_retriever(agent_type="A", use_gpu=False)
            except Exception as e:
                print(f"⚠ RAG 检索器 A 加载失败: {str(e)[:60]}")
                self.rag_retriever_a = None
                
        elif agent_type == "B" and self.rag_retriever_b is None:
            try:
                if get_onnx_rag_retriever is None:
                    from core.rag_onnx import get_onnx_rag_retriever as loader
                    get_onnx_rag_retriever = loader
                self.rag_retriever_b = get_onnx_rag_retriever(agent_type="B", use_gpu=False)
            except Exception as e:
                print(f"⚠ RAG 检索器 B 加载失败: {str(e)[:60]}")
                self.rag_retriever_b = None
        
        if self.llm is None:
            self.llm = GeminiLLM()
    
    def process_turn(
        self,
        user_input: str,
        chat_history_a: list,
        chat_history_b: list,
        use_rag: bool = True
    ):
        """Process a single turn with text emotion recognition"""
        self._ensure_components(agent_type="A")
        
        # 1. Text emotion (if available)
        print(f"\n[DEBUG] Analyzing text: {user_input[:100]}...")
        if self.emotion_recognizer is not None:
            text_emo_result = self.emotion_recognizer.predict(user_input)
            print(f"[DEBUG] Text emotion result: {text_emo_result['emo_top']} (conf: {text_emo_result.get('emo_conf', 0):.3f})")
            print(f"[DEBUG] Full distribution: {text_emo_result.get('emo8_dist', [])}")
            # 修复：统一字段名为 emo_score
            if 'emo_conf' in text_emo_result:
                text_emo_result['emo_score'] = text_emo_result['emo_conf']
        else:
            # 情感识别不可用，使用中性默认值
            print("[DEBUG] Text emotion recognizer not available, using neutral default")
            text_emo_result = {
                'emo_top': 'trust',  # 默认使用 trust（中性/信任）
                'emo_score': 0.5,
                'emo_conf': 0.5,
                'emo8_dist': [0.125] * 8  # 均匀分布
            }

        # Keep final emotion source as text-only
        emotion_result = {
            "final_emotion": text_emo_result.get('emo_top', 'trust'),
            "final_score": text_emo_result.get('emo_score', text_emo_result.get('emo_conf', 0.0)),
            "modalities_used": ["text"]
        }
        user_emotion = emotion_result['final_emotion']
        
        # Check Robot B status first
        # Note: chat_history_a includes opening message, so we need to adjust count
        # Opening: len=1, After 1st user input: len=2, After 2nd: len=3, After 3rd: len=4
        turn_count_a = len(chat_history_a)
        turn_count_b = len(chat_history_b)
        b_has_appeared = len(chat_history_b) > 0
        
        # B appears after A's 3rd response (A1, A2, A3)
        # With opening at len=1, after 3 user interactions we have len=4
        should_b_appear = turn_count_a >= 4 and not b_has_appeared
        # B can continue responding after B6 for closure and new episodes (no hard limit)
        should_b_respond = b_has_appeared
        
        # Robot A only responds before B appears
        response_a = None
        response_b = None
        new_history_a = chat_history_a
        new_history_b = chat_history_b
        
        if not b_has_appeared:
            # Robot A responds normally (first 3 turns)
            rag_context_a = ""
            if use_rag and self.rag_retriever_a:
                rag_results = self.rag_retriever_a.retrieve(user_input, top_k=2)
                if rag_results:
                    rag_context_a = self.rag_retriever_a.format_rag_context(rag_results, max_topics=2)
            
            messages_a = self.robot_a.format_prompt_with_history(
                chat_history=chat_history_a,
                user_input=user_input,
                user_emotion=user_emotion,
                rag_context=rag_context_a
            )
            
            response_a = self.llm.generate(messages_a, max_tokens=2000)
            
            # Ensure response ends with complete sentence
            response_a = self._ensure_complete_sentence(response_a)
            
            new_history_a = chat_history_a + [{"user": user_input, "assistant": response_a}]
            
            # Check if this is A's 3rd turn (with opening: len=4)
            # If yes, Robot B should immediately appear (without waiting for user's 4th input)
            if len(new_history_a) == 4:
                print(f"\n[DEBUG] A's 3rd turn completed. Robot B will now appear automatically.")
                self._ensure_components(agent_type="B")
                
                # Generate B's welcome message
                welcome_msg = self.robot_b.get_welcome_message()
                print(f"[DEBUG] B's welcome: {welcome_msg}")
                
                # Generate B's B1 (Alignment) based on A's conversation history
                # Use the last user input for B1 alignment
                rag_context_b = ""
                if use_rag and self.rag_retriever_b:
                    rag_results = self.rag_retriever_b.retrieve(user_input, top_k=2)
                    if rag_results:
                        rag_context_b = self.rag_retriever_b.format_rag_context(rag_results, max_topics=2)
                
                messages_b = self.robot_b.format_prompt_with_history(
                    chat_history=[],  # Empty history for first appearance
                    user_input=user_input,
                    user_emotion=user_emotion,
                    rag_context=rag_context_b,
                    robot_b_turn_count=1,
                    is_first_appearance=True,
                    chat_history_a=new_history_a
                )
                
                b1_response = self.llm.generate(messages_b, max_tokens=2000)
                b1_response = self._ensure_complete_sentence(b1_response)
                
                # B1 directly starts (no separate welcome message to avoid repetition)
                response_b = welcome_msg + ("\n\n" if welcome_msg else "") + b1_response
                print(f"[DEBUG] B's B1 response: {response_b[:100]}...")
                
                # Update B's history - use empty user to show only B's first message
                # The user's input was already shown in chatbot_a
                new_history_b = [{"user": "", "assistant": response_b}]
                
                # Update b_has_appeared flag
                b_has_appeared = True
        
        # Handle Robot B's subsequent responses (B2-B6)
        elif should_b_respond:
            self._ensure_components(agent_type="B")
            
            rag_context_b = ""
            if use_rag and self.rag_retriever_b:
                rag_results = self.rag_retriever_b.retrieve(user_input, top_k=2)
                if rag_results:
                    rag_context_b = self.rag_retriever_b.format_rag_context(rag_results, max_topics=2)
            
            # B's first appearance is now handled in A's 3rd turn, so is_first_appearance is always False here
            is_first_appearance = False
            
            messages_b = self.robot_b.format_prompt_with_history(
                chat_history=chat_history_b,
                user_input=user_input,
                user_emotion=user_emotion,
                rag_context=rag_context_b,
                robot_b_turn_count=turn_count_b + 1,
                is_first_appearance=is_first_appearance,
                chat_history_a=chat_history_a
            )
            
            response_b = self.llm.generate(messages_b, max_tokens=2000)
            
            # Ensure B's response ends with complete sentence
            response_b = self._ensure_complete_sentence(response_b)
            
            # Don't truncate B's response - let suggestions be complete
            new_history_b = chat_history_b + [{"user": user_input, "assistant": response_b}]
            
            # Robot A comments from turn 6 (B4) onwards
            # B1-B3: A does not intervene
            # B4+: A always provides supportive comment after B's response (no keyword detection)
            print(f"\n[DEBUG] 检查A支持条件 - turn_count_b: {turn_count_b}, 需要>=3")
            print(f"[DEBUG] B的回复: {response_b[:100]}...")
            
            if turn_count_b >= 3:
                print(f"\n[DEBUG] 条件满足！生成A的支持性评论...")
                supportive_comment = self.robot_a.generate_supportive_comment(response_b, self.llm)
                print(f"[DEBUG] A的支持评论: {supportive_comment}")
                # Use actual user_input instead of "[サポート]" marker to avoid display merge
                new_history_a.append({"user": user_input, "assistant": supportive_comment})
            else:
                print(f"[DEBUG] 条件不满足（turn_count_b < 3），A不介入")
        
        # Format emotion info
        emotion_info = self._format_emotion_info(
            text_emo_result, 
            emotion_result
        )
        
        emotion_flow = self._format_emotion_flow(
            text_emo_result,
            emotion_result
        )
        
        status_msg = f"[OK] Processing completed | Text emotion: {user_emotion}"
        
        # TTS 播放逻辑
        self._ensure_components(need_tts=True)
        try:
            latest_response_a = None
            latest_response_b = None
            is_b_first_appearance_turn = False  # Flag to track if this is B's first appearance
            
            # 检查 B 是否有新回复
            if len(new_history_b) > len(chat_history_b):
                latest_response_b = new_history_b[-1]["assistant"]
                print(f"\n[DEBUG] B 有新回复: {latest_response_b[:50]}...")
                
                # Check if this is B's first appearance (chat_history_b was empty)
                if len(chat_history_b) == 0:
                    is_b_first_appearance_turn = True
                    print(f"\n[DEBUG] 检测到B首次登场")
            
            # 检查 A 是否有新回复
            if len(new_history_a) > len(chat_history_a):
                # A 有新消息
                last_message = new_history_a[-1]
                print(f"\n[DEBUG] A 的最后消息 - user: {last_message['user']}, assistant: {last_message['assistant'][:50]}...")
                
                if b_has_appeared and not is_b_first_appearance_turn:
                    # B 已出现且不是首次登场，检查是否是支持性评论
                    if last_message["user"] == "[サポート]":
                        latest_response_a = last_message["assistant"]
                        print(f"\n[DEBUG] 提取到 A 的支持性评论: {latest_response_a[:50]}...")
                else:
                    # B 未出现 或 B首次登场，是 A 的正常回复
                    latest_response_a = last_message["assistant"]
                    print(f"\n[DEBUG] A 的正常回复: {latest_response_a[:50]}...")
            
            # 播放逻辑
            if latest_response_a and latest_response_b and is_b_first_appearance_turn:
                # B 首次登场：先 A（引荐）后 B（欢迎+B1）
                print(f"\n[TTS] 播放顺序: Robot A (引荐) → Robot B (首次登场)")
                print(f"[TTS] A 的文本: {latest_response_a[:100]}...")
                print(f"[TTS] B 的文本: {latest_response_b[:100]}...")
                # Use dual synthesis but with A first, B second
                self.tts_engine.synthesize_dual_ab_order(
                    text_a=latest_response_a,
                    text_b=latest_response_b
                )
            elif latest_response_b and latest_response_a:
                # B 和 A 都有回复（B已经登场，A提供气氛支持）：先 B 后 A
                print(f"\n[TTS] 播放顺序: Robot B → Robot A (气氛支持)")
                print(f"[TTS] B 的文本: {latest_response_b[:100]}...")
                print(f"[TTS] A 的文本: {latest_response_a[:100]}...")
                self.tts_engine.synthesize_dual(
                    text_b=latest_response_b,
                    text_a=latest_response_a
                )
            elif latest_response_b:
                # 只有 B 回复
                print(f"\n[TTS] 播放 Robot B")
                print(f"[TTS] B 的文本: {latest_response_b[:100]}...")
                self.tts_engine.synthesize_and_play(latest_response_b, robot="B")
            elif latest_response_a:
                # 只有 A 回复（B 出现前的阶段）
                print(f"\n[TTS] 播放 Robot A")
                print(f"[TTS] A 的文本: {latest_response_a[:100]}...")
                self.tts_engine.synthesize_and_play(latest_response_a, robot="A")
            else:
                print(f"\n[TTS] 警告: 没有检测到需要播放的内容")
        except Exception as e:
            print(f"[TTS] 语音播放错误: {e}")
            import traceback
            traceback.print_exc()
        
        return (new_history_a, new_history_b, emotion_info, emotion_flow, status_msg)
    
    def _format_emotion_info(self, text_emo, emotion_result) -> str:
        """Format text-only emotion information"""
        lines = ["**テキスト感情分析**\n"]
        
        # Text emotion
        if text_emo:
            score = text_emo.get('emo_score', text_emo.get('emo_conf', 0))
            lines.append(f"[TEXT] **テキスト感情**: {text_emo.get('emo_top', 'N/A')} (信頼度: {score:.2%})")
        
        lines.append(f"\n[FINAL] **最終採用感情**: **{emotion_result['final_emotion'].upper()}** (信頼度: {emotion_result['final_score']:.2%})")
        lines.append(f"[DATA] 使用モダリティ: {' + '.join(emotion_result['modalities_used'])}")
        
        return "\n\n".join(lines)
    
    def _format_emotion_flow(self, text_emo, emotion_result) -> str:
        """Format text emotion recognition flow for display"""
        flow_lines = []
        
        flow_lines.append("【感情認識フロー】")
        flow_lines.append("")
        
        # Step 1: Text
        if text_emo:
            score = text_emo.get('emo_score', text_emo.get('emo_conf', 0))
            flow_lines.append(f"[1] テキスト感情分析 → {text_emo.get('emo_top', 'N/A')} (信頼度: {score:.2%})")

        flow_lines.append("")
        flow_lines.append("↓ テキスト感情を直接採用")
        flow_lines.append("")
        flow_lines.append(f"[結果] {emotion_result['final_emotion'].upper()}")
        
        return "\n".join(flow_lines)


# Initialize system with unified scenario
system = ParallelAgentSystem(scenario="unified")


def format_chat_display(chat_history):
    """Format chat history for Gradio chatbot (dict format for Gradio 6.x)"""
    display = []
    for turn in chat_history:
        u = turn.get("user", "")
        a = turn.get("assistant", "")

        # Skip system markers, avoid showing "user: [開始]"
        if u and u not in ["[開始]", "[サポート]"]:
            display.append({"role": "user", "content": u})

        if a:
            display.append({"role": "assistant", "content": a})
    return display
def submit_message(
    user_input,
    chat_history_a,
    chat_history_b,
    use_rag
):
    """Handle message submission (text only)"""
    
    # Check if we have text input
    if not user_input or (isinstance(user_input, str) and not user_input.strip()):
        return (
            chat_history_a,
            format_chat_display(chat_history_a),
            chat_history_b,
            format_chat_display(chat_history_b),
            "",
            "[WARNING] テキストを入力してください",
            "入力待機中...",
            ""
        )
    
    # Process turn
    try:
        (
            new_history_a,
            new_history_b,
            emotion_info,
            emotion_flow,
            status_msg
        ) = system.process_turn(
            user_input=user_input,
            chat_history_a=chat_history_a,
            chat_history_b=chat_history_b,
            use_rag=use_rag
        )
        
        return (
            new_history_a,
            format_chat_display(new_history_a),
            new_history_b,
            format_chat_display(new_history_b),
            "",  # Clear text input
            status_msg,
            emotion_flow,
            emotion_info
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return (
            chat_history_a,
            format_chat_display(chat_history_a),
            chat_history_b,
            format_chat_display(chat_history_b),
            user_input,
            f"[ERROR] エラー: {str(e)}",
            "入力待機中...",
            ""
        )

def init_ui():
    opening = system.robot_a.get_opening_message()
    # State 中 user 为空字符串，只有 assistant 开场白
    history_a = [{"user": "", "assistant": opening}]
    display_a = [{"role": "assistant", "content": opening}]
    return history_a, display_a, [], [], "[READY] システム準備完了", "入力待機中...", "入力待機中..."


def reset_session():
    """Reset the session with Robot A's opening message"""
    global system
    
    # Get Robot A's opening message
    opening_message = system.robot_a.get_opening_message()
    
    # State: user 为空，只有 assistant 开场白
    initial_history_a = [{"user": "", "assistant": opening_message}]
    
    # Display: 字典格式
    initial_display_a = [{"role": "assistant", "content": opening_message}]
    
    return (
        initial_history_a,  # chat_history_a with opening
        initial_display_a,  # display_a with opening
        [],  # chat_history_b
        [],  # display_b
        "",  # text_input
        "[SYSTEM] 新規セッション開始 - Robot A が開場白を言いました",
        "入力待機中...",  # emotion_flow
        ""  # emotion_display
    )


def regenerate_last_response(
    chat_history_a,
    chat_history_b,
    use_rag
):
    """Regenerate the last bot response"""
    
    # Check if there's any history to regenerate
    if len(chat_history_a) <= 1 and len(chat_history_b) == 0:
        # Only opening message, nothing to regenerate
        return (
            chat_history_a,
            format_chat_display(chat_history_a),
            chat_history_b,
            format_chat_display(chat_history_b),
            "[WARNING] 再生成する内容がありません",
            "入力待機中...",
            ""
        )
    
    # Determine which robot made the last response
    last_turn_a = len(chat_history_a)
    last_turn_b = len(chat_history_b)
    
    # Get the last user input and rollback history
    if last_turn_b > 0:
        # Robot B has responded, regenerate B (and possibly A's support comment)
        last_user_input = chat_history_b[-1]["user"]
        
        # Check if this was B's first appearance (len=1)
        if last_turn_b == 1:
            # B's first appearance - need to also regenerate A's handoff
            # Rollback both A and B
            rollback_history_a = chat_history_a[:-1]  # Remove A's handoff
            rollback_history_b = []  # Clear B's history
        else:
            # B's subsequent responses
            # Check if A added a support comment
            if chat_history_a[-1]["user"] == "[サポート]":
                # A made a support comment, rollback both
                rollback_history_a = chat_history_a[:-1]
                rollback_history_b = chat_history_b[:-1]
            else:
                # Only B responded
                rollback_history_a = chat_history_a
                rollback_history_b = chat_history_b[:-1]
    else:
        # Only Robot A has been responding (B hasn't appeared yet)
        if last_turn_a <= 1:
            # Only opening message
            return (
                chat_history_a,
                format_chat_display(chat_history_a),
                chat_history_b,
                format_chat_display(chat_history_b),
                "[WARNING] 再生成する内容がありません",
                "入力待機中...",
                ""
            )
        
        last_user_input = chat_history_a[-1]["user"]
        rollback_history_a = chat_history_a[:-1]
        rollback_history_b = []
    
    # Re-process the turn with the same user input
    try:
        (
            new_history_a,
            new_history_b,
            emotion_info,
            emotion_flow,
            status_msg
        ) = system.process_turn(
            user_input=last_user_input,
            chat_history_a=rollback_history_a,
            chat_history_b=rollback_history_b,
            use_rag=use_rag
        )
        
        return (
            new_history_a,
            format_chat_display(new_history_a),
            new_history_b,
            format_chat_display(new_history_b),
            f"{status_msg} [再生成完了]",
            emotion_flow,
            emotion_info
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return (
            chat_history_a,
            format_chat_display(chat_history_a),
            chat_history_b,
            format_chat_display(chat_history_b),
            f"[ERROR] 再生成エラー: {str(e)}",
            "入力待機中...",
            ""
        )


# Custom CSS for academic style
custom_css = """
/* グローバルスタイル */
.gradio-container {
    font-family: 'Yu Gothic', 'Meiryo', 'Hiragino Kaku Gothic Pro', sans-serif;
    background-color: #f8f9fa;
}

/* チャットボックススタイル */
.chatbot-container {
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid #e0e0e0;
    background: white;
}

/* Chatbot文字颜色修复 */
#chatbot_a, #chatbot_b {
    color: #1f2937 !important;
}

#chatbot_a .message, 
#chatbot_b .message,
#chatbot_a .bot,
#chatbot_b .bot,
#chatbot_a .user,
#chatbot_b .user,
#chatbot_a p,
#chatbot_b p,
#chatbot_a [class*="message"],
#chatbot_b [class*="message"] {
    color: #1f2937 !important;
}

#chatbot_a .bot p,
#chatbot_b .bot p {
    color: #1f2937 !important;
}

#chatbot_a .user p,
#chatbot_b .user p {
    color: #1f2937 !important;
}

/* 入力エリア */
.input-area {
    background: #ffffff;
    border-radius: 8px;
    padding: 16px;
    margin-top: 16px;
    border: 1px solid #d0d0d0;
}

/* ボタンスタイル */
.send-button {
    background: #4a5568;
    border: none;
    border-radius: 6px;
    color: white;
    font-weight: 500;
}

/* 感情カード */
.emotion-card {
    background: white;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
    border: 1px solid #e8e8e8;
}

/* ===== Loading Animation - 自然的加载动画 ===== */

#chatbot_a .pending,
#chatbot_b .pending,
#chatbot_a .generating,
#chatbot_b .generating,
#chatbot_a [class*="pending"],
#chatbot_b [class*="pending"] {
    opacity: 0.7;
}

/* 隐藏默认的三点加载动画 */
#chatbot_a .dot-flashing,
#chatbot_b .dot-flashing {
    display: none !important;
}

/* 添加自然的加载提示 */
#chatbot_a .bot.pending::after,
#chatbot_b .bot.pending::after,
#chatbot_a [class*="message"][class*="bot"].pending::after,
#chatbot_b [class*="message"][class*="bot"].pending::after {
    content: "考え中...";
    display: inline-block;
    margin-left: 8px;
    color: #6b7280;
    font-style: italic;
    animation: fadeInOut 1.5s ease-in-out infinite;
}

@keyframes fadeInOut {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 1; }
}

/* 头像大小 - 简单设置 */
#chatbot_a img[class*="avatar"],
#chatbot_b img[class*="avatar"] {
    width: 120px;
    height: 120px;
}

"""

# Get initial opening message before creating Gradio interface
INITIAL_OPENING_MESSAGE = system.robot_a.get_opening_message()

# Create Gradio interface
with gr.Blocks(title="Robot A+B - 対話システム") as demo:
    
    # Apply custom CSS
    gr.HTML(f"<style>{custom_css}</style>")
    
    # Header
    gr.Markdown(
        """
        # Robot A + B 対話システム
        
        <div style='text-align: center; color: #555; margin-bottom: 20px; background: white; padding: 16px; border-radius: 8px; border: 1px solid #e0e0e0;'>
            <p style='font-size: 16px; font-weight: 500;'>感情的サポート × 認知的ガイダンス</p>
            <p style='font-size: 13px; color: #777;'>音声入力はASRでテキスト化し、テキスト感情のみで応答を制御</p>
        </div>
        """
    )
    
    with gr.Row():
        with gr.Column():
            scenario_info = gr.Markdown(
                """
                **現在の対話設定：統一モード（学業・進路・経済・人間関係）**
                """
            )
    
    # State variables - 初始化：user 为空，只有开场白
    chat_history_a_state = gr.State([{"user": "", "assistant": INITIAL_OPENING_MESSAGE}])
    chat_history_b_state = gr.State([])
    
    # Main layout
    with gr.Row():
        # Left column: Emotion
        with gr.Column(scale=1):
            gr.Markdown("### [FLOW] 感情認識プロセス")
            emotion_flow = gr.Textbox(
                value="入力待機中...",
                label="",
                show_label=False,
                lines=6,
                interactive=False
            )
            
            gr.Markdown("### [ANALYSIS] 感情分析結果")
            emotion_display = gr.Markdown(
                value="入力待機中...",
                elem_classes="emotion-card"
            )
        
        # Middle column: Robot A
        with gr.Column(scale=2):
            gr.Markdown("### Robot A - 感情的サポート")
            chatbot_a = gr.Chatbot(
                label="",
                height=500,
                show_label=False,
                elem_id="chatbot_a",
                value=[{"role": "assistant", "content": INITIAL_OPENING_MESSAGE}],
                avatar_images=(None, r"C:\Users\wangs\Downloads\robotA_gradio_final.png")
            )
        
        # Right column: Robot B  
        with gr.Column(scale=2):
            gr.Markdown("### Robot B - 認知的ガイダンス")
            chatbot_b = gr.Chatbot(
                label="",
                height=500,
                show_label=False,
                elem_id="chatbot_b",
                value=[],
                avatar_images=(None, r"C:\Users\wangs\Downloads\robotB_gradio_final.png")
            )
    
    # Input area - text only
    gr.Markdown("---")
    with gr.Row():
        with gr.Column(scale=8):
            text_input = gr.Textbox(
                label="",
                placeholder="メッセージを入力してください...",
                lines=2,
                show_label=False
            )
        with gr.Column(scale=1):
            send_button = gr.Button(
                "送信",
                variant="primary",
                size="lg"
            )
        with gr.Column(scale=1):
            regenerate_button = gr.Button(
                "🔄 再生成",
                variant="secondary",
                size="lg"
            )
    
    # Status bar
    with gr.Row():
        status_display = gr.Textbox(
            label="ステータス",
            value="[READY] システム準備完了",
            interactive=False,
            show_label=False
        )
    
    # Settings (collapsible)
    with gr.Accordion("システム設定", open=False):
        use_rag_checkbox = gr.Checkbox(label="RAG知識検索を有効化", value=True)
        reset_button = gr.Button("新規対話を開始", variant="stop")
        
        gr.Markdown("""
        **使用方法**
        - **テキスト入力**: メッセージを入力して「送信」ボタンをクリック
        - **再生成**: 最後の回答が気に入らない場合、🔄再生成ボタンで別の回答を生成
        - **RAG知識検索**: 4つの主要トピック（学業・進路・経済・人間関係）から関連知識を自動検索
        - **感情判定**: テキスト内容から8種類の感情（joy, sadness, anticipation, surprise, anger, fear, disgust, trust）を分析
        """)
    
    # Event handlers
    send_button.click(
        fn=submit_message,
        inputs=[
            text_input,
            chat_history_a_state,
            chat_history_b_state,
            use_rag_checkbox
        ],
        outputs=[
            chat_history_a_state,
            chatbot_a,
            chat_history_b_state,
            chatbot_b,
            text_input,
            status_display,
            emotion_flow,
            emotion_display
        ]
    )
    
    # 注意：移除了 text_input.submit 绑定，这样按Enter键不会提交
    # 用户必须点击"发送"按钮，没有快捷键要求
    
    regenerate_button.click(
        fn=regenerate_last_response,
        inputs=[
            chat_history_a_state,
            chat_history_b_state,
            use_rag_checkbox
        ],
        outputs=[
            chat_history_a_state,
            chatbot_a,
            chat_history_b_state,
            chatbot_b,
            status_display,
            emotion_flow,
            emotion_display
        ]
    )
    
    reset_button.click(
        fn=reset_session,
        inputs=[],
        outputs=[
            chat_history_a_state,
            chatbot_a,
            chat_history_b_state,
            chatbot_b,
            text_input,
            status_display,
            emotion_flow,
            emotion_display
        ]
    )
    
if __name__ == "__main__":
    print("\n" + "="*60)
    print("起動中: 二重ロボット対話システム（テキストのみ）...")
    print("="*60 + "\n")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,  # 创建公共链接，可从任何设备访问
        css=custom_css
    )
