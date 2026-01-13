import os
from typing import List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

class Database:
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
