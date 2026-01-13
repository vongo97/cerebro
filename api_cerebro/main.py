import os
from fastapi import FastAPI, HTTPException, Header, Body
from typing import List, Dict, Any, Optional
from api_cerebro.logic import brain
from api_cerebro.database import db
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Cerebro Free API")

CEREBRO_API_TOKEN = os.getenv("CEREBRO_API_TOKEN")

@app.get("/health")
async def health_check():
    return {"status": "alive", "version": "1.0.0"}

@app.post("/v1/chat/completions")
async def chat_completions(
    authorization: str = Header(None),
    payload: Dict[str, Any] = Body(...)
):
    # 1. Verificar Token de Seguridad
    if not CEREBRO_API_TOKEN or authorization != f"Bearer {CEREBRO_API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2. Extraer Parámetros
    messages = payload.get("messages", [])
    model = payload.get("model", "default")
    session_id = payload.get("session_id", "default_session")
    priority = payload.get("priority", "normal")

    if not messages:
        raise HTTPException(status_code=400, detail="Messages are required")

    # 3. Recuperar Contexto (Opcional, si el usuario no los envió todos)
    # n8n suele enviar todo el historial, pero por seguridad recuperamos de Supabase
    # history = db.get_history(session_id)
    # total_messages = history + messages # Depende de la implementación deseada

    # 4. Procesar con Brain (Cascada)
    result = await brain.chat_completion(messages, priority=priority)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    # 5. Guardar en Persistencia
    # Guardar el mensaje del usuario (el último recibid)
    user_msg = messages[-1]["content"]
    db.save_message(session_id, "user", user_msg)
    
    # Guardar la respuesta del asistente
    db.save_message(
        session_id, 
        "assistant", 
        result["content"], 
        model_used=result["model"]
    )

    # 6. Responder en formato OpenAI Compatible
    return {
        "id": "chatcmpl-cerebro",
        "object": "chat.completion",
        "created": 1234567, # Placeholder
        "model": result["model"],
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result["content"]
                }
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }
