"""
Logger Module - Turn-level logging to JSONL
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from core.config import TURN_LOG_PATH


class TurnLogger:
    """Logger for turn-level interactions"""
    
    def __init__(self, log_path: Path = TURN_LOG_PATH):
        """
        Initialize turn logger
        
        Args:
            log_path: Path to JSONL log file
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Turn logger initialized: {log_path}")
    
    def log_turn(self, turn_data: Dict):
        """
        Log a single turn to JSONL file
        
        Args:
            turn_data: Dictionary containing turn information
        """
        # Add timestamp
        turn_data["timestamp"] = datetime.now().isoformat()
        
        # Write to file
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(turn_data, ensure_ascii=False) + "\n")
    
    def create_turn_record(
        self,
        route: str,
        user_text: str,
        reply_text: str,
        # Step 3: Emotion
        emo_user_top: str,
        emo_user_conf: float,
        emo_user_dist: list,
        # Step 6: Reply emotion (from gate)
        emo_reply_top: str,
        emo_reply_conf: float,
        emo_reply_dist: list,
        # Gate
        emo_match: bool,
        match_score: float,
        rewrite_attempts: int,
        # RAG
        rag_results: list,
        # Timing
        step_times: Dict[str, float],
        total_time: float,
        # Optional: Audio paths (Route A only)
        input_audio_path: Optional[str] = None,
        tts_audio_path: Optional[str] = None,
        # Optional: ASR metadata (Route A only)
        asr_metadata: Optional[dict] = None,
        # Optional: LLM metadata
        llm_metadata: Optional[dict] = None,
    ) -> Dict:
        """
        Create a turn record
        
        Args:
            route: Route type ("voice" or "text")
            user_text: User input text
            reply_text: System reply text
            emo_user_top: User's top emotion
            emo_user_conf: User's emotion confidence
            emo_user_dist: User's emotion distribution
            emo_reply_top: Reply's top emotion
            emo_reply_conf: Reply's emotion confidence
            emo_reply_dist: Reply's emotion distribution
            emo_match: Whether emotions match
            match_score: Emotion match score
            rewrite_attempts: Number of rewrite attempts
            rag_results: RAG retrieval results
            step_times: Dictionary of step timing
            total_time: Total processing time
            input_audio_path: Input audio path (Route A)
            tts_audio_path: TTS output audio path (Route A)
            asr_metadata: ASR metadata (Route A)
            llm_metadata: LLM metadata
            
        Returns:
            Turn record dictionary
        """
        record = {
            "route": route,
            "user_text": user_text,
            "reply_text": reply_text,
            "emo_user_top": emo_user_top,
            "emo_user_conf": emo_user_conf,
            "emo_user_dist": emo_user_dist,
            "emo_reply_top": emo_reply_top,
            "emo_reply_conf": emo_reply_conf,
            "emo_reply_dist": emo_reply_dist,
            "emo_match": emo_match,
            "match_score": match_score,
            "rewrite_attempts": rewrite_attempts,
            "rag_top_k": len(rag_results),
            "rag_results": [
                {
                    "text": r["text"][:100] + "..." if len(r["text"]) > 100 else r["text"],
                    "source": r["source"],
                    "score": r["score"]
                }
                for r in rag_results
            ],
            "step_times": step_times,
            "total_time": total_time,
        }
        
        # Add route-specific fields
        if route == "voice":
            record["input_audio_path"] = input_audio_path
            record["tts_audio_path"] = tts_audio_path
            if asr_metadata:
                record["asr_metadata"] = asr_metadata
        else:
            record["input_audio_path"] = None
            record["tts_audio_path"] = None
        
        # Add LLM metadata
        if llm_metadata:
            record["llm_metadata"] = llm_metadata
        
        return record


# Global logger instance
_turn_logger = None


def get_turn_logger() -> TurnLogger:
    """Get or create global turn logger instance"""
    global _turn_logger
    if _turn_logger is None:
        _turn_logger = TurnLogger()
    return _turn_logger


def log_turn(turn_data: Dict):
    """
    Convenience function to log a turn
    
    Args:
        turn_data: Turn data dictionary
    """
    logger = get_turn_logger()
    logger.log_turn(turn_data)


if __name__ == "__main__":
    # Test
    logger = TurnLogger()
    
    test_record = logger.create_turn_record(
        route="text",
        user_text="今日は嬉しいことがありました。",
        reply_text="それは良かったですね。嬉しい気持ちが伝わってきます。",
        emo_user_top="joy",
        emo_user_conf=0.85,
        emo_user_dist=[0.85, 0.05, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01],
        emo_reply_top="joy",
        emo_reply_conf=0.80,
        emo_reply_dist=[0.80, 0.06, 0.04, 0.03, 0.02, 0.02, 0.02, 0.01],
        emo_match=True,
        match_score=0.92,
        rewrite_attempts=0,
        rag_results=[],
        step_times={"emo": 0.5, "rag": 0.2, "llm": 1.5, "gate": 0.3},
        total_time=2.5
    )
    
    logger.log_turn(test_record)
    print(f"Test record logged to {logger.log_path}")
    print(json.dumps(test_record, indent=2, ensure_ascii=False))
