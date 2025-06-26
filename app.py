from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
from datetime import datetime
from agent import MultiAgentSystem, AgentState
import logging

# Set up logging
logger = logging.getLogger(__name__)

app = FastAPI(title="Post-Discharge Medical AI Assistant")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize the multi-agent system
agent_system = MultiAgentSystem()

# Store active sessions (in production, use Redis or database)
active_sessions = {}

class ChatMessage(BaseModel):
    message: str
    session_id: str

@app.get("/", response_class=HTMLResponse)
async def home():
    """Main chat interface - serve HTML from static folder"""
    return FileResponse("static/index.html")

@app.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    """Handle chat messages"""
    try:
        session_id = chat_message.session_id
        message = chat_message.message
        
        logger.info(f"Chat request from session {session_id}: {message}")
        
        # Get or create session state
        if session_id not in active_sessions:
            active_sessions[session_id] = AgentState()
            logger.info(f"Created new session: {session_id}")
        
        state = active_sessions[session_id]
        
        # Process message through agent system
        result = agent_system.chat(message, state)
        
        # Update session state
        active_sessions[session_id] = result
        
        response_data = {
            "response": result.agent_response,
            "patient_name": result.patient_name,
            "has_discharge_report": bool(result.discharge_report),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Response sent to session {session_id}")
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return JSONResponse(
            content={"error": "Sorry, I encountered an error. Please try again."},
            status_code=500
        )

@app.get("/logs/{session_id}")
async def get_session_logs(session_id: str):
    """Get interaction logs for a session"""
    if session_id in active_sessions:
        state = active_sessions[session_id]
        return JSONResponse(content={
            "logs": agent_system.get_interaction_log(state),
            "conversation_history": state.conversation_history
        })
    return JSONResponse(content={"logs": [], "conversation_history": []})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
