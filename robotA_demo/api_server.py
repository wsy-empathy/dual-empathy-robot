"""
FastAPI Backend for Dual Empathy Robot System
双共情机器人系统后端API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import uuid
from datetime import datetime

# 导入核心模块
from core.topics import get_topic_list, get_subtopic_list, get_topic_name, get_subtopic_name
from core.session_manager import SessionManager
from core.agents.aer_agent import AERAgent
from core.agents.cer_agent import CERAgent
from core.llm_gemini import GeminiLLM
from core.emo_wrime_luke_onnx import get_onnx_wrime_luke_recognizer
from core.rag_v2_retriever import RAGV2Retriever
from core.i18n import get_message  # 独立的多语言模块

# 初始化FastAPI
app = FastAPI(
    title="Dual Empathy Robot API",
    description="AER + CER 双共情机器人系统API",
    version="2.0.0"
)

# CORS配置 - 允许Vercel前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 本地开发
        "https://*.vercel.app",   # Vercel部署
        "*"  # 开发阶段允许所有（生产环境建议限制）
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局实例
session_manager = SessionManager()
aer_agent = AERAgent()
cer_agent = CERAgent()
llm = GeminiLLM()
emotion_recognizer = None  # 延迟加载
rag_retriever = None  # 延迟加载


# ========== 数据模型 ==========

class SessionCreate(BaseModel):
    """创建会话请求"""
    user_id: Optional[str] = None


class TopicSelection(BaseModel):
    """选择Topic"""
    session_id: str
    topic_key: str


class SubtopicSelection(BaseModel):
    """选择Subtopic"""
    session_id: str
    subtopic_key: str


class UserMessage(BaseModel):
    """用户消息"""
    session_id: str
    message: str


class ChatResponse(BaseModel):
    """聊天响应"""
    session_id: str
    agent: str  # "system", "AER", "CER"
    message: str
    stage: str
    emotion: Optional[Dict] = None
    is_completed: bool = False


# ========== API路由 ==========

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "Dual Empathy Robot API",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/api/topics")
async def get_topics():
    """获取所有大topic列表"""
    topics = get_topic_list()
    return {
        "topics": [
            {"key": key, "ja": ja, "zh": zh}
            for key, ja, zh in topics
        ]
    }


@app.get("/api/topics/{topic_key}/subtopics")
async def get_subtopics(topic_key: str):
    """获取指定topic下的subtopic列表"""
    subtopics = get_subtopic_list(topic_key)
    if not subtopics:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return {
        "topic_key": topic_key,
        "topic_name": get_topic_name(topic_key, "ja"),
        "subtopics": [
            {"key": key, "ja": ja, "zh": zh}
            for key, ja, zh in subtopics
        ]
    }


@app.post("/api/session/create")
async def create_session(request: SessionCreate):
    """创建新会话（多语言支持）"""
    session_id = str(uuid.uuid4())
    
    # 多语言支持
    lang = request.user_id if request.user_id in ['ja', 'zh'] else 'ja'
    session = session_manager.create_session(session_id, lang)
    
    return {
        "session_id": session_id,
        "created_at": session.start_time.isoformat(),
        "message": get_message(lang, 'session_start')
    }
    session = session_manager.create_session(session_id)
    
    # 多语言支持
    lang = request.user_id if request.user_id in ['ja', 'zh'] else 'ja'
    message = {
        'ja': '最近、気がかりなことがあれば聞かせてもらえますか？まず、下記から一つ選んでください。',
        'zh': '最近有什么让你担心的事情吗？首先，请从下面选择一个。'
    }
    
    return {
        "session_id": session_id,
        "created_at": session.start_time.isoformat(),
        "message": message.get(lang, message['ja'])
    }


@app.post("/api/session/select-topic")
async def select_topic(request: TopicSelection):
    """选择大topic（多语言支持）"""
    session = session_manager.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    lang = session.language
    topic_name = get_topic_name(request.topic_key, lang)
    if not topic_name:
        raise HTTPException(status_code=400, detail="Invalid topic")
    
    session.set_topic(request.topic_key, topic_name)
    session.add_turn("system", f"Topic selected: {topic_name}", "entry")
    
    return {
        "session_id": request.session_id,
        "topic": {"key": request.topic_key, "name": topic_name},
        "message": get_message(lang, 'topic_selected', topic=topic_name),
        "subtopics": get_subtopic_list(request.topic_key)
    }


@app.post("/api/session/select-subtopic")
async def select_subtopic(request: SubtopicSelection):
    """选择子topic（多语言支持）"""
    session = session_manager.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.topic_key:
        raise HTTPException(status_code=400, detail="Please select topic first")
    
    lang = session.language
    subtopic_name = get_subtopic_name(session.topic_key, request.subtopic_key, lang)
    if not subtopic_name:
        raise HTTPException(status_code=400, detail="Invalid subtopic")
    
    session.set_subtopic(request.subtopic_key, subtopic_name)
    session.add_turn("system", f"Subtopic selected: {subtopic_name}", "entry")
    session.advance_stage()  # 进入aer_1
    
    return {
        "session_id": request.session_id,
        "subtopic": {"key": request.subtopic_key, "name": subtopic_name},
        "message": get_message(lang, 'subtopic_selected', topic=session.topic_name, subtopic=subtopic_name)
    }


@app.post("/api/chat")
async def chat(request: UserMessage):
    """处理用户消息"""
    global emotion_recognizer, rag_retriever
    
    session = session_manager.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 确保已选择topic和subtopic
    if not session.topic_key or not session.subtopic_key:
        raise HTTPException(status_code=400, detail="Please complete topic selection first")
    
    # 添加用户消息到历史
    session.add_turn("user", request.message, session.current_stage)
    
    # 第一次用户输入时进行情绪识别
    if session.detected_emotion is None:
        if emotion_recognizer is None:
            emotion_recognizer = get_onnx_wrime_luke_recognizer(use_gpu=False)
        
        emotion_result = emotion_recognizer.predict(request.message)
        session.set_emotion(emotion_result["emo_top"], emotion_result["emo_score"])
    
    # 初始化RAG检索器
    if rag_retriever is None:
        rag_retriever = RAGV2Retriever()
    
    # 获取RAG内容
    rag_content = rag_retriever.retrieve(
        topic_key=session.topic_key,
        subtopic_key=session.subtopic_key,
        stage=session.current_stage
    )
    
    # 根据当前阶段选择Agent
    current_agent = session.get_current_agent()
    
    if current_agent == "AER":
        # AER回应（多语言）
        messages = aer_agent.format_prompt(
            language=session.language,
            stage=session.current_stage,
            user_input=request.message,
            emotion=session.detected_emotion,
            rag_content=rag_content,
            dialogue_history=session.dialogue_history
        )
        response = llm.generate(messages, max_tokens=1000)
        
    elif current_agent == "CER":
        # CER回应（多语言）
        messages = cer_agent.format_prompt(
            language=session.language,
            stage=session.current_stage,
            user_input=request.message,
            rag_content=rag_content,
            dialogue_history=session.dialogue_history
        )
        response = llm.generate(messages, max_tokens=1000)
    
    else:
        response = "System message"
    
    # 添加机器人回应到历史
    session.add_turn(current_agent, response, session.current_stage)
    
    # 进入下一阶段
    session.advance_stage()
    
    # 检查是否完成
    is_completed = session.is_completed()
    if is_completed:
        session.save_to_file()
    
    return ChatResponse(
        session_id=request.session_id,
        agent=current_agent,
        message=response,
        stage=session.current_stage,
        emotion={"label": session.detected_emotion, "score": session.emotion_score} if session.detected_emotion else None,
        is_completed=is_completed
    )


@app.get("/api/session/{session_id}/status")
async def get_session_status(session_id: str):
    """获取会话状态"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.to_dict()


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    session = session_manager.get_session(session_id)
    if session:
        session.save_to_file()
        session_manager.remove_session(session_id)
    
    return {"message": "Session deleted", "session_id": session_id}


# ========== 启动配置 ==========

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Starting Dual Empathy Robot API Server")
    print("="*60)
    print("Backend running on: http://0.0.0.0:8000")
    print("API Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 开发模式启用热重载
    )
