"""
Vercel Serverless API - Main Entry
"""

from http.server import BaseHTTPRequestHandler
import json
import uuid

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理 GET 请求"""
        if self.path.startswith('/api/topics'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # 解析查询参数
            lang = 'ja'
            if '?' in self.path:
                params = dict(x.split('=') for x in self.path.split('?')[1].split('&') if '=' in x)
                lang = params.get('lang', 'ja')
            
            topics_data = {
                "ja": [
                    {"key": "academic", "name": "学業の問題", "ja": "学業の問題", "zh": "学业问题"},
                    {"key": "financial", "name": "経済的な問題", "ja": "経済的な問題", "zh": "经济问题"},
                    {"key": "relationship", "name": "人間関係", "ja": "人間関係", "zh": "人际关系"},
                    {"key": "future", "name": "将来設計", "ja": "将来設計", "zh": "未来规划"}
                ],
                "zh": [
                    {"key": "academic", "name": "学业问题", "ja": "学業の問題", "zh": "学业问题"},
                    {"key": "financial", "name": "经济问题", "ja": "経済的な問題", "zh": "经济问题"},
                    {"key": "relationship", "name": "人际关系", "ja": "人間関係", "zh": "人际关系"},
                    {"key": "future", "name": "未来规划", "ja": "将来設計", "zh": "未来规划"}
                ]
            }
            
            self.wfile.write(json.dumps({"topics": topics_data.get(lang, topics_data["ja"])}).encode())
            return
        
        # 默认响应
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "service": "Dual Empathy Robot API"}).encode())
    
    def do_POST(self):
        """处理 POST 请求"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body)
        except:
            data = {}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # 创建会话
        if self.path == '/api/session/create':
            language = data.get("user_id", "ja")
            session_id = str(uuid.uuid4())
            
            welcome_messages = {
                "ja": "最近、気がかりなことがあれば聞かせてもらえますか？授業のこと、進路のこと、お金のこと、人との関係のことなど、どれからでも大丈夫です。",
                "zh": "最近有什么让你担心的事情吗？无论是课程、未来规划、经济问题还是人际关系，都可以和我聊聊。"
            }
            
            response = {
                "session_id": session_id,
                "message": welcome_messages.get(language, welcome_messages["ja"]),
                "language": language
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # 选择话题
        elif self.path == '/api/session/select-topic':
            topic_key = data.get("topic_key", "")
            language = data.get("language", "ja")
            
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
            
            response = {
                "message": "具体的にはどの点が気になりますか？" if language == "ja" else "具体来说，哪方面让你困扰？",
                "subtopics": subtopics_map.get(topic_key, [])
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # 选择子话题
        elif self.path == '/api/session/select-subtopic':
            language = data.get("language", "ja")
            
            start_messages = {
                "ja": "それでは、あなたの気持ちを聞かせてください。",
                "zh": "那么，请告诉我你的感受吧。"
            }
            
            response = {
                "message": start_messages.get(language, start_messages["ja"])
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # 聊天接口
        elif self.path == '/api/chat':
            session_id = data.get("session_id", "")
            message = data.get("message", "")
            language = data.get("language", "ja")
            
            # 简化响应（演示版本）
            response = {
                "session_id": session_id,
                "agent": "AER",
                "response": "こんにちは！Vercel経由で接続されました。これは簡易版です。完全な機能を使用するには、バックエンドサーバーを起動してください。" if language == "ja" else "你好！已通过Vercel连接。这是简化版本。要使用完整功能，请启动后端服务器。",
                "emotion": None,
                "stage": "aer_1"
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # 默认响应
        self.wfile.write(json.dumps({"status": "ok"}).encode())
    
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
