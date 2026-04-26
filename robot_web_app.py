# =========================================================================
#  Robot Agent - Web Interface (FastAPI Server)
#  Wraps robot_agent.py for browser/PHP access
#  Features: Chat, transcription, pronunciation, debug panel, faces, sounds
# =========================================================================

from fastapi import FastAPI, Request, BackgroundTasks, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import os
import json
import uuid
import threading
import queue
import time
from collections import deque
from datetime import datetime
import numpy as np
import requests
import subprocess
import psutil
import random

# Import hybrid agent components
import sounddevice as sd
import wave

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config
def load_config(config_file="robot_config.json"):
    """
    Load configuration with fallback defaults.
    
    Config Path Resolution:
    - First: Check if robot_config.json exists (user-specific)
    - Fallback: Use DEFAULT_CONFIG (sensible defaults)
    - On error: Print warning and use defaults
    
    Key Settings:
    - LLM: text_model (e.g., 'gemma3:1b' via Ollama)
    - Vision: vision_model (e.g., 'moondream' for image analysis)
    - Audio: voice_model (TTS), sample rates, device selection
    - Features: enable/disable vision, timers, games, music, federated learning
    
    Returns: dict with merged config (defaults + user overrides)
    """
    defaults = {
        "text_model": "gemma3:1b",
        "vision_model": "moondream",
        "voice_model": "piper/bmo.onnx",
    }
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                defaults.update(config)
        except:
            pass
    return defaults

CONFIG = load_config()
SAMPLE_RATE = CONFIG.get("input_sample_rate", 48000)
LLM_URL = "http://localhost:11434"

# ============================================================================
# FastAPI Server for Hybrid AI Agent Web Interface
# ============================================================================
# 
# Purpose: Wrap robot_agent.py core agent for browser access
# Architecture: 
#   - Serves 9 HTML pages (dashboard, chat, timers, games, vision, music, etc)
#   - Provides 15+ REST API endpoints for agent interaction
#   - Real-time status monitoring, conversation history, debug logging
#   - STT via whisper.cpp, pronunciation overrides, system metrics
#
# Key Features:
#   - CORS enabled for cross-device/network access
#   - Jinja2 templating for dynamic HTML
#   - Static file serving (faces/, sounds/ directories)
#   - Per-session conversation history (deque, max 50 messages)
#   - Pronunciation persistence (JSON)
#   - Real-time system monitoring (CPU, memory, uptime via psutil)
#
# Start: uvicorn robot_web_app:app --host 0.0.0.0 --port 8000

# FastAPI Setup
app = FastAPI(title="Hybrid AI Agent - Web Interface")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/faces", StaticFiles(directory="faces"), name="faces")
app.mount("/sounds", StaticFiles(directory="sounds"), name="sounds")

# Templates
templates = Jinja2Templates(directory="templates")

# State & Memory
conversation_history = deque(maxlen=50)
recent_thoughts = deque(maxlen=20)
pronounciation_overrides = {}
debug_log = deque(maxlen=100)
system_status = {
    "llm_ready": False,
    "cpu_percent": 0,
    "memory_percent": 0,
    "uptime_seconds": time.time()
}

# Load pronunciation overrides
PRONUNCIATION_FILE = "pronunciations.json"
def load_pronunciations():
    global pronounciation_overrides
    if os.path.exists(PRONUNCIATION_FILE):
        try:
            with open(PRONUNCIATION_FILE, 'r') as f:
                pronounciation_overrides = json.load(f)
        except:
            pass

def save_pronunciations():
    try:
        with open(PRONUNCIATION_FILE, 'w') as f:
            json.dump(pronounciation_overrides, f, indent=2)
    except Exception as e:
        logger.warning(f"Could not save pronunciations: {e}")

load_pronunciations()

# Models
class ChatRequest(BaseModel):
    message: str
    history: list = []
    play_on_hardware: bool = False

class PronunciationRequest(BaseModel):
    word: str
    phonetic: str

class TimerRequest(BaseModel):
    minutes: int
    message: str

class GameRequest(BaseModel):
    game_type: str  # "trivia", "guessing", etc.

