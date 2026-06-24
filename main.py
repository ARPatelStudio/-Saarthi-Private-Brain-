from fastapi import FastAPI, Request
from llama_cpp import Llama
import os
import urllib.request

app = FastAPI()

# 🚀 NAYA, 100% WORKING MODEL URL (Case Sensitive Fix)
MODEL_URL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MODEL_PATH = "tinyllama-1.1b.gguf"

# Download model silently if it doesn't exist on server
if not os.path.exists(MODEL_PATH):
    print(f"Downloading Private LLM Model from: {MODEL_URL}")
    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Download Complete!")
    except Exception as e:
        print(f"CRITICAL ERROR Downloading Model: {str(e)}")
        # Agar download fail ho toh server crash hone se roko
        pass

# Load Model into Memory (Only if download was successful)
if os.path.exists(MODEL_PATH):
    try:
        llm = Llama(model_path=MODEL_PATH, n_ctx=1024, n_threads=2)
    except Exception as e:
        print(f"Error loading model into RAM: {e}")
        llm = None
else:
    llm = None

@app.post("/api/private_chat")
async def chat(request: Request):
    if llm is None:
        return {"reply": "Boss, Private server par model download ya load nahi ho paaya. Please logs check karein."}

    data = await request.json()
    system_prompt = data.get("system", "You are Jarvis.")
    user_message = data.get("user", "")

    # TinyLlama Prompt Format
    prompt = f"<|system|>\n{system_prompt}</s>\n<|user|>\n{user_message}</s>\n<|assistant|>\n"
    
    try:
        output = llm(prompt, max_tokens=256, stop=["</s>"], echo=False)
        response_text = output['choices'][0]['text'].strip()
        return {"reply": response_text}
    except Exception as e:
        return {"reply": f"Boss, Private server error: {str(e)}"}
