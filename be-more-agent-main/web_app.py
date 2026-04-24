import datetime
import json
import os
import random
import re
import shutil
import subprocess
import threading
import time
import uuid
import wave
from collections import deque

import numpy as np
import ollama
import scipy.signal
import sounddevice as sd
from fastapi import FastAPI, File, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openwakeword.model import Model
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
PRONUNCIATION_FILE = os.path.join(BASE_DIR, "pronunciations.json")
MUSIC_DIR = os.path.join(BASE_DIR, "sounds", "music")
BMO_IMAGE_FILE = os.path.join(BASE_DIR, "current_image.jpg")
WAKE_WORD_MODEL = os.path.join(BASE_DIR, "wakeword.onnx")
WAKE_WORD_THRESHOLD = 0.5

WHISPER_BIN = os.path.join(BASE_DIR, "whisper.cpp", "build", "bin", "whisper-cli")
WHISPER_MODEL = os.path.join(BASE_DIR, "whisper.cpp", "models", "ggml-base.en.bin")
PIPER_BIN = os.path.join(BASE_DIR, "piper", "piper")

DEFAULT_CONFIG = {
    "text_model": "gemma3:1b",
    "vision_model": "moondream",
    "voice_model": "piper/en_GB-semaine-medium.onnx",
}


def load_config():
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except Exception:
            pass
    return config


CURRENT_CONFIG = load_config()
TEXT_MODEL = CURRENT_CONFIG["text_model"]
VISION_MODEL = CURRENT_CONFIG["vision_model"]
VOICE_MODEL = os.path.join(BASE_DIR, CURRENT_CONFIG["voice_model"])


class ChatRequest(BaseModel):
    message: str
    history: list = []
    session_id: str | None = None
    play_on_pi_audio: bool = False


class PronunciationRequest(BaseModel):
    word: str
    phonetic: str


class DebugStore:
    def __init__(self):
        self.logs = deque(maxlen=200)
        self.history = deque(maxlen=200)
        self.lock = threading.Lock()

    def log(self, event: str):
        line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {event}"
        with self.lock:
            self.logs.append(line)

    def remember(self, role: str, text: str):
        with self.lock:
            self.history.append({"role": role, "text": text, "ts": time.time()})

    def snapshot(self):
        with self.lock:
            return {"logs": list(self.logs), "history": list(self.history)}


debug_store = DebugStore()


class GameState:
    def __init__(self):
        self.mode = None
        self.score = 0
        self.round = 0
        self.current_answer = None
        self.number_to_guess = None


TRIVIA_BANK = [
    {"q": "What planet is known as the Red Planet?", "a": "mars"},
    {"q": "How many days are in a leap year?", "a": "366"},
    {"q": "What gas do plants absorb from the atmosphere?", "a": "carbon dioxide"},
    {"q": "Which ocean is the largest?", "a": "pacific"},
]


games = {}
timers = []
timers_lock = threading.Lock()


