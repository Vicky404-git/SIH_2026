import os
import sqlite3
import ollama
from pathlib import Path
from .rag import get_db, _store_chunk, clear_session

THRESHOLD = 50  # Trigger consolidation after 50 chat messages

def check_and_consolidate(project_id: str = "workbench"):
    db_path = f"memory/{project_id}.db"
    if not os.path.exists(db_path):
        return

    db = get_db(db_path)
    try:
        cursor = db.execute("SELECT COUNT(*) as cnt FROM chunks WHERE source_type = 'chat'")
        row = cursor.fetchone()
        count = row["cnt"] if row else 0

        if count < THRESHOLD:
            return

        # Fetch raw chat history
        chats = db.execute("SELECT content FROM chunks WHERE source_type = 'chat' ORDER BY rowid ASC").fetchall()
        chat_text = "\n".join([c["content"] for c in chats])

        # Summarize via local Ollama model
        prompt = (
            "Summarize the following chat interaction history densely and factually. "
            "Focus on technical decisions, code changes, and progress made. Do not hallucinate.\n\n"
            f"{chat_text}"
        )
        
        response = ollama.generate(model="llama3.2:3b", prompt=prompt)
        summary = response.get("response", "").strip()

        if not summary:
            return

        # Store summary as a permanent 'doc' chunk
        vec_response = ollama.embeddings(model="nomic-embed-text", prompt=summary)
        vec = vec_response.get("embedding")
        
        if vec:
            _store_chunk(db, file_path=f"summary:{project_id}", content=summary, source_type="doc", vec=vec)
            db.commit()

        # Clear raw chat rows to keep database fast
        clear_session(db_path=db_path)

    except Exception as e:
        print(f"[MemoryManager] Consolidation failed: {e}")
    finally:
        db.close()
