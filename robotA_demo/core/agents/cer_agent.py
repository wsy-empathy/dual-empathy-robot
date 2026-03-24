"""
New CER Agent - Cognitive Empathy Robot
重构的认知共情机器人（支持多语言）
"""

from typing import Dict, List, Optional
from core.i18n import Language, get_cer_system_prompt


class CERAgent:
    """认知共情机器人（多语言支持）"""
    
    def __init__(self):
        """初始化CER"""
        print("[CER] Cognitive Empathy Robot initialized (multi-language support)")
    
    def format_prompt(
        self,
        language: Language,
        stage: str,
        user_input: str,
        rag_content: str,
        dialogue_history: List[Dict],
        aer_summary: Optional[str] = None
    ) -> List[Dict]:
        """
        格式化CER的prompt（多语言）
        
        Args:
            language: 语言 ('ja' or 'zh')
            stage: 当前阶段 (cer_1, cer_2, cer_3)
            user_input: 用户输入
            rag_content: RAG检索内容
            dialogue_history: 对话历史
            aer_summary: AER阶段的情感总结（可选）
        
        Returns:
            格式化的messages列表
        """
        # 获取系统提示词
        system_message = get_cer_system_prompt(language)
        
        # 阶段说明（多语言）
        stage_instructions = {
            'ja': {
                "cer_1": "\n\n【当前阶段】CER Round 1 - PT (Perspective-Taking)\n簡潔複述ユーザー状況、2句以下、新分析なし",
                "cer_2": "\n\n【当前阶段】CER Round 2 - Mz (Mentalizing)\n心智化モデリング：「状況→信念/懸念→意図/目標→コミット→現在の困難」、2句以下、反証可能形式",
                "cer_3": "\n\n【当前阶段】CER Round 3 - Advice\n唯一の具体的建議（✖️代替案禁止）：\n1句理解圧縮 + 1句単一アクション提案（含まれる：何を+どうやって+完了判定）"
            },
            'zh': {
                "cer_1": "\n\n【当前阶段】CER Round 1 - PT (Perspective-Taking)\n简洁复述用户状况，≤2句，不加新分析",
                "cer_2": "\n\n【当前阶段】CER Round 2 - Mz (Mentalizing)\n心智化建模：「情境→信念/担忧→意图/目标→承诺→当前困难」，≤2句，可证伪形式",
                "cer_3": "\n\n【当前阶段】CER Round 3 - Advice\n唯一的具体建议（✖️禁止备选）：\n1句压缩理解 + 1句单一行动建议（含：做什么+怎么做+完成判据）"
            }
        }
        
        system_message += stage_instructions.get(language, stage_instructions['ja']).get(stage, "")
        
        # 添加RAG内容
        if rag_content:
            rag_label = "【参考内容】" if language == 'ja' else "【参考内容】"
            system_message += f"\n\n{rag_label}\n{rag_content}"
        
        # 添加AER总结（如果是CER首次出现）
        if aer_summary and stage == "cer_1":
            aer_label = "【AER情感总结】" if language == 'zh' else "【AER情感総結】"
            system_message += f"\n\n{aer_label}\n{aer_summary}"
        
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