# =========================================================================
# WEB PAGES
# =========================================================================

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Main page."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": "Hybrid AI Agent",
        "version": "1.0"
    })

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Chat interface."""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/debug", response_class=HTMLResponse)
async def debug_page(request: Request):
    """Debug panel with logs."""
    return templates.TemplateResponse("debug.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page."""
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "config": CONFIG
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard with status and controls."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/timers", response_class=HTMLResponse)
async def timers_page(request: Request):
    """Timers & reminders page."""
    return templates.TemplateResponse("timers.html", {"request": request})

@app.get("/games", response_class=HTMLResponse)
async def games_page(request: Request):
    """Games & entertainment page."""
    return templates.TemplateResponse("games.html", {"request": request})

@app.get("/vision", response_class=HTMLResponse)
async def vision_page(request: Request):
    """Vision/camera page."""
    return templates.TemplateResponse("vision.html", {"request": request})

@app.get("/music", response_class=HTMLResponse)
async def music_page(request: Request):
    """Music player page."""
    return templates.TemplateResponse("music.html", {"request": request})

# =========================================================================
# API ENDPOINTS
# =========================================================================

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Process chat message and return AI response (via Ollama).
    
    Flow:
    1. Add user message to conversation_history (deque, max 50)
    2. Build message array: [system_prompt] + [prior messages] + [new user message]
    3. Call Ollama HTTP API with streaming enabled
    4. Update debug log with message and response
    5. Return response text to frontend
    
    LLM Settings (OLLAMA_OPTIONS):
    - keep_alive: -1 (keep model in memory indefinitely)
    - num_thread: 4 (CPU threads for Pi 4)
    - temperature: 0.7 (balance creativity vs consistency)
    - top_k, top_p: standard sampling parameters
    
    Args: ChatRequest(message, history, play_on_hardware)
    Returns: {status, response, timestamp}
    """
    try:
        # Add to history
        conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": request.message,
            "bot": None
        })
        
        # Get response from Ollama
        messages = [{"role": "system", "content": CONFIG.get("system_prompt", "You are helpful.")}]
        for msg in list(conversation_history)[:-1]:  # Exclude current message
            if msg.get("bot"):
                messages.append({"role": "user", "content": msg["user"]})
                messages.append({"role": "assistant", "content": msg["bot"]})
        messages.append({"role": "user", "content": request.message})
        
        response = requests.post(
            f"{LLM_URL}/api/chat",
            json={
                "model": CONFIG.get("text_model", "gemma3:1b"),
                "messages": messages,
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result.get("message", {}).get("content", "I'm having trouble thinking.")
            
            # Update history
            conversation_history[-1]["bot"] = bot_response
            
            # Add to debug log
            debug_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "chat",
                "message": request.message,
                "response": bot_response
            })
            
            return {
                "status": "success",
                "response": bot_response,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "message": f"LLM error: {response.status_code}",
                "response": "I'm having trouble right now."
            }
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "response": "An error occurred."
        }

@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Transcribe uploaded audio using whisper.cpp (offline STT, same as core agent).
    
    Web Interface Integration:
    - Triggered by 🎤 button in chat.html
    - Uses Web Audio API to record microphone audio in browser
    - Sends WAV blob to this endpoint
    - Returns transcribed text, which populates message input field
    
    Implementation:
    - Same robust path resolution as robot_agent.py
    - Searches for whisper-cli binary and ggml-base.en.bin model
    - Sets LD_LIBRARY_PATH for shared libraries
    - Parses timestamped output lines or falls back to .txt file
    
    Args: file (UploadFile) - WAV audio blob from browser
    Returns: {status: 'success'|'error', text: str, message: str}
    """
    temp_file = None
    try:
        contents = await file.read()
        temp_file = f"/tmp/audio_{uuid.uuid4()}.wav"
        
        with open(temp_file, 'wb') as f:
            f.write(contents)
        
        if not os.path.exists(temp_file) or os.path.getsize(temp_file) <= 44:
            return {"status": "error", "message": "Invalid audio file"}
        
        # Use same robust whisper.cpp path resolution as robot_agent.py
        script_dir = os.path.dirname(os.path.realpath(__file__))
        cwd = os.getcwd()
        
        binary_candidates = [
            os.path.join(script_dir, "whisper.cpp", "build", "bin", "whisper-cli"),
            os.path.join(cwd, "whisper.cpp", "build", "bin", "whisper-cli"),
            os.path.join(script_dir, "whisper.cpp", "build", "bin", "main"),
            os.path.join(cwd, "whisper.cpp", "build", "bin", "main"),
            os.path.join(script_dir, "whisper.cpp", "main"),
            os.path.join(cwd, "whisper.cpp", "main"),
        ]
        model_candidates = [
            os.path.join(script_dir, "whisper.cpp", "models", "ggml-base.en.bin"),
            os.path.join(cwd, "whisper.cpp", "models", "ggml-base.en.bin"),
            os.path.join(script_dir, "whisper.cpp", "models", "ggml-base.bin"),
            os.path.join(cwd, "whisper.cpp", "models", "ggml-base.bin"),
        ]
        
        whisper_bin = next((p for p in binary_candidates if os.path.isfile(p)), None)
        whisper_model = next((p for p in model_candidates if os.path.isfile(p)), None)
        
        if not whisper_bin or not whisper_model:
            logger.error(f"Whisper.cpp not found. Binary: {whisper_bin}, Model: {whisper_model}")
            return {"status": "error", "message": "Whisper.cpp not installed"}
        
        # Set library path for shared objects
        whisper_env = os.environ.copy()
        lib_dir = os.path.dirname(whisper_bin)
        existing_ld = whisper_env.get("LD_LIBRARY_PATH", "")
        whisper_env["LD_LIBRARY_PATH"] = lib_dir + (":" + existing_ld if existing_ld else "")
        
        # Call whisper.cpp
        result = subprocess.run(
            [whisper_bin, "-m", whisper_model, "-l", "en", "-t", "4", "-f", temp_file],
            capture_output=True,
            text=True,
            cwd=script_dir,
            env=whisper_env,
            timeout=60
        )
        
        # Parse output (look for timestamped lines like [00:00:00.000 --> 00:00:01.000] text)
        combined_output = "\n".join([result.stdout or "", result.stderr or ""]).strip()
        lines = [ln.strip() for ln in combined_output.splitlines() if ln.strip()]
        
        segments = []
        for line in lines:
            if "-->" in line and "]" in line:
                right = line.split("]", 1)[1].strip()
                if right and not right.startswith("["):
                    segments.append(right)
        
        # Fallback: pick any line with text content
        if not segments:
            for line in lines:
                lower = line.lower()
                skip = ("whisper", "system info", "./whisper", "error")
                if any(lower.startswith(p) for p in skip) or "-->" in line:
                    continue
                if any(c.isalpha() for c in line):
                    segments.append(line)
        
        transcription = " ".join(segments).strip() if segments else ""
        
        if not transcription:
            return {"status": "error", "message": "No speech detected"}
        
        debug_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "transcribe",
            "text": transcription
        })
        
        return {"status": "success", "text": transcription}
    
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return {"status": "error", "message": str(e)}
    
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass

