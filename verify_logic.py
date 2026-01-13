import httpx
import asyncio
from unittest.mock import AsyncMock, patch
import os

# Simulación básica para probar la lógica sin gastar tokens reales si no hay keys
async def test_logic_cascade():
    from app.logic import Brain
    
    brain = Brain()
    messages = [{"role": "user", "content": "Hola"}]
    
    print("--- Probando Cascada de Resiliencia (Mock) ---")
    
    # 1. Simular fallo en OpenRouter y éxito en Gemini Directo
    with patch("app.logic.Brain._call_openrouter", side_effect=Exception("OpenRouter Down")), \
         patch("app.logic.Brain._call_gemini_direct", return_value="Respuesta de Gemini Directo"):
        
        result = await brain.chat_completion(messages)
        print(f"Resultado Fallback: {result}")
        assert result["source"] == "google_direct"

    # 2. Simular éxito en el primer modelo de OpenRouter
    with patch("app.logic.Brain._call_openrouter", return_value={"choices": [{"message": {"content": "Respuesta OpenRouter"}}]}):
        result = await brain.chat_completion(messages)
        print(f"Resultado Éxito: {result}")
        assert result["source"] == "openrouter"

    print("--- Verificación de lógica completada ---")

if __name__ == "__main__":
    # Asegurar que existan variables dummy para cargar el módulo
    os.environ["SUPABASE_URL"] = "http://localhost"
    os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "dummy"
    os.environ["OPENROUTER_API_KEY"] = "dummy"
    os.environ["GEMINI_API_KEY"] = "dummy"
    os.environ["CEREBRO_API_TOKEN"] = "dummy"
    
    asyncio.run(test_logic_cascade())
