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
async def create_session(language: str = "ja"):
    """创建会话"""
    import uuid
    session_id = str(uuid.uuid4())
    return {
        "session_id": session_id,
        "language": language,
        "created_at": "2026-03-24T00:00:00Z"
    }


# Vercel需要导出handler
def handler(request: Request):
    """Vercel Serverless Function Handler"""
    return app(request)