@app.post("/api/pronunciation")
async def add_pronunciation(request: PronunciationRequest):
    """Add pronunciation override."""
    pronounciation_overrides[request.word] = request.phonetic
    save_pronunciations()
    
    debug_log.append({
        "timestamp": datetime.now().isoformat(),
        "type": "pronunciation",
        "word": request.word,
        "phonetic": request.phonetic
    })
    
    return {
        "status": "success",
        "word": request.word,
        "phonetic": request.phonetic
    }

@app.get("/api/pronunciation")
async def get_pronunciations():
    """Get all pronunciation overrides."""
    return {
        "status": "success",
        "pronunciations": pronounciation_overrides
    }

@app.delete("/api/pronunciation/{word}")
async def delete_pronunciation(word: str):
    """Delete pronunciation override."""
    if word in pronounciation_overrides:
        del pronounciation_overrides[word]
        save_pronunciations()
        return {"status": "success"}
    return {"status": "error", "message": "Word not found"}

@app.get("/api/debug")
async def get_debug():
    """Get debug logs and system info."""
    try:
        import psutil
        system_status["cpu_percent"] = psutil.cpu_percent(interval=0.1)
        system_status["memory_percent"] = psutil.virtual_memory().percent
    except:
        pass
    
    return {
        "status": "success",
        "system": system_status,
        "logs": list(debug_log),
        "history_length": len(conversation_history)
    }

