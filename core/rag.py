"""
CLANKA RAG ENGINE v3.0 (sqlite-vec)
====================================
Pure logic module - no console/CLI printing here. Callers (CLI layer,
DaemonV, etc.) decide how to surface progress/errors.

Replaces sqlite-vss (unmaintained) with sqlite-vec (actively maintained).

Two kinds of memory live in the same `chunks` table, distinguished by
`source_type`, so they can be filtered independently and never get
wiped by each other's rebuild:

    'code'  - project/codebase chunks, rebuilt via build_index()
    'doc'   - manuals/SOPs/reference docs, same rebuild path as 'code'
    'chat'  - conversational memory, appended to over time, NEVER
              dropped wholesale by build_index()

`score` and `last_accessed` exist so a future consolidation job can
rank 'chat' rows by importance (recency + retrieval frequency) without
schema changes.
"""

import os
import struct
import sqlite3
import time
from pathlib import Path

import sqlite_vec

try:
    import ollama
except ImportError:  # keep the module importable even without ollama installed
    ollama = None

EMBED_MODEL = "nomic-embed-text"
EMBED_DIM = 768
DB_PATH = "memory/clanka.db"
IGNORE_DIRS = {'.git', '.venv', '__pycache__', 'build', 'clanka.egg-info', 'node_modules', 'memory'}

# source_types that build_index() owns and is allowed to rebuild wholesale.
# 'chat' is deliberately excluded - it's append-only from this module's POV.
INDEXABLE_TYPES = ('code', 'doc')


# ==========================================
# LOW-LEVEL HELPERS
# ==========================================

def _serialize(vec):
    """Pack a list of floats into the blob format sqlite-vec expects."""
    return struct.pack(f"{len(vec)}f", *vec)


def get_embedding(text):
    """Pings local Ollama to turn text into an embedding vector.
    Returns None on failure - callers must check for that.
    """
    if ollama is None:
        return None
    try:
        response = ollama.embeddings(model=EMBED_MODEL, prompt=text)
        return response['embedding']
    except Exception:
        return None


def get_db(db_path=DB_PATH):
    """Connects to SQLite and loads the sqlite-vec extension."""
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    db = sqlite3.connect(db_path)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    db.row_factory = sqlite3.Row
    init_db(db)
    return db


def init_db(db):
    """Creates tables if they don't exist. Safe to call every connect."""
    db.execute('''
        CREATE TABLE IF NOT EXISTS chunks (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            content TEXT,
            source_type TEXT DEFAULT 'code',
            score REAL DEFAULT 1.0,
            last_accessed REAL DEFAULT (unixepoch())
        )
    ''')
    db.execute(f'''
        CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks USING vec0(
            embedding float[{EMBED_DIM}]
        )
    ''')
    db.commit()


# ==========================================
# STORAGE
# ==========================================

def _store_chunk(db, file_path, content, source_type, vec, score=1.0):
    """Inserts one chunk + its embedding, linked by rowid. Returns the rowid."""
    cursor = db.execute(
        "INSERT INTO chunks (file_path, content, source_type, score, last_accessed) "
        "VALUES (?, ?, ?, ?, unixepoch())",
        (file_path, content, source_type, score)
    )
    rowid = cursor.lastrowid
    db.execute(
        "INSERT INTO vec_chunks (rowid, embedding) VALUES (?, ?)",
        (rowid, _serialize(vec))
    )
    return rowid


def add_chat_memory(prompt, response, persona=None, db_path=DB_PATH):
    """Embeds and stores one (prompt, response) exchange as chat memory.
    Never touches 'code'/'doc' rows. Safe to call after every turn.
    """
    text = f"User: {prompt}\nAssistant: {response}"
    vec = get_embedding(text)
    if vec is None:
        return None

    db = get_db(db_path)
    try:
        file_path = f"chat:{persona}" if persona else "chat"
        rowid = _store_chunk(db, file_path, text, "chat", vec, score=1.0)
        db.commit()
        return rowid
    finally:
        db.close()


# ==========================================
# INDEXING (code / docs)
# ==========================================