def load_pronunciations():
    if os.path.exists(PRONUNCIATION_FILE):
        try:
            with open(PRONUNCIATION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    default_map = {"bmo": "beemo", "ollama": "oh-lah-ma"}
    save_pronunciations(default_map)
    return default_map


def save_pronunciations(mapping):
    with open(PRONUNCIATION_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)


def apply_pronunciations(text: str) -> str:
    mapping = load_pronunciations()
    out = text
    for word, replacement in mapping.items():
        out = re.sub(rf"\\b{re.escape(word)}\\b", replacement, out, flags=re.IGNORECASE)
    return out


def play_wav_on_pi(file_path: str):
    try:
        with wave.open(file_path, "rb") as wf:
            file_sr = wf.getframerate()
            data = wf.readframes(wf.getnframes())
            audio = np.frombuffer(data, dtype=np.int16)

        native_rate = int(sd.query_devices(kind="output")["default_samplerate"])
        playback_rate = file_sr
        try:
            sd.check_output_settings(device=None, samplerate=file_sr)
        except Exception:
            playback_rate = native_rate
            samples = int(len(audio) * (native_rate / file_sr))
            audio = scipy.signal.resample(audio, samples).astype(np.int16)

        sd.play(audio, playback_rate)
        sd.wait()
    except Exception as e:
        debug_store.log(f"Pi audio playback failed: {e}")


def synthesize_to_wav(text: str, output_file: str) -> bool:
    clean = re.sub(r"[^\\w\\s,.!?:-]", "", apply_pronunciations(text)).strip()
    if not clean:
        return False

    try:
        cmd = [PIPER_BIN, "--model", VOICE_MODEL, "--output_file", output_file]
        result = subprocess.run(cmd, input=(clean + "\n"), capture_output=True, text=True)
        if result.returncode == 0 and os.path.exists(output_file):
            return True
    except Exception:
        pass

    try:
        raw_cmd = [PIPER_BIN, "--model", VOICE_MODEL, "--output-raw"]
        proc = subprocess.Popen(raw_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        proc.stdin.write(clean.encode("utf-8") + b"\n")
        proc.stdin.close()
        raw = proc.stdout.read()
        proc.wait(timeout=30)
        if raw:
            with wave.open(output_file, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(22050)
                wf.writeframes(raw)
            return True
    except Exception as e:
        debug_store.log(f"TTS generation failed: {e}")

    return False


def transcribe_audio(file_path: str) -> str:
    if not (os.path.exists(WHISPER_BIN) and os.path.exists(WHISPER_MODEL)):
        return ""
    try:
        result = subprocess.run(
            [WHISPER_BIN, "-m", WHISPER_MODEL, "-l", "en", "-t", "4", "-f", file_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if not lines:
            return ""
        last = lines[-1]
        if "]" in last:
            return last.split("]", 1)[1].strip()
        return last.strip()
    except Exception as e:
        debug_store.log(f"Transcription failed: {e}")
        return ""


def capture_and_analyze_vision(user_text: str) -> str:
    try:
        subprocess.run(
            ["rpicam-still", "-t", "500", "-n", "--width", "640", "--height", "480", "-o", BMO_IMAGE_FILE],
            check=True,
            timeout=15,
        )
        resp = ollama.chat(
            model=VISION_MODEL,
            messages=[{"role": "user", "content": user_text, "images": [BMO_IMAGE_FILE]}],
            stream=False,
        )
        return resp["message"]["content"]
    except Exception as e:
        return f"I could not use the camera right now: {e}"


def maybe_set_timer(user_text: str) -> str | None:
    timer_match = re.search(r"(?:set )?(?:a )?(?:timer|alarm|reminder)(?: for| in)? (\\d+) (second|seconds|minute|minutes)", user_text.lower())
    if not timer_match:
        return None

    amount = int(timer_match.group(1))
    unit = timer_match.group(2)
    seconds = amount * 60 if "minute" in unit else amount
    due_at = time.time() + seconds

    timer_id = uuid.uuid4().hex[:8]
    reminder_line = f"Timer {timer_id} finished."

    def timer_worker():
        debug_store.log(reminder_line)
        out_file = os.path.join(AUDIO_DIR, f"timer_{timer_id}.wav")
        spoken = f"BMO timer done. {amount} {unit} is up."
        if synthesize_to_wav(spoken, out_file):
            threading.Thread(target=play_wav_on_pi, args=(out_file,), daemon=True).start()

    t = threading.Timer(seconds, timer_worker)
    t.daemon = True
    t.start()

    with timers_lock:
        timers.append({"id": timer_id, "due_at": due_at, "seconds": seconds})

    return f"Okay. I set a timer for {amount} {unit}."


def handle_game(session_id: str, user_text: str) -> str | None:
    lower = user_text.lower().strip()
    state = games.setdefault(session_id, GameState())

    if "trivia" in lower and state.mode is None:
        state.mode = "trivia"
        state.score = 0
        state.round = 0

    if "guessing game" in lower or "guess a number" in lower:
        state.mode = "guess"
        state.number_to_guess = random.randint(1, 20)
        state.round = 0
        return "I picked a number from 1 to 20. Tell me your guess."

    if state.mode == "trivia":
        if state.current_answer is None:
            question = random.choice(TRIVIA_BANK)
            state.current_answer = question["a"]
            state.round += 1
            return f"Trivia round {state.round}. {question['q']}"

        if lower == state.current_answer:
            state.score += 1
            state.current_answer = None
            return f"Correct. Score is now {state.score}. Want another trivia question?"

        if "quit" in lower or "stop" in lower:
            score = state.score
            games.pop(session_id, None)
            return f"Game over. Final trivia score: {score}."

        state.current_answer = None
        return "Not quite. Want another trivia question?"

    if state.mode == "guess":
        if "quit" in lower or "stop" in lower:
            games.pop(session_id, None)
            return "Guessing game stopped."

        num_match = re.search(r"\\b(\\d{1,2})\\b", lower)
        if not num_match:
            return "Give me a number from 1 to 20."

        guess = int(num_match.group(1))
        state.round += 1
        if guess == state.number_to_guess:
            tries = state.round
            games.pop(session_id, None)
            return f"You got it in {tries} tries. Nice game."
        if guess < state.number_to_guess:
            return "Too low. Try again."
        return "Too high. Try again."

    return None


def maybe_play_music(user_text: str) -> str | None:
    lower = user_text.lower()
    music_keywords = ["play music", "sing", "play a song", "jam", "chiptune"]
    if not any(k in lower for k in music_keywords):
        return None

    if not os.path.isdir(MUSIC_DIR):
        return "I want to jam, but sounds/music is missing."

    songs = [f for f in os.listdir(MUSIC_DIR) if f.lower().endswith(".wav")]
    if not songs:
        return "I want to jam, but sounds/music has no wav files yet."

    file_path = os.path.join(MUSIC_DIR, random.choice(songs))
    threading.Thread(target=play_wav_on_pi, args=(file_path,), daemon=True).start()
    return "Jamming now. Add more wav files into sounds/music for new songs."


def is_vision_request(user_text: str) -> bool:
    keys = ["what am i holding", "what do you see", "look at this", "does this look good", "use camera", "take a photo"]
    lower = user_text.lower()
    return any(k in lower for k in keys)


def chat_with_ollama(history: list, user_text: str) -> str:
    messages = [{"role": "system", "content": "You are a helpful offline Raspberry Pi robot assistant. Keep replies concise and friendly."}]
    messages.extend(history[-12:])
    messages.append({"role": "user", "content": user_text})

    response = ollama.chat(model=TEXT_MODEL, messages=messages, stream=False)
    return response["message"]["content"].strip()


app = FastAPI(title="Pi Robot Web UI")
os.makedirs(AUDIO_DIR, exist_ok=True)
templates = Jinja2Templates(directory=TEMPLATE_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/faces", StaticFiles(directory=os.path.join(BASE_DIR, "faces")), name="faces")


try:
    wake_model = Model(wakeword_model_paths=[WAKE_WORD_MODEL])
    wake_model_loaded = True
except Exception as e:
    wake_model = None
    wake_model_loaded = False
    debug_store.log(f"Wake word unavailable in web mode: {e}")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("web_index.html", {"request": request})


@app.get("/api/status")
async def status():
    try:
        tags = ollama.list()
        names = {m.get("name", "") for m in tags.get("models", [])}
        ready = TEXT_MODEL in names
        return {"status": "online" if ready else "model-missing", "model": TEXT_MODEL, "wakeword": wake_model_loaded}
    except Exception as e:
        return {"status": "offline", "error": str(e), "wakeword": wake_model_loaded}


@app.get("/api/debug")
async def debug_info():
    snapshot = debug_store.snapshot()
    now = time.time()
    with timers_lock:
        active_timers = [
            {"id": t["id"], "seconds_left": max(0, int(t["due_at"] - now))}
            for t in timers
            if t["due_at"] > now
        ]
    return {"logs": snapshot["logs"], "history": snapshot["history"], "timers": active_timers}


@app.get("/api/pronunciation")
async def get_pronunciation():
    return load_pronunciations()


@app.post("/api/pronunciation")
async def set_pronunciation(item: PronunciationRequest):
    mapping = load_pronunciations()
    mapping[item.word.lower()] = item.phonetic
    save_pronunciations(mapping)
    debug_store.log(f"Pronunciation override: {item.word} -> {item.phonetic}")
    return {"ok": True}


@app.get("/api/idle-signal")
async def idle_signal():
    mood = random.choice(["heart", "dizzy", "sleepy"])
    symbol = {"heart": "<3", "dizzy": "*", "sleepy": "zzz"}[mood]
    return {"mood": mood, "symbol": symbol}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    session_id = req.session_id or "default"
    user_text = req.message.strip()
    history = req.history or []

    if not user_text:
        return {"error": "Empty message"}

    debug_store.remember("user", user_text)

    timer_resp = maybe_set_timer(user_text)
    if timer_resp:
        bot_text = timer_resp
    else:
        game_resp = handle_game(session_id, user_text)
        if game_resp:
            bot_text = game_resp
        else:
            music_resp = maybe_play_music(user_text)
            if music_resp:
                bot_text = music_resp
            elif is_vision_request(user_text):
                bot_text = capture_and_analyze_vision(user_text)
            else:
                try:
                    bot_text = chat_with_ollama(history, user_text)
                except Exception as e:
                    bot_text = f"I hit a local LLM error: {e}"

    debug_store.remember("assistant", bot_text)
    debug_store.log(f"chat: {user_text[:60]}")

    audio_url = None
    output_name = f"response_{uuid.uuid4().hex[:8]}.wav"
    output_file = os.path.join(AUDIO_DIR, output_name)
    if synthesize_to_wav(bot_text, output_file):
        if req.play_on_pi_audio:
            threading.Thread(target=play_wav_on_pi, args=(output_file,), daemon=True).start()
        else:
            audio_url = f"/static/audio/{output_name}"

    return {"response": bot_text, "audio_url": audio_url}


@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    temp_path = os.path.join(AUDIO_DIR, f"upload_{uuid.uuid4().hex}.webm")
    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        text = transcribe_audio(temp_path)
        return {"text": text}
    finally:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass


@app.websocket("/api/wakeword")
async def wakeword_socket(ws: WebSocket):
    await ws.accept()
    if wake_model is None:
        await ws.send_json({"error": "wake word model unavailable"})
        await ws.close()
        return

    try:
        while True:
            data = await ws.receive_bytes()
            audio_chunk = np.frombuffer(data, dtype=np.int16)
            wake_model.predict(audio_chunk)
            fired = False
            for model_name, scores in wake_model.prediction_buffer.items():
                if scores and scores[-1] > WAKE_WORD_THRESHOLD:
                    await ws.send_json({"event": "wakeword_detected", "model": model_name})
                    debug_store.log(f"wake word detected by web stream: {model_name}")
                    wake_model.reset()
                    fired = True
                    break
            if fired:
                continue
    except WebSocketDisconnect:
        return
    except Exception as e:
        debug_store.log(f"wakeword websocket error: {e}")
        try:
            await ws.close()
        except Exception:
            pass


@app.get("/favicon.ico")
async def favicon():
    icon_path = os.path.join(BASE_DIR, "favicon.png")
    if os.path.exists(icon_path):
        return FileResponse(icon_path)
    return {"ok": True}