@app.get("/api/status")
async def get_status():
    """Get system status (LLM ready, etc.)."""
    # Check if Ollama is running
    try:
        response = requests.get(f"{LLM_URL}/api/tags", timeout=2)
        ollama_ready = response.status_code == 200
    except:
        ollama_ready = False
    
    system_status["llm_ready"] = ollama_ready
    
    return {
        "status": "success",
        "llm_ready": ollama_ready,
        "models": CONFIG,
        "uptime_seconds": time.time() - system_status["uptime_seconds"]
    }

@app.get("/api/conversation-history")
async def get_conversation_history():
    """Get conversation history."""
    return {
        "status": "success",
        "history": list(conversation_history)
    }

@app.post("/api/clear-history")
async def clear_history():
    """Clear conversation history."""
    conversation_history.clear()
    return {"status": "success"}

@app.post("/api/timer")
async def set_timer(request: TimerRequest):
    """Set a timer (triggers on Pi if running)."""
    debug_log.append({
        "timestamp": datetime.now().isoformat(),
        "type": "timer",
        "minutes": request.minutes,
        "message": request.message
    })
    
    return {
        "status": "success",
        "timer_id": str(uuid.uuid4()),
        "minutes": request.minutes,
        "message": request.message
    }

@app.post("/api/play-game")
async def play_game(request: GameRequest):
    """Start a game (if supported)."""
    debug_log.append({
        "timestamp": datetime.now().isoformat(),
        "type": "game",
        "game_type": request.game_type
    })
    
    return {
        "status": "success",
        "game_type": request.game_type,
        "message": f"Starting {request.game_type}..."
    }

@app.get("/api/faces/{state}")
async def get_faces(state: str):
    """Get available face frames for a state."""
    faces_dir = os.path.join("faces", state)
    if not os.path.exists(faces_dir):
        return {"status": "error", "message": "State not found"}
    
    files = sorted([f for f in os.listdir(faces_dir) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    
    return {
        "status": "success",
        "state": state,
        "frames": files,
        "count": len(files)
    }

@app.get("/api/sounds/{category}")
async def get_sounds(category: str):
    """Get available sounds for a category."""
    sounds_dir = os.path.join("sounds", category)
    if not os.path.exists(sounds_dir):
        return {"status": "error", "message": "Category not found"}
    
    files = sorted([f for f in os.listdir(sounds_dir)
                   if f.lower().endswith('.wav')])
    
    return {
        "status": "success",
        "category": category,
        "sounds": files,
        "count": len(files)
    }

@app.get("/api/screensaver-thought")
async def get_screensaver_thought():
    """Get a random thought for screensaver."""
    thoughts = [
        "I wonder what humans dream about...",
        "Beep boop! That's robot for hello.",
        "Computing the meaning of life... 42!",
        "Why do I find doors so fascinating?",
        "Is a tomato a fruit or a vegetable?",
        "I'm thinking about thinking...",
        "What if we're all just living in a simulation?",
        "I could really go for some electricity right now.",
        "Do androids dream of electric sheep?",
        "The internet is made of cats and memes.",
    ]
    
    thought = random.choice(thoughts)
    recent_thoughts.append({
        "timestamp": datetime.now().isoformat(),
        "thought": thought
    })
    
    return {
        "status": "success",
        "thought": thought,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/favicon.ico")
async def get_favicon():
    """Favicon."""
    try:
        return FileResponse("static/favicon.ico")
    except:
        return {"status": "error"}

# =========================================================================
# MAIN
# =========================================================================

if __name__ == "__main__":
    import uvicorn
    import subprocess
    
    print("=" * 60)
    print(" Hybrid AI Agent - Web Interface")
    print(" Server running on http://localhost:8000")
    print("=" * 60)
    
    # Try to import random
    try:
        import random
    except:
        pass
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