def build_index(directory=".", db_path=DB_PATH, on_progress=None):
    """Scans files, chunks them, and (re)stores them as 'code'/'doc' chunks.

    Only rebuilds INDEXABLE_TYPES - 'chat' memory is left untouched.
    on_progress(str) is an optional callback for status lines instead
    of printing directly (keeps this module CLI-agnostic).
    """
    def report(msg):
        if on_progress:
            on_progress(msg)

    report(f"Building index for '{directory}'...")
    db = get_db(db_path)

    try:
        # Delete only the rebuildable source types (and their vectors),
        # leave 'chat' memory alone.
        placeholders = ",".join("?" for _ in INDEXABLE_TYPES)
        rows = db.execute(
            f"SELECT rowid FROM chunks WHERE source_type IN ({placeholders})",
            INDEXABLE_TYPES
        ).fetchall()
        old_rowids = [r["rowid"] for r in rows]
        if old_rowids:
            vec_placeholders = ",".join("?" for _ in old_rowids)
            db.execute(f"DELETE FROM vec_chunks WHERE rowid IN ({vec_placeholders})", old_rowids)
            db.execute(f"DELETE FROM chunks WHERE rowid IN ({vec_placeholders})", old_rowids)
            db.commit()

        chunk_count = 0
        doc_exts = {'.md', '.txt'}

        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]

            for file in files:
                if not file.endswith(('.py', '.md', '.txt', '.sh', '.toml')):
                    continue

                filepath = Path(root) / file
                source_type = 'doc' if filepath.suffix in doc_exts else 'code'

                try:
                    content = filepath.read_text(errors='ignore')
                    chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 40]

                    for chunk in chunks:
                        vec = get_embedding(chunk)
                        if vec:
                            _store_chunk(db, str(filepath), chunk, source_type, vec)
                            chunk_count += 1

                except Exception as e:
                    report(f"Skipped {filepath}: {e}")

        db.commit()
        report(f"Indexing complete. {chunk_count} chunks stored ({db_path}).")
        return chunk_count
    finally:
        db.close()


# ==========================================
# SEARCH
# ==========================================

def search(query, top_k=3, source_types=None, db_path=DB_PATH):
    """Vector search, optionally filtered to specific source_types.

    source_types: e.g. ('code',) or ('chat', 'doc'). None = search everything.
    Bumps score + last_accessed on hits (feeds future consolidation ranking).
    Returns list of (distance, {"file":..., "content":..., "source_type":...}).
    """
    if not os.path.exists(db_path):
        return []

    query_vec = get_embedding(query)
    if query_vec is None:
        return []

    db = get_db(db_path)
    try:
        if source_types:
            type_filter = " AND chunks.source_type IN ({})".format(
                ",".join("?" for _ in source_types)
            )
            params = (_serialize(query_vec), top_k, *source_types)
        else:
            type_filter = ""
            params = (_serialize(query_vec), top_k)

        # sqlite-vec requires the MATCH+k clause on the virtual table itself;
        # do the vector search first, then join+filter on metadata.
        cursor = db.execute(f"""
            SELECT chunks.rowid, chunks.file_path, chunks.content,
                   chunks.source_type, vec_chunks.distance
            FROM vec_chunks
            JOIN chunks ON chunks.rowid = vec_chunks.rowid
            WHERE vec_chunks.embedding MATCH ? AND k = ?
            {type_filter}
            ORDER BY vec_chunks.distance
        """, params)

        results = []
        hit_rowids = []
        for row in cursor.fetchall():
            results.append((
                row['distance'],
                {
                    "file": row['file_path'],
                    "content": row['content'],
                    "source_type": row['source_type'],
                }
            ))
            hit_rowids.append(row['rowid'])

        if hit_rowids:
            ph = ",".join("?" for _ in hit_rowids)
            db.execute(
                f"UPDATE chunks SET score = score + 0.1, last_accessed = unixepoch() "
                f"WHERE rowid IN ({ph})",
                hit_rowids
            )
            db.commit()

        return results
    finally:
        db.close()


# ==========================================
# STANDALONE TESTING
# ==========================================
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "index":
        build_index(on_progress=print)
    elif len(sys.argv) > 2 and sys.argv[1] == "search":
        query = " ".join(sys.argv[2:])
        print(f"Searching for: '{query}'")
        for score, doc in search(query):
            print(f"\n[Distance: {score:.4f}] ({doc['source_type']}) {doc['file']}")
            print(f"Content: {doc['content'][:200]}...")
