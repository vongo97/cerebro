import os
from typing import List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

class Database:
    def __init__(self):
        print("======== CEREBRO DB CONFIG ========")
        print("Versión del código: 1.1 (Con Validación)")
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not url or "tu_proyecto" in url:
            print(f"ERROR: SUPABASE_URL inválida: {url}")
            raise ValueError("SUPABASE_URL no configurada o sigue siendo el valor de ejemplo.")
        
        # Mostrar solo los primeros caracteres por seguridad
        key_preview = f"{key[:10]}..." if key else "NULA"
        print(f"CEREBRO_LOG: Intentando conectar a {url} con llave {key_preview}")

        try:
            self.client: Client = create_client(url, key)
            print("CEREBRO_LOG: Cliente Supabase creado exitosamente.")
        except Exception as e:
            print(f"CEREBRO_LOG: Error crítico en create_client: {e}")
            raise

    def save_message(self, session_id: str, role: str, content: str, model_used: str = None, tokens: int = 0):
        data = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "model_used": model_used,
            "tokens_used": tokens
        }
        return self.client.table("interacciones").insert(data).execute()

    def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        response = self.client.table("interacciones") \
            .select("*") \
            .eq("session_id", session_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        
        # Invertir para que estén en orden cronológico
        messages = response.data[::-1]
        return [{"role": m["role"], "content": m["content"]} for m in messages]

db = Database()
