from fastapi import FastAPI, Request
from llama_cpp import Llama
import os
import urllib.request

app = FastAPI()

# Model Path (Using TinyLlama for Low-RAM Servers like Render Free Tier)
MODEL_URL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.q4_k_m.gguf"
MODEL_PATH = "tinyllama-1.1b.gguf"

# Download model silently if it doesn't exist on server
if not os.path.exists(MODEL_PATH):
    print("Downloading Private LLM Model...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Download Complete!")

# Load Model into Memory
llm = Llama(model_path=MODEL_PATH, n_ctx=1024, n_threads=2)

@app.post("/api/private_chat")
async def chat(request: Request):
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

# Render Start Command: uvicorn main:app --host 0.0.0.0 --port 10000
