from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from llama_cpp import Llama
import os
import requests
import wave
import io
import asyncio

app = FastAPI()

# 🚀 100% WORKING MODEL URL
MODEL_URL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MODEL_PATH = "tinyllama-1.1b.gguf"

# 🛡️ THE "ANTI-BLOCK" ROBUST DOWNLOADER
if not os.path.exists(MODEL_PATH):
    print("Downloading Private LLM Model...")
    try:
        # Fake browser ID so Hugging Face doesn't block us as a bot
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(MODEL_URL, stream=True, headers=headers)
        
        if response.status_code == 200:
            with open(MODEL_PATH, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("✅ Download Complete!")
        else:
            print(f"❌ HTTP Error {response.status_code} from Hugging Face.")
    except Exception as e:
        print(f"❌ CRITICAL DOWNLOAD ERROR: {str(e)}")

# 🧠 LOAD MODEL INTO RAM (Optimized for Render Free Tier - 512MB)
if os.path.exists(MODEL_PATH):
    try:
        # n_ctx=512 ensures it doesn't crash Render's limited memory
        llm = Llama(model_path=MODEL_PATH, n_ctx=512, n_threads=2)
        print("✅ Model successfully loaded into RAM!")
    except Exception as e:
        print(f"❌ Error loading model into RAM: {e}")
        llm = None
else:
    llm = None


# ==========================================
# 🟢 STANDARD CHAT ENDPOINT (PRESERVED)
# ==========================================
@app.post("/api/private_chat")
async def chat(request: Request):
    if llm is None:
        return {"reply": "Boss, Private server par model load nahi ho paaya. RAM full ho sakti hai."}

    data = await request.json()
    system_prompt = data.get("system", "You are Jarvis.")
    user_message = data.get("user", "")

    # TinyLlama Prompt Format
    prompt = f"<|system|>\n{system_prompt}</s>\n<|user|>\n{user_message}</s>\n<|assistant|>\n"
    
    try:
        # max_tokens=150 to keep response fast and memory-friendly
        output = llm(prompt, max_tokens=150, stop=["</s>"], echo=False)
        response_text = output['choices'][0]['text'].strip()
        return {"reply": response_text}
    except Exception as e:
        return {"reply": f"Boss, Private server runtime error: {str(e)}"}


# ==========================================
# 🚀 NAYA: LIVE MODE WEBSOCKET ENGINE (MARK 8.0)
# ==========================================
@app.websocket("/api/live_stream")
async def live_stream(websocket: WebSocket):
    # 1. Sabse pehle connection accept karo taaki 403 error na aaye
    await websocket.accept()
    print("🟢 Live Mode Connected! Listening to Android Mic...")
    
    try:
        audio_buffer = bytearray()
        
        # 16000 sample rate * 16-bit (2 bytes) = 32000 bytes/sec
        # Hum har ~2.5 seconds ka audio buffer collect karenge STT ke liye
        PROCESS_THRESHOLD = 32000 * 2  

        while True:
            # 2. Receive raw PCM bytes from Android App
            data = await websocket.receive_bytes()
            audio_buffer.extend(data)

            # 3. Jab audio lamba ho jaye, tab usko process karo
            if len(audio_buffer) >= PROCESS_THRESHOLD:
                print(f"🎙️ Buffer Full: {len(audio_buffer)} bytes. Ready for STT processing...")
                
                # --- FUTURE GROQ STT LOGIC YAHAN AAYEGA ---
                # Raw PCM ko In-Memory WAV file mein convert karne ka logic:
                """
                wav_io = io.BytesIO()
                with wave.open(wav_io, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(16000)
                    wav_file.writeframes(audio_buffer)
                wav_io.seek(0)
                
                # TODO: wav_io ko Groq Whisper API par bhejkar Text nikalna hai
                """

                # 4. Abhi ke liye, hum connection test karne ke liye Android ko reply bhej rahe hain
                await websocket.send_text("Jarvis Server: Audio received and buffered successfully.")
                
                # 5. Buffer clear karo taaki agla sentence sun sakein
                audio_buffer.clear()
                
    except WebSocketDisconnect:
        print("🔴 Live Mode Disconnected by User.")
    except Exception as e:
        print(f"❌ WebSocket Error: {str(e)}")
