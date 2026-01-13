import os
import httpx
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Lista de modelos gratuitos en OpenRouter (en orden de preferencia)
FREE_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "deepseek/deepseek-r1:free",
    "meta-llama/llama-3.3-70b-instruct:free",
]

class Brain:
    def __init__(self):
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    async def chat_completion(self, messages: List[Dict[str, str]], priority: str = "normal") -> Dict[str, Any]:
        """
        Lógica de cascada: 
        1. Intenta con OpenRouter (modelos free secuencialmente).
        2. Si falla todo OpenRouter, intenta con Google Gemini Directo.
        """
        
        # 1. Intentar con OpenRouter
        for model in FREE_MODELS:
            try:
                response = await self._call_openrouter(messages, model)
                if response:
                    return {
                        "content": response["choices"][0]["message"]["content"],
                        "model": model,
                        "source": "openrouter"
                    }
            except Exception as e:
                print(f"Error con modelo {model} en OpenRouter: {e}")
                continue

        # 2. Respaldo Final: Google Gemini Directo
        try:
            response = await self._call_gemini_direct(messages)
            if response:
                return {
                    "content": response,
                    "model": "gemini-1.5-flash",
                    "source": "google_direct"
                }
        except Exception as e:
            print(f"Error crítico en callback de Gemini Directo: {e}")
        
        return {"error": "Todos los modelos fallaron"}

    async def _call_openrouter(self, messages: List[Dict[str, str]], model: str):
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/vongole/cerebro", # Opcional
            "X-Title": "Cerebro Free",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.openrouter_url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    async def _call_gemini_direct(self, messages: List[Dict[str, str]]):
        # Convertir mensajes de formato OpenAI a formato Gemini
        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
        
        payload = {"contents": contents}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.gemini_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

brain = Brain()
