"""
自主对话测试脚本 - Autonomous Dialogue Testing
测试所有功能：完整对话流程、情绪检测、RAG检索、LLM生成、对话自然性

使用方法：
python test_autonomous_dialogue.py --lang ja  # 测试日语
python test_autonomous_dialogue.py --lang zh  # 测试中文
python test_autonomous_dialogue.py --lang both  # 测试两种语言
"""

import asyncio
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from core.session_manager import SessionState
from core.agents.aer_agent import AERAgent
from core.agents.cer_agent import CERAgent
from core.llm_gemini import GeminiLLM
from core.emo_wrime_luke_onnx import get_onnx_wrime_luke_recognizer
from core.rag_v2_retriever import RAGV2Retriever
from core.topics import get_topic_list, get_subtopic_list
from core.i18n import get_message


class AutonomousDialogueTester:
    """自主对话测试器"""
    
    def __init__(self, language: str = 'ja'):
        """初始化测试器"""
        self.language = language
        self.aer_agent = AERAgent()
        self.cer_agent = CERAgent()
        self.llm = GeminiLLM()
        self.emotion_recognizer = get_onnx_wrime_luke_recognizer()
        self.rag_retriever = RAGV2Retriever()
        
        # 测试用户输入（模拟真实学生的担忧）- 完整9轮对话
        self.test_dialogues = {
            'ja': {
                'exam_anxiety': [
                    # AER Round 1 (aer_1)
                    "来週、数学の期末試験があって、とても不安です。勉強してもなかなか点数が上がらなくて...",
                    # AER Round 2 (aer_2)
                    "はい、特に応用問題が全然できなくて、焦っています。",
                    # AER Round 3 (aer_3)
                    "前回の中間試験では、基礎問題は解けたんですが、応用で大きく失点しました。時間も足りなかったです。",
                    # AER Transition (aer_transition)
                    "そうですね。でも具体的にどうすればいいのか分からなくて。",
                    # CER Round 1 (cer_1)
                    "はい、そうなんです。完璧にやろうとしすぎているかもしれません。",
                    # CER Round 2 (cer_2)
                    "確かに、どこまでやれば十分か分からなくて、どんどん不安になります。",
                    # CER Round 3 (cer_3)
                    "なるほど、最低ラインを設定するんですね。それなら試してみます。",
                    # AER Closing 1 (aer_closing_1)
                    "はい、具体的な方法があると分かって、少し安心しました。",
                    # AER Closing 2 (aer_closing_2)
                    "ありがとうございます。少しずつやってみます。"
                ],
                'cost_burden': [
                    # AER Round 1
                    "最近、学費とアルバイトのバランスで悩んでいます。",
                    # AER Round 2
                    "はい、学費を自分で稼がないといけないので、週4日バイトしているんですが、勉強時間が足りなくて...",
                    # AER Round 3
                    "親からの援助は少しだけで、基本的に自分で学費を払っています。疲れて授業に集中できないこともあります。",
                    # AER Transition
                    "そうですね。何か方法があればいいんですけど。",
                    # CER Round 1
                    "はい、このままだと学業が疎かになってしまいそうで心配です。",
                    # CER Round 2
                    "確かに、時間をうまく使えれば両立できるかもしれません。",
                    # CER Round 3
                    "奨学金や学内アルバイトは考えたことありませんでした。調べてみます。",
                    # AER Closing 1
                    "はい、新しい選択肢が見えて少し希望が持てました。",
                    # AER Closing 2
                    "ありがとうございます。相談してよかったです。"
                ]
            },
            'zh': {
                'exam_anxiety': [
                    # AER Round 1
                    "下周有数学期末考试，我特别焦虑。学了很多但成绩还是上不去...",
                    # AER Round 2
                    "对，特别是应用题完全不会做，非常着急。",
                    # AER Round 3
                    "上次期中考试基础题还能做，但应用题丢了很多分，时间也不够。",
                    # AER Transition
                    "是啊，但我不知道具体该怎么做。",
                    # CER Round 1
                    "对，我确实想做到完美，可能给自己压力太大了。",
                    # CER Round 2
                    "没错，我总觉得不知道学到什么程度才够，越学越焦虑。",
                    # CER Round 3
                    "设定最低标准啊，这个主意不错。我试试看。",
                    # AER Closing 1
                    "嗯，有了具体方法，心里踏实多了。",
                    # AER Closing 2
                    "谢谢你，我会一步步来的。"
                ],
                'cost_burden': [
                    # AER Round 1
                    "最近在学费和打工之间很纠结。",
                    # AER Round 2
                    "对，学费要自己赚，所以每周打工四天，但学习时间不够...",
                    # AER Round 3
                    "父母只能给一点点支持，学费基本要自己付。有时候太累了，上课都没法集中精神。",
                    # AER Transition
                    "是啊，要是有什么办法就好了。",
                    # CER Round 1
                    "对，我担心这样下去学业会受影响。",
                    # CER Round 2
                    "是的，如果时间安排好的话，可能两边都能兼顾。",
                    # CER Round 3
                    "奖学金和校内兼职我还真没想过，回头查查。",
                    # AER Closing 1
                    "嗯，看到新的可能性，感觉轻松了一些。",
                    # AER Closing 2
                    "谢谢你，和你聊完感觉好多了。"
                ]
            }
        }
        
        print(f"[Tester] 初始化完成 - 语言: {language}")
    
    def analyze_emotion(self, text: str) -> Dict:
        """分析文本情绪"""
        try:
            result = self.emotion_recognizer.predict(text)
            emotion_label = result['emo_top']
            emotion_score = result['emo_conf']
            return {
                'label': emotion_label,
                'score': emotion_score,
                'details': result
            }
        except Exception as e:
            print(f"[情绪检测错误] {e}")
            return {'label': 'neutral', 'score': 0.5, 'details': {}}
    
    def retrieve_rag_content(self, topic_key: str, subtopic_key: str, stage: str) -> str:
        """检索RAG内容"""
        try:
            content = self.rag_retriever.retrieve(topic_key, subtopic_key, stage)
            return content if content else ""
        except Exception as e:
            print(f"[RAG检索错误] {e}")
            return ""
    
    def generate_response(self, messages: List[Dict]) -> str:
        """生成LLM响应"""
        try:
            response = self.llm.generate(messages=messages)
            return response
        except Exception as e:
            print(f"[LLM生成错误] {e}")
            return f"[生成失败: {str(e)}]"
    
    async def run_dialogue(self, topic_key: str, subtopic_key: str, user_inputs: List[str]) -> Dict:
        """运行完整对话流程"""
        
        session = SessionState(f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}", self.language)
        session.set_topic(topic_key, f"{topic_key}")
        session.set_subtopic(subtopic_key, f"{subtopic_key}")
        
        # 对话记录
        dialogue_log = {
            'session_id': session.session_id,
            'language': self.language,
            'topic': topic_key,
            'subtopic': subtopic_key,
            'turns': [],
            'quality_analysis': {
                'naturalness_score': 0,
                'repetition_issues': [],
                'emotion_tracking': [],
                'rag_usage': [],
                'stage_completion': []
            }
        }
        
        # 阶段顺序
        stage_order = ["aer_1", "aer_2", "aer_3", "aer_transition", "cer_1", "cer_2", "cer_3", "aer_closing_1", "aer_closing_2"]
        
        print(f"\n{'='*60}")
        print(f"开始测试对话 - {topic_key}/{subtopic_key}")
        print(f"语言: {self.language}")
        print(f"{'='*60}\n")
        
        for idx, user_input in enumerate(user_inputs):
            if idx >= len(stage_order):
                break
            
            stage = stage_order[idx]
            session.current_stage = stage
            agent_type = "AER" if stage.startswith("aer") else "CER"
            
            print(f"\n{'─'*50}")
            print(f"【阶段】 {stage} ({agent_type})")
            print(f"【用户】 {user_input}")
            
            # 1. 情绪检测
            emotion_result = self.analyze_emotion(user_input)
            print(f"【情绪】 {emotion_result['label']} (置信度: {emotion_result['score']:.2f})")
            session.set_emotion(emotion_result['label'], emotion_result['score'])
            dialogue_log['quality_analysis']['emotion_tracking'].append({
                'stage': stage,
                'emotion': emotion_result['label'],
                'score': emotion_result['score']
            })
            
            # 2. RAG检索（内部使用，不显示技术细节）
            rag_content = self.retrieve_rag_content(topic_key, subtopic_key, stage)
            dialogue_log['quality_analysis']['rag_usage'].append({
                'stage': stage,
                'content_length': len(rag_content) if rag_content else 0,
                'has_content': bool(rag_content)
            })
            
            # 3. 构建prompt
            if agent_type == "AER":
                messages = self.aer_agent.format_prompt(
                    language=self.language,
                    stage=stage,
                    user_input=user_input,
                    emotion=emotion_result['label'],
                    rag_content=rag_content,
                    dialogue_history=session.dialogue_history
                )
            else:
                messages = self.cer_agent.format_prompt(
                    language=self.language,
                    stage=stage,
                    user_input=user_input,
                    rag_content=rag_content,
                    dialogue_history=session.dialogue_history
                )
            
            # 4. LLM生成
            response = self.generate_response(messages)
            print(f"【{agent_type}】 {response}")
            
            # 5. 检查对话质量
            quality_issues = self.check_response_quality(user_input, response, agent_type)
            if quality_issues:
                print(f"⚠️  【质量问题】 {', '.join(quality_issues)}")
                dialogue_log['quality_analysis']['repetition_issues'].extend([
                    {'stage': stage, 'issue': issue} for issue in quality_issues
                ])
            else:
                print(f"✓ 【质量】 通过")
            
            # 6. 记录对话
            session.add_turn("user", user_input, stage)
            session.add_turn(agent_type, response, stage)
            
            dialogue_log['turns'].append({
                'stage': stage,
                'user': user_input,
                'agent': agent_type,
                'response': response,
                'emotion': emotion_result,
                'rag_used': len(rag_content) > 0,
                'quality_issues': quality_issues
            })
            
            dialogue_log['quality_analysis']['stage_completion'].append({
                'stage': stage,
                'completed': True
            })
            
            # 短暂延迟，避免API限流
            await asyncio.sleep(2)
        
        # 计算自然性得分
        dialogue_log['quality_analysis']['naturalness_score'] = self.calculate_naturalness_score(dialogue_log)
        
        print(f"\n{'='*60}")
        print(f"对话测试完成")
        print(f"自然性得分: {dialogue_log['quality_analysis']['naturalness_score']:.1f}/100")
        print(f"质量问题数: {len(dialogue_log['quality_analysis']['repetition_issues'])}")
        print(f"{'='*60}\n")
        
        return dialogue_log
    
    def check_response_quality(self, user_input: str, response: str, agent_type: str) -> List[str]:
        """检查响应质量，发现重复、不自然等问题"""
        issues = []
        
        # 检查是否大量重复用户输入
        user_words = set(user_input.split())
        response_words = response.split()
        
        # 计算重复度（只检查长词，忽略常见助词）
        common_words = {'の', 'は', 'が', 'を', 'に', 'で', 'と', 'も', 'から', 'まで', '的', '了', '着', '在', '是', '有', '这', '那'}
        filtered_user_words = set(word for word in user_words if word not in common_words and len(word) > 1)
        
        repeated_count = sum(1 for word in response_words if word in filtered_user_words and len(word) > 1)
        repetition_ratio = repeated_count / len(response_words) if response_words else 0
        
        if repetition_ratio > 0.5:
            issues.append(f"过度重复用户输入({repetition_ratio:.1%})")
        
        # 检查回复长度 - 简洁是好事，不算问题
        # AER应该简洁（15-120字），CER稍长（20-150字）
        if agent_type == "AER":
            if len(response) > 150:
                issues.append("回复过长（AER应简洁）")
        elif agent_type == "CER":
            if len(response) < 15:
                issues.append("回复过短（CER应稍详细）")
            elif len(response) > 200:
                issues.append("回复过长")
        
        # 检查是否有明显的机器生成痕迹
        robot_phrases = [
            "作为一个", "作为AI", "我是机器人", "私はAI", "私はロボット",
            "AI助手", "人工知能", "言語モデル"
        ]
        if any(phrase in response for phrase in robot_phrases):
            issues.append("包含机器人自我指称")
        
        # 检查是否有不必要的重复短语（句子过多）
        sentence_count = response.count("。") + response.count("？") + response.count("！")
        if sentence_count > 6:
            issues.append("句子过多，不够简洁")
        
        return issues
    
    def calculate_naturalness_score(self, dialogue_log: Dict) -> float:
        """计算对话自然性得分（0-100）"""
        score = 100.0
        
        # 扣分项
        score -= len(dialogue_log['quality_analysis']['repetition_issues']) * 5
        
        # 检查阶段完整性
        expected_stages = 9
        completed_stages = len(dialogue_log['quality_analysis']['stage_completion'])
        if completed_stages < expected_stages:
            score -= (expected_stages - completed_stages) * 10
        
        # RAG使用率
        rag_used = sum(1 for r in dialogue_log['quality_analysis']['rag_usage'] if r['has_content'])
        rag_rate = rag_used / len(dialogue_log['quality_analysis']['rag_usage']) if dialogue_log['quality_analysis']['rag_usage'] else 0
        if rag_rate < 0.5:
            score -= 10
        
        return max(0, min(100, score))
    
    async def run_all_tests(self):
        """运行所有测试案例"""
        
        print(f"\n{'#'*60}")
        print(f"# 自主对话测试开始 - 语言: {self.language}")
        print(f"# 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*60}\n")
        
        results = []
        
        test_cases = self.test_dialogues[self.language]
        
        for subtopic_key, user_inputs in test_cases.items():
            # 推断topic_key - 根据实际的RAG文件格式
            # 文件名格式: {topic}_{subtopic}.txt，例如 academic_exam_anxiety.txt
            if subtopic_key in ['exam_anxiety', 'follow_content', 'study_pace']:
                topic_key = 'academic'
            elif subtopic_key in ['cost_burden', 'financial_anxiety', 'work_study_balance']:
                topic_key = 'financial'
            elif subtopic_key in ['career_choice', 'preparation', 'unclear_goals']:
                topic_key = 'future'
            elif subtopic_key in ['interaction_issues', 'making_friends', 'no_confidant']:
                topic_key = 'relationship'
            else:
                topic_key = 'academic'  # 默认
            
            result = await self.run_dialogue(topic_key, subtopic_key, user_inputs)
            results.append(result)
            
            # 保存单个测试结果
            self.save_test_result(result)
            
            # 测试间隔
            await asyncio.sleep(3)
        
        # 生成综合报告
        self.generate_summary_report(results)
        
        return results
    
    def save_test_result(self, result: Dict):
        """保存测试结果"""
        output_dir = Path("logs/test_results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"test_{result['session_id']}_{result['language']}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 测试结果已保存: {filepath}")
    
    def generate_summary_report(self, results: List[Dict]):
        """生成综合测试报告"""
        output_dir = Path("logs/test_results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"summary_report_{self.language}_{timestamp}.md"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# 对话测试综合报告\n\n")
            f.write(f"**语言**: {self.language}\n")
            f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**测试案例数**: {len(results)}\n\n")
            
            f.write(f"## 总体评分\n\n")
            avg_score = sum(r['quality_analysis']['naturalness_score'] for r in results) / len(results)
            f.write(f"- **平均自然性得分**: {avg_score:.1f}/100\n")
            
            total_issues = sum(len(r['quality_analysis']['repetition_issues']) for r in results)
            f.write(f"- **总质量问题数**: {total_issues}\n\n")
            
            f.write(f"## 各案例详情\n\n")
            for idx, result in enumerate(results, 1):
                f.write(f"### 案例 {idx}: {result['topic']}/{result['subtopic']}\n\n")
                f.write(f"- **自然性得分**: {result['quality_analysis']['naturalness_score']:.1f}/100\n")
                f.write(f"- **质量问题数**: {len(result['quality_analysis']['repetition_issues'])}\n")
                f.write(f"- **完成阶段数**: {len(result['quality_analysis']['stage_completion'])}/9\n")
                
                rag_used = sum(1 for r in result['quality_analysis']['rag_usage'] if r['has_content'])
                f.write(f"- **RAG使用率**: {rag_used}/{len(result['quality_analysis']['rag_usage'])}\n")
                
                if result['quality_analysis']['repetition_issues']:
                    f.write(f"\n**发现的问题**:\n")
                    for issue in result['quality_analysis']['repetition_issues']:
                        f.write(f"- {issue['stage']}: {issue['issue']}\n")
                
                f.write(f"\n")
        
        print(f"\n✓ 综合报告已生成: {filepath}")
        print(f"\n平均自然性得分: {avg_score:.1f}/100")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='自主对话测试脚本')
    parser.add_argument('--lang', type=str, default='both', choices=['ja', 'zh', 'both'],
                        help='测试语言: ja(日语), zh(中文), both(两者)')
    
    args = parser.parse_args()
    
    languages = ['ja', 'zh'] if args.lang == 'both' else [args.lang]
    
    for lang in languages:
        tester = AutonomousDialogueTester(language=lang)
        await tester.run_all_tests()
        
        if len(languages) > 1:
            print(f"\n{'='*60}")
            print(f"等待10秒后开始下一个语言的测试...")
            print(f"{'='*60}\n")
            await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
