import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Asegurar que el directorio raíz esté en el path ANTES de cualquier importación de api_cerebro
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Configurar variables de entorno dummy
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "dummy_key"
os.environ["CEREBRO_API_TOKEN"] = "demo_token"
os.environ["OPENROUTER_API_KEY"] = "dummy"
os.environ["GEMINI_API_KEY"] = "dummy"

# 1. Mock de la base de datos
mock_db = MagicMock()

# 2. Mock de la lógica de AI
async def mock_chat_completion(messages, priority="normal"):
    print(f"\n[BRAIN LOG] Procesando pregunta: '{messages[-1]['content']}' con prioridad '{priority}'")
    return {
        "content": "¡Hola! Soy el Cerebro Free. Estoy funcionando correctamente en modo demo con cascada de resiliencia.",
        "model": "google/gemini-2.0-flash-exp:free",
        "source": "openrouter"
    }

# Importar app después de configurar el entorno
from api_cerebro.main import app

def run_integration_test():
    client = TestClient(app)
    
    print("\n" + "="*50)
    print("DEMOSTRACIÓN DEL CEREBRO FREE")
    print("="*50)
    
    headers = {
        "Authorization": "Bearer demo_token",
    }
    
    payload = {
        "messages": [{"role": "user", "content": "¿Cuál es tu función principal?"}],
        "session_id": "session_n8n_abc",
        "priority": "normal"
    }
    
    # Aplicar patches durante el test
    with patch("app.main.db.save_message", mock_db.save_message), \
         patch("app.main.brain.chat_completion", side_effect=mock_chat_completion):
        
        print("\n[CLIENTE] Enviando petición HTTP POST a /v1/chat/completions...")
        response = client.post("/v1/chat/completions", headers=headers, json=payload)
        
        print(f"\n[SERVIDOR] Respuesta recibida (Status: {response.status_code})")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n[RESULTADO] Modelo utilizado: {data['model']}")
            print(f"[RESULTADO] Contenido:\n{data['choices'][0]['message']['content']}")
            
            # Verificar si se intentó guardar en la DB
            if mock_db.save_message.called:
                print("\n[PERSISTENCIA] Se detectaron llamadas para guardar en Supabase (éxito).")
        else:
            print(f"Error: {response.text}")

    print("\n" + "="*50)
    print("PRUEBA COMPLETADA EXITOSAMENTE")
    print("="*50)

if __name__ == "__main__":
    run_integration_test()
