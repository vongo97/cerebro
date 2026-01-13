import os
import sys
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Header, Body
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# --- 1. CONFIGURACIÓN ---
os.environ["CEREBRO_API_TOKEN"] = "test_token_123"

# --- 2. LÓGICA DEL CEREBRO (logic.py simplificado) ---
class Brain:
    async def chat_completion(self, messages: List[Dict[str, str]], priority: str = "normal") -> Dict[str, Any]:
        # Simulación de Cascada: OpenRouter falla -> Gemini Directo funciona
        print(f"\n[BRAIN] Simulando Cascada: Intentando OpenRouter...")
        print(f"[BRAIN] Simulando Fallo en OpenRouter (Rate Limit)")
        print(f"[BRAIN] Saltando a Fallback: Google Gemini Directo")
        return {
            "content": "Esta es una respuesta del Cerebro Free (vía Gemini Fallback). ¡Todo funciona!",
            "model": "gemini-1.5-flash",
            "source": "google_direct"
        }

brain = Brain()

# --- 3. SERVIDOR (main.py simplificado) ---
app = FastAPI()

@app.post("/v1/chat/completions")
async def chat_completions(authorization: str = Header(None), payload: Dict[str, Any] = Body(...)):
    if authorization != "Bearer test_token_123":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    messages = payload.get("messages", [])
    session_id = payload.get("session_id", "demo_session")
    
    # Procesar
    result = await brain.chat_completion(messages)
    
    # Simular persistencia
    print(f"[DB] Guardando interacción para sesión: {session_id}")
    
    return {
        "model": result["model"],
        "choices": [{"message": {"role": "assistant", "content": result["content"]}}],
        "source_info": result["source"]
    }

# --- 4. EJECUCIÓN DE LA PRUEBA ---
def run_test():
    client = TestClient(app)
    print("\n" + "="*50)
    print("DEMOSTRACIÓN INTEGRAL: CEREBRO FREE")
    print("="*50)
    
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer test_token_123"},
        json={
            "messages": [{"role": "user", "content": "Hola Cerebro, ¿estás listo?"}],
            "session_id": "n8n_test_999"
        }
    )
    
    if response.status_code == 200:
        res = response.json()
        print(f"\n[CLIENTE] Código de Estado: {response.status_code}")
        print(f"[CLIENTE] Fuente detectada: {res['source_info']}")
        print(f"[CLIENTE] Respuesta Recibida:\n{res['choices'][0]['message']['content']}")
        print("\n" + "="*50)
        print("RESULTADO: PRUEBA EXITOSA")
        print("="*50)
    else:
        print(f"Error en la prueba: {response.text}")

if __name__ == "__main__":
    run_test()
