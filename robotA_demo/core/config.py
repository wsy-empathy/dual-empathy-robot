"""
Configuration file for Robot A Empathy Listener
"""

import os
import warnings
from pathlib import Path

# Suppress RTX 5070 sm_120 warning (known incompatibility)
warnings.filterwarnings('ignore', message='.*CUDA capability sm_120.*')

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
RAG_CORPUS_DIR = DATA_DIR / "rag_corpus"

# Create directories if they don't exist
LOGS_DIR.mkdir(exist_ok=True)
RAG_CORPUS_DIR.mkdir(parents=True, exist_ok=True)

# LLM Configuration (OpenAI-compatible API)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "sk-fZi9uid1sghutP0cjDG9y0R25AsS32z6nvNo96rdlpDMfzAB")
GEMINI_MODEL = "gemini-2.5-pro-no"  # No thinking chain output
GEMINI_BASE_URL = "https://hiapi.online/v1"  # OpenAI-compatible endpoint

# LLM 生成参数
LLM_TEMPERATURE = 0.7   
LLM_MAX_TOKENS = 1200   

# Emotion Model Configuration
EMOTION_MODEL_NAME = "Mizuiro-sakura/luke-japanese-large-sentiment-analysis-wrime"
EMOTION_LABELS = ["joy", "sadness", "anticipation", "surprise", "anger", "fear", "disgust", "trust"]

# Audio Configuration
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_FORMAT = "wav"

# ASR Configuration (faster-whisper)
WHISPER_MODEL = "base"  # Can be: tiny, base, small, medium, large-v2, large-v3
WHISPER_DEVICE = "cpu"  # 使用 CPU 模式（绕过 Windows DLL 安全策略）
WHISPER_COMPUTE_TYPE = "int8"  # CPU int8 优化

# Runtime Status - 当前配置：CPU 模式
# ✓ ONNX Runtime: 文本情感识别 + RAG
# ✓ Faster-Whisper (CPU): 语音识别 ASR

# RAG Configuration
RAG_TOP_K = 3
RAG_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Emotion Consistency Gate Configuration
EMOTION_GATE_ENABLED = True
EMOTION_MATCH_REQUIRED = True
EMOTION_COSINE_THRESHOLD = 0.75
MAX_REWRITE_ATTEMPTS = 2

# TTS Configuration
TTS_ENGINE = "edge_tts"  # Cross-platform Edge TTS (Windows/macOS/Linux compatible)
TTS_VOICE = "ja-JP-NanamiNeural"  # Default Japanese voice for Edge TTS

# Emotion-to-Voice Mapping for Robot A (Affective Empathy)
# Robot A uses different Edge TTS voices to mirror user's emotion
# All female voices for consistent empathetic tone
EMOTION_VOICE_MAP = {
    "joy": "ja-JP-AoiNeural",        # 明亮、愉快的音色 (female)
    "sadness": "ja-JP-NanamiNeural",  # 温柔、低沉的音色 (female)
    "anger": "ja-JP-AoiNeural",       # 较强、坚定的音色 (female)
    "fear": "ja-JP-MayuNeural",       # 柔和、关怀的音色 (female)
    "disgust": "ja-JP-ShioriNeural",  # 稳重、冷静的音色 (female)
    "trust": "ja-JP-NanamiNeural",    # 温暖、可靠的音色 (female)
    "surprise": "ja-JP-AoiNeural",    # 活泼、有变化的音色 (female)
    "anticipation": "ja-JP-ShioriNeural"  # 温和、鼓励的音色 (female)
}

# Logging
TURN_LOG_PATH = LOGS_DIR / "turns.jsonl"
