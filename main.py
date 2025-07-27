from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import json
import uuid
from datetime import datetime

from agents import banking_agent
from models import ChatMessage

# FastAPI app
app = FastAPI(
    title="AI Banking Conversation System",
    description="Advanced conversational AI for banking with multi-turn understanding",
    version="5.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: str):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(message)
            except:
                self.disconnect(session_id)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {
        "message": "AI Banking Conversation System",
        "version": "5.0.0",
        "features": [
            "Multi-turn conversation understanding",
            "Context switching between banking tasks",
            "Gradual information gathering",
            "Ambiguity handling with clarifying questions",
            "Real-time database integration"
        ],
        "demo_users": [
            {"user_id": "user_demo1", "name": "John Smith"},
            {"user_id": "user_demo2", "name": "Sarah Johnson"}
        ]
    }

@app.post("/api/v1/chat")
async def chat(message: ChatMessage, user_id: str = "user_demo1"):
    """Main chat endpoint - simplified without authentication"""
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    response = await banking_agent.process_message(user_id, message.message, session_id)
    
    return {
        **response,
        "user_id": user_id,
        "session_id": session_id
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: str = "user_demo1"):
    """WebSocket for real-time conversation"""
    session_id = f"ws_{uuid.uuid4().hex[:8]}"
    await manager.connect(websocket, session_id)
    
    try:
        # Send welcome message
        welcome_msg = {
            "type": "system",
            "message": """🏦 Welcome to your AI Banking Assistant!

I can help you with sophisticated banking conversations:

🔄 **Multi-turn Conversations** - I remember context across messages
🎯 **Context Switching** - Switch from loans to cards seamlessly  
❓ **Smart Questions** - I'll ask for clarification when needed
💾 **Database Integration** - Real banking data and operations

**Try these examples:**
• "Block my card"
• "Apply for a $15,000 loan for home improvement"
• "What's my balance?"
• "I want a new credit card"

What can I help you with today?""",
            "session_id": session_id,
            "user_id": user_id
        }
        await manager.send_message(session_id, json.dumps(welcome_msg))
        
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if user_message.strip():
                response = await banking_agent.process_message(user_id, user_message, session_id)
                
                response_data = {
                    "type": "assistant",
                    "message": response["response"],
                    "intent": response.get("intent"),
                    "workflow_active": response.get("workflow_active"),
                    "completed": response.get("completed"),
                    "context_switched": response.get("context_switched"),
                    "session_id": session_id,
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                }
                
                await manager.send_message(session_id, json.dumps(response_data))
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)

if __name__ == "__main__":
    import uvicorn
    print("🏦 Starting AI Banking Conversation System...")
    print("📊 Demo data populated with 2 users, accounts, cards, and transactions")
    print("🔗 WebSocket: ws://localhost:8000/ws")
    print("📡 API: POST /api/v1/chat")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
