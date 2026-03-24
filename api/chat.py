"""
Vercel Serverless Function - Chat API
简化版对话接口，适配Vercel部署限制
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import json

app = FastAPI()

# 环境变量
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
BACKEND_API = os.getenv("BACKEND_API", "")  # 如果有独立后端服务


class ChatRequest(BaseModel):
    """聊天请求"""
    session_id: str
    message: str
    language: str = "ja"
    stage: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    session_id: str
    agent: str  # AER or CER
    response: str
    emotion: Optional[str] = None
    stage: str


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "Dual Empathy Robot API",
        "version": "2.0.0",
        "deployment": "vercel"
    }


@app.get("/api/topics")
async def get_topics(lang: str = "ja"):
    """获取话题列表"""
    topics = {
        "ja": [
            {"key": "academic", "name": "学業の問題"},
            {"key": "financial", "name": "経済的な問題"},
            {"key": "relationship", "name": "人間関係"},
            {"key": "future", "name": "将来設計"}
        ],
        "zh": [
            {"key": "academic", "name": "学业问题"},
            {"key": "financial", "name": "经济问题"},
            {"key": "relationship", "name": "人际关系"},
            {"key": "future", "name": "未来规划"}
        ]
    }
    return {"topics": topics.get(lang, topics["ja"])}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    聊天接口
    
    注意：由于Vercel限制，这里使用简化版本
    完整功能需要连接到独立后端服务或使用客户端直连
    """
    
    # 如果有独立后端API
    if BACKEND_API:
        # 转发到完整后端
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_API}/chat",
                json=request.dict()
            )
            return response.json()
    
    # 否则返回模拟响应（用于测试）
    return {
        "session_id": request.session_id,
        "agent": "AER",
        "response": "こんにちは！Vercel経由で接続されました。完全な機能を使用するには、バックエンドサービスを設定してください。" if request.language == "ja" else "你好！已通过Vercel连接。要使用完整功能，请配置后端服务。",
        "emotion": None,
        "stage": "aer_1",
        "note": "This is a simplified response. Configure BACKEND_API environment variable for full functionality."
    }


@app.post("/api/session/create")
async def create_session(request: Request):
    """创建会话"""
    import uuid
    body = await request.json()
    language = body.get("user_id", "ja")
    session_id = str(uuid.uuid4())
    
    # 返回欢迎消息
    welcome_messages = {
        "ja": "最近、気がかりなことがあれば聞かせてもらえますか？授業のこと、進路のこと、お金のこと、人との関係のことなど、どれからでも大丈夫です。",
        "zh": "最近有什么让你担心的事情吗？无论是课程、未来规划、经济问题还是人际关系，都可以和我聊聊。"
    }
    
    return {
        "session_id": session_id,
        "message": welcome_messages.get(language, welcome_messages["ja"]),
        "language": language,
        "created_at": "2026-03-24T00:00:00Z"
    }


@app.post("/api/session/select-topic")
async def select_topic(request: Request):
    """选择主题"""
    body = await request.json()
    topic_key = body.get("topic_key", "")
    
    subtopics_map = {
        "academic": [
            ["exam_anxiety", "試験不安", "考试焦虑"],
            ["study_pace", "学習ペース", "学习节奏"],
            ["follow_content", "授業理解", "课程理解"]
        ],
        "financial": [
            ["cost_burden", "経済的負担", "经济负担"],
            ["work_study_balance", "バイトと学業", "打工与学业"],
            ["financial_anxiety", "お金の不安", "经济焦虑"]
        ],
        "relationship": [
            ["making_friends", "友達作り", "交朋友"],
            ["no_confidant", "相談相手がいない", "没有倾诉对象"],
            ["interaction_issues", "コミュニケーション", "沟通问题"]
        ],
        "future": [
            ["unclear_goals", "目標が不明確", "目标不明确"],
            ["career_choice", "進路選択", "职业选择"],
            ["preparation", "就活準備", "就业准备"]
        ]
    }
    
    return {
        "message": "具体的にはどの点が気になりますか？" if body.get("language", "ja") == "ja" else "具体来说，哪方面让你困扰？",
        "subtopics": subtopics_map.get(topic_key, [])
    }


@app.post("/api/session/select-subtopic")
async def select_subtopic(request: Request):
    """选择子主题"""
    body = await request.json()
    language = body.get("language", "ja")
    
    start_messages = {
        "ja": "それでは、あなたの気持ちを聞かせてください。",
        "zh": "那么，请告诉我你的感受吧。"
    }
    
    return {
        "message": start_messages.get(language, start_messages["ja"])
    }


# Vercel需要导出handler
def handler(request: Request):
    """Vercel Serverless Function Handler"""
    return app(request)
