"""
Session Manager - 会话状态管理
管理整个对话流程的状态和阶段转换
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path

from core.topics import DIALOGUE_STAGES


class SessionState:
    """会话状态类"""
    
    def __init__(self, session_id: str, language: str = 'ja'):
        self.session_id = session_id
        self.start_time = datetime.now()
        self.language = language  # 'ja' or 'zh'
        
        # Topic 信息
        self.topic_key: Optional[str] = None
        self.topic_name: Optional[str] = None
        self.subtopic_key: Optional[str] = None
        self.subtopic_name: Optional[str] = None
        
        # 阶段信息
        self.current_stage: str = "entry"
        self.stage_index: int = 0
        
        # 对话历史
        self.dialogue_history: List[Dict] = []
        
        # 情绪信息
        self.detected_emotion: Optional[str] = None
        self.emotion_score: float = 0.0
        
        # 实验数据
        self.experiment_data = {
            "session_id": session_id,
            "start_time": self.start_time.isoformat(),
            "topic": None,
            "subtopic": None,
            "emotion": None,
            "turns": [],
            "completion_status": "ongoing"
        }
    
    def set_topic(self, topic_key: str, topic_name: str):
        """设置选定的大topic"""
        self.topic_key = topic_key
        self.topic_name = topic_name
        self.experiment_data["topic"] = {
            "key": topic_key,
            "name": topic_name
        }
    
    def set_subtopic(self, subtopic_key: str, subtopic_name: str):
        """设置选定的子topic"""
        self.subtopic_key = subtopic_key
        self.subtopic_name = subtopic_name
        self.experiment_data["subtopic"] = {
            "key": subtopic_key,
            "name": subtopic_name
        }
    
    def set_emotion(self, emotion: str, score: float):
        """设置检测到的情绪"""
        self.detected_emotion = emotion
        self.emotion_score = score
        self.experiment_data["emotion"] = {
            "label": emotion,
            "score": score
        }
    
    def add_turn(self, role: str, content: str, stage: str, metadata: Optional[Dict] = None):
        """添加对话轮次"""
        turn = {
            "role": role,
            "content": content,
            "stage": stage,
            "timestamp": datetime.now().isoformat()
        }
        if metadata:
            turn["metadata"] = metadata
        
        self.dialogue_history.append(turn)
        self.experiment_data["turns"].append(turn)
    
    def advance_stage(self) -> str:
        """进入下一阶段"""
        # 阶段顺序
        stage_order = [
            "entry",
            "aer_1",
            "aer_2", 
            "aer_3",
            "aer_transition",
            "cer_1",
            "cer_2",
            "cer_3",
            "aer_closing_1",
            "aer_closing_2"
        ]
        
        current_idx = stage_order.index(self.current_stage)
        if current_idx < len(stage_order) - 1:
            self.stage_index = current_idx + 1
            self.current_stage = stage_order[self.stage_index]
        
        return self.current_stage
    
    def get_current_agent(self) -> str:
        """获取当前应该回应的Agent"""
        if self.current_stage in ["entry"]:
            return "system"
        elif self.current_stage.startswith("aer"):
            return "AER"
        elif self.current_stage.startswith("cer"):
            return "CER"
        return "system"
    
    def is_completed(self) -> bool:
        """判断会话是否完成"""
        return self.current_stage == "aer_closing_2"
    
    def save_to_file(self, output_dir: str = "logs/experiments"):
        """保存实验数据到文件"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"session_{self.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_path / filename
        
        # 添加完成时间
        self.experiment_data["end_time"] = datetime.now().isoformat()
        self.experiment_data["completion_status"] = "completed" if self.is_completed() else "incomplete"
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.experiment_data, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "session_id": self.session_id,
            "topic": self.topic_key,
            "subtopic": self.subtopic_key,
            "current_stage": self.current_stage,
            "detected_emotion": self.detected_emotion,
            "dialogue_history": self.dialogue_history
        }


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}
    
    def create_session(self, session_id: str, language: str = 'ja') -> SessionState:
        """创建新会话"""
        session = SessionState(session_id, language)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def remove_session(self, session_id: str):
        """移除会话"""
        if session_id in self.sessions:
            # 保存实验数据
            session = self.sessions[session_id]
            session.save_to_file()
            del self.sessions[session_id]
