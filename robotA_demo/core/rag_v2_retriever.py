"""
RAG V2 Retriever - 支持新的topic/subtopic/stage结构
"""

from pathlib import Path
from typing import Dict, Optional


class RAGV2Retriever:
    """RAG V2 检索器 - 基于topic/subtopic/stage的检索"""
    
    def __init__(self, rag_dir: str = "data/rag_v2"):
        """初始化检索器"""
        self.rag_dir = Path(rag_dir)
        self.cache = {}  # 缓存已加载的内容
        print("[RAG V2] Retriever initialized")
    
    def _get_filename(self, topic_key: str, subtopic_key: str) -> str:
        """根据topic和subtopic生成文件名"""
        return f"{topic_key}_{subtopic_key}.txt"
    
    def _load_content(self, topic_key: str, subtopic_key: str) -> Optional[Dict]:
        """加载指定topic/subtopic的内容"""
        cache_key = f"{topic_key}_{subtopic_key}"
        
        # 检查缓存
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 加载文件
        filename = self._get_filename(topic_key, subtopic_key)
        filepath = self.rag_dir / filename
        
        if not filepath.exists():
            print(f"[RAG V2] Warning: Content file not found: {filepath}")
            return None
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 解析内容
            parsed = self._parse_content(content)
            self.cache[cache_key] = parsed
            return parsed
            
        except Exception as e:
            print(f"[RAG V2] Error loading content: {e}")
            return None
    
    def _parse_content(self, content: str) -> Dict:
        """解析RAG内容文件 - 支持多种格式"""
        sections = {"AER": {}, "CER": {}, "KEYWORDS": ""}
        
        lines = content.split("\n")
        current_section = None
        current_key = None
        current_content = []
        
        for line in lines:
            # 检测section标记
            if line.strip() == "=== AER Content ===":
                current_section = "AER"
                continue
            elif line.strip() == "=== CER Content ===":
                current_section = "CER"
                continue
            elif line.strip() == "=== Keywords ===":
                current_section = "KEYWORDS"
                continue
            
            # 检测子项标记 - 支持两种格式
            # 格式1: [key]
            # 格式2: key:
            is_key_line = False
            detected_key = None
            
            if current_section in ["AER", "CER"]:
                # 格式1: [key]
                if line.startswith("[") and "]" in line:
                    is_key_line = True
                    detected_key = line[1:line.index("]")]
                # 格式2: key: （行结尾是冒号，且key包含下划线）
                elif ":" in line and "_" in line and not line.strip().startswith("==="):
                    # 提取冒号前的部分作为key
                    potential_key = line.split(":")[0].strip()
                    # 确保key看起来像是RAG key（包含下划线）
                    if "_" in potential_key and len(potential_key) < 50:
                        is_key_line = True
                        detected_key = potential_key
            
            if is_key_line and detected_key:
                # 保存之前的内容
                if current_key and current_content:
                    sections[current_section][current_key] = "\n".join(current_content).strip()
                
                # 开始新的子项
                current_key = detected_key
                current_content = []
                continue
            
            # 收集内容
            if current_section == "KEYWORDS":
                if line.strip():  # 只添加非空行
                    sections["KEYWORDS"] += line + "\n"
            elif current_key:
                # 跳过空行在内容开始时
                if current_content or line.strip():
                    current_content.append(line)
        
        # 保存最后一个子项
        if current_section in ["AER", "CER"] and current_key and current_content:
            sections[current_section][current_key] = "\n".join(current_content).strip()
        
        # 清理KEYWORDS
        sections["KEYWORDS"] = sections["KEYWORDS"].strip()
        
        return sections
    
    def retrieve(
        self,
        topic_key: str,
        subtopic_key: str,
        stage: str
    ) -> str:
        """
        检索指定阶段的RAG内容
        
        Args:
            topic_key: 大topic key
            subtopic_key: 子topic key
            stage: 当前对话阶段
        
        Returns:
            格式化的RAG内容字符串
        """
        # 加载内容
        content = self._load_content(topic_key, subtopic_key)
        if not content:
            return ""
        
        # 根据stage提取相应内容
        if stage.startswith("aer"):
            # AER阶段 - 修复key匹配问题
            stage_map = {
                "aer_1": "AER_R1_M+N/U+E",
                "aer_2": "AER_R2_M+R+E",
                "aer_3": "AER_R3_M+S+E",
                "aer_transition": "AER_Transition",  # 修正：Transition首字母大写
                "aer_closing_1": "AER_Closing1_M+R",  # 修正：Closing1
                "aer_closing_2": "AER_Closing2_M+S"   # 修正：Closing2
            }
            
            stage_key = stage_map.get(stage)
            if stage_key and stage_key in content["AER"]:
                return content["AER"][stage_key]
        
        elif stage.startswith("cer"):
            # CER阶段 - 修复key匹配问题
            stage_map = {
                "cer_1": "CER_PT",      # 修正：CER_PT，不是CER_R1_PT
                "cer_2": "CER_Mz",      # 修正：CER_Mz，不是CER_R2_Mz
                "cer_3": "CER_Advice"   # 修正：CER_Advice，不是CER_R3_Advice
            }
            
            stage_key = stage_map.get(stage)
            if stage_key and stage_key in content["CER"]:
                return content["CER"][stage_key]
        
        return ""
    
    def get_keywords(self, topic_key: str, subtopic_key: str) -> str:
        """获取关键词列表"""
        content = self._load_content(topic_key, subtopic_key)
        if content:
            return content.get("KEYWORDS", "")
        return ""
