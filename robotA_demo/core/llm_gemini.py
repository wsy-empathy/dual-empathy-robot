"""
LLM Module - Gemini API integration using OpenAI-compatible API (hiapi)
"""

import time
from typing import Dict, List, Optional
from openai import OpenAI

from core.config import GEMINI_API_KEY, GEMINI_MODEL
try:
    from core.config import GEMINI_BASE_URL
except ImportError:
    GEMINI_BASE_URL = "https://hiapi.online/v1"


class GeminiLLM:
    """Gemini LLM wrapper using OpenAI-compatible API"""
    
    def __init__(
        self,
        api_key: str = GEMINI_API_KEY,
        model_name: str = GEMINI_MODEL,
        base_url: str = GEMINI_BASE_URL
    ):
        """
        Initialize Gemini LLM
        
        Args:
            api_key: Gemini API key
            model_name: Model name
            base_url: API base URL (OpenAI-compatible endpoint)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url
        
        # Create OpenAI client with custom base URL
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        print(f"Gemini LLM initialized: {model_name} via {base_url}")
    
    def generate(
        self,
        prompt=None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        messages: Optional[List[Dict]] = None
    ):
        """
        Generate response from Gemini
        
        Args:
            prompt: User prompt (string) OR list of messages
            system_prompt: System prompt (optional, used if prompt is string)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            messages: Optional list of message dictionaries (takes precedence)
            
        Returns:
            Response text string (or dict with metadata if original format needed)
        """
        start_time = time.time()
        
        # Prepare messages
        if messages is not None:
            # Use provided messages directly
            final_messages = messages
        elif isinstance(prompt, list):
            # prompt is already a list of messages
            final_messages = prompt
        else:
            # Build messages from prompt and system_prompt
            final_messages = []
            if system_prompt:
                final_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            if prompt:
                final_messages.append({
                    "role": "user",
                    "content": prompt
                })
        
        if not final_messages:
            raise ValueError("No messages provided for generation")
        
        try:
            # Generate using OpenAI-compatible API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=final_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Extract text
            response_text = response.choices[0].message.content
            
            # Handle None or empty response
            if response_text is None or response_text.strip() == "":
                print(f"Warning: Empty response from LLM. Response object: {response}")
                response_text = ""  # Ensure it's a string
            
            # Return string directly for new usage
            return response_text.strip() if response_text else ""
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"Error in LLM generation: {e}")
            raise  # Re-raise for caller to handle


# ============================================================
# 以下为旧系统代码（已废弃，保留以备参考）
# Legacy code from old system (deprecated, kept for reference)
# ============================================================

# def load_system_prompt(
#     emo_top: str,
#     emo_conf: float,
#     prompt_path: str = "old_system_prompt_path"
# ) -> str:
#     """旧系统：从文件加载系统提示词"""
#     with open(prompt_path, "r", encoding="utf-8") as f:
#         template = f.read()
#     prompt = template.replace("{emo_top}", emo_top)
#     prompt = prompt.replace("{emo_conf:.2f}", f"{emo_conf:.2f}")
#     return prompt


# def build_prompt(
#     user_text: str,
#     emo_top: str,
#     emo_conf: float,
#     rag_results: List[Dict],
#     target_emotion: Optional[str] = None
# ) -> str:
#     """旧系统：构建用户提示词"""
#     prompt_parts = []
#     prompt_parts.append(f"【ユーザーの感情状態】")
#     prompt_parts.append(f"主要感情: {emo_top} (信頼度: {emo_conf:.2f})")
#     if rag_results:
#         prompt_parts.append(f"\n【関連する過去の対話や知識】")
#         for i, result in enumerate(rag_results[:3]):
#             prompt_parts.append(f"{i+1}. {result['text']}")
#     prompt_parts.append(f"\n【ユーザーの発言】")
#     prompt_parts.append(user_text)
#     if target_emotion:
#         prompt_parts.append(f"\n【重要な制約】")
#         prompt_parts.append(
#             f"あなたの応答は、ユーザーの感情「{target_emotion}」を鏡映し、"
#             f"同じ感情的基調で表現してください。"
#         )
#     prompt_parts.append(f"\n【あなたの応答】")
#     prompt_parts.append("ユーザーに共感的に応答してください：")
#     return "\n".join(prompt_parts)


# def generate_reply(
#     user_text: str,
#     emo_top: str,
#     emo_conf: float,
#     rag_results: List[Dict],
#     target_emotion: Optional[str] = None,
#     llm: Optional[GeminiLLM] = None
# ) -> Dict:
#     """旧系统：生成回复"""
#     if llm is None:
#         llm = GeminiLLM()
#     system_prompt = load_system_prompt(emo_top, emo_conf)
#     user_prompt = build_prompt(user_text, emo_top, emo_conf, rag_results, target_emotion)
#     result = llm.generate(user_prompt, system_prompt=system_prompt)
#     return result


if __name__ == "__main__":
    # 简单测试 - 新系统使用AER/CER agents
    print("Gemini LLM初始化测试")
    llm = GeminiLLM()
    print(f"✓ 模型: {llm.model_name}")
    print(f"✓ Base URL: {llm.base_url}")
    print("提示：请使用 test_autonomous_dialogue.py 进行完整测试")

