"""
New AER Agent - Affective Empathy Robot
重构的情感共情机器人（支持多语言）
"""

from typing import Dict, List, Optional
from core.i18n import Language, get_aer_system_prompt, format_agent_prompt


class AERAgent:
    """AER - 情感共情机器人（多语言支持）"""
    
    def __init__(self):
        """初始化AER"""
        print("[AER] Affective Empathy Robot initialized (multi-language support)")
    
    def format_prompt(
        self,
        language: Language,
        stage: str,
        user_input: str,
        emotion: Optional[str],
        rag_content: str,
        dialogue_history: List[Dict]
    ) -> List[Dict]:
        """
        格式化AER的prompt（多语言）
        
        Args:
            language: 语言 ('ja' or 'zh')
            stage: 当前阶段 (aer_1, aer_2, aer_3, aer_transition, aer_closing_1, aer_closing_2)
            user_input: 用户输入
            emotion: 检测到的情绪
            rag_content: RAG检索内容
            dialogue_history: 对话历史
        
        Returns:
            格式化的messages列表
        """
        # 获取系统提示词
        system_message = get_aer_system_prompt(language)
        
        # 阶段说明（多语言）
        stage_instructions = {
            'ja': {
                "aer_1": "\n\n【当前阶段】AER Round 1 - M+N/U+E\n使用：情绪模仿(M) + 命名/理解(N/U) + 感受導向探索(E)",
                "aer_2": "\n\n【当前阶段】AER Round 2 - M+R+E\n使用：情绪模仿(M) + 尊重(R) + 感受導向探索(E)",
                "aer_3": "\n\n【当前阶段】AER Round 3 - M+S+E\n使用：情绪模仿(M) + 支持(S) + 最後の感受導向問題(E)",
                "aer_transition": "\n\n【当前阶段】AER Transition\n簡短情感総結、自然引出CER",
                "aer_closing_1": "\n\n【当前阶段】AER Closing 1 - M+R\n軽量情緒承接 + 尊重。❌不重複分析❌",
                "aer_closing_2": "\n\n【当前阶段】AER Closing 2 - M+S\n簡短鼓励 + 支持性収尾。❌不重複建議❌"
            },
            'zh': {
                "aer_1": "\n\n【当前阶段】AER Round 1 - M+N/U+E\n使用：情绪模仿(M) + 命名/理解(N/U) + 感受导向探索(E)",
                "aer_2": "\n\n【当前阶段】AER Round 2 - M+R+E\n使用：情绪模仿(M) + 尊重(R) + 感受导向探索(E)",
                "aer_3": "\n\n【当前阶段】AER Round 3 - M+S+E\n使用：情绪模仿(M) + 支持(S) + 最后的感受导向问题(E)",
                "aer_transition": "\n\n【当前阶段】AER Transition\n简短情感总结，自然引出CER",
                "aer_closing_1": "\n\n【当前阶段】AER Closing 1 - M+R\n轻量情绪承接 + 尊重。❌不重复分析❌",
                "aer_closing_2": "\n\n【当前阶段】AER Closing 2 - M+S\n简短鼓励 + 支持性收尾。❌不重复建议❌"
            }
        }
        
        system_message += stage_instructions.get(language, stage_instructions['ja']).get(stage, "")
        
        # 添加RAG内容
        if rag_content:
            rag_label = "【参考内容】" if language == 'ja' else "【参考内容】"
            system_message += f"\n\n{rag_label}\n{rag_content}"
        
        # 添加情绪信息
        if emotion:
            emotion_label = "【用户情绪】" if language == 'zh' else "【ユーザー情緒】"
            system_message += f"\n\n{emotion_label}{emotion}"
        
        # 构建messages
        messages = [{"role": "system", "content": system_message}]
        
        # 添加对话历史（只保留最近几轮）
        recent_history = dialogue_history[-6:] if len(dialogue_history) > 6 else dialogue_history
        for turn in recent_history:
            if turn["role"] == "user":
                messages.append({"role": "user", "content": turn["content"]})
            elif turn["role"] in ["AER", "CER"]:
                messages.append({"role": "assistant", "content": turn["content"]})
        
        # 添加当前用户输入
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def get_transition_message(self, language: Language = 'ja') -> str:
        """获取过渡消息（多语言）"""
        messages = {
            'ja': "私には、一緒に状況を整理することが得意なパートナーがいます。一緒に話してみませんか？",
            'zh': "我有一个擅长一起整理情况的伙伴。要不要一起聊聊看？"
        }
        return messages.get(language, messages['ja'])
