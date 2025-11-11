"""
SQLite database for multi-session chat history and metadata.
"""
import aiosqlite
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: Path):
        self.db_path = str(db_path)
        self.db_path_obj = db_path
        
    async def init_db(self):
        """Initialize database schema."""
        db_path_obj = Path(self.db_path)
        db_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    media_url TEXT,
                    media_type TEXT,
                    timestamp TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    brand_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    uploaded_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    brand_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS vectors (
                    id TEXT PRIMARY KEY,
                    chunk_id TEXT NOT NULL,
                    brand_id TEXT NOT NULL,
                    vector_index INTEGER NOT NULL,
                    FOREIGN KEY (chunk_id) REFERENCES chunks(id) ON DELETE CASCADE
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS brands (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_ingested_at TEXT,
                    metadata TEXT
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    job_type TEXT NOT NULL,
                    model_id TEXT,
                    status TEXT NOT NULL,
                    input_data TEXT,
                    output_data TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
                )
            """)
            
            await db.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_chunks_brand ON chunks(brand_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_vectors_brand ON vectors(brand_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_session ON jobs(session_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_type ON jobs(job_type)")
            
            await db.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    async def create_session(self, session_id: str, name: str, metadata: Optional[Dict] = None) -> Dict:
        """Create a new chat session."""
        now = datetime.utcnow().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO sessions (id, name, created_at, updated_at, metadata) VALUES (?, ?, ?, ?, ?)",
                (session_id, name, now, now, json.dumps(metadata or {}))
            )
            await db.commit()
        return {"id": session_id, "name": name, "created_at": now, "updated_at": now}
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
        return None
    
    async def list_sessions(self) -> List[Dict]:
        """List all sessions."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM sessions ORDER BY updated_at DESC") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            await db.commit()
            return cursor.rowcount > 0
    
    async def add_message(self, session_id: str, role: str, content: str, 
                         media_url: Optional[str] = None, media_type: Optional[str] = None,
                         metadata: Optional[Dict] = None) -> Dict:
        """Add a message to a session."""
        now = datetime.utcnow().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO messages (session_id, role, content, media_url, media_type, timestamp, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (session_id, role, content, media_url, media_type, now, json.dumps(metadata or {}))
            )
            message_id = cursor.lastrowid
            
            await db.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id))
            await db.commit()
            
        return {
            "id": message_id,
            "session_id": session_id,
            "role": role,
            "content": content,
            "media_url": media_url,
            "media_type": media_type,
            "timestamp": now
        }
    
    async def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get messages for a session."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = "SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp ASC"
            if limit:
                query += f" LIMIT {limit}"
            async with db.execute(query, (session_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def save_document(self, doc_id: str, brand_id: str, filename: str, 
                           file_type: str, metadata: Optional[Dict] = None) -> Dict:
        """Save document metadata."""
        now = datetime.utcnow().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO documents (id, brand_id, filename, file_type, uploaded_at, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                (doc_id, brand_id, filename, file_type, now, json.dumps(metadata or {}))
            )
            await db.commit()
        return {"id": doc_id, "brand_id": brand_id, "filename": filename, "uploaded_at": now}
    
    async def save_chunk(self, chunk_id: str, document_id: str, brand_id: str, 
                        content: str, chunk_index: int, metadata: Optional[Dict] = None) -> Dict:
        """Save chunk metadata."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO chunks (id, document_id, brand_id, content, chunk_index, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                (chunk_id, document_id, brand_id, content, chunk_index, json.dumps(metadata or {}))
            )
            await db.commit()
        return {"id": chunk_id, "document_id": document_id, "brand_id": brand_id}
    
    async def save_vector(self, vector_id: str, chunk_id: str, brand_id: str, vector_index: int) -> Dict:
        """Save vector metadata."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO vectors (id, chunk_id, brand_id, vector_index) VALUES (?, ?, ?, ?)",
                (vector_id, chunk_id, brand_id, vector_index)
            )
            await db.commit()
        return {"id": vector_id, "chunk_id": chunk_id, "vector_index": vector_index}
    
    async def get_brand_chunks(self, brand_id: str) -> List[Dict]:
        """Get all chunks for a brand."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM chunks WHERE brand_id = ?", (brand_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def list_brands(self) -> List[str]:
        """List all unique brand IDs."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT DISTINCT brand_id FROM documents ORDER BY brand_id") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
    
    async def delete_brand(self, brand_id: str) -> int:
        """Delete all data for a brand."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM vectors WHERE brand_id = ?", (brand_id,))
            await db.execute("DELETE FROM chunks WHERE brand_id = ?", (brand_id,))
            cursor = await db.execute("DELETE FROM documents WHERE brand_id = ?", (brand_id,))
            await db.execute("DELETE FROM brands WHERE id = ?", (brand_id,))
            await db.commit()
            return cursor.rowcount
    
    async def create_brand(self, brand_id: str, name: str, metadata: Optional[Dict] = None) -> Dict:
        """Create or update a brand."""
        now = datetime.utcnow().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT OR REPLACE INTO brands (id, name, created_at, last_ingested_at, metadata)
                   VALUES (?, ?, COALESCE((SELECT created_at FROM brands WHERE id = ?), ?), ?, ?)""",
                (brand_id, name, brand_id, now, now, json.dumps(metadata or {}))
            )
            await db.commit()
        return {"id": brand_id, "name": name, "last_ingested_at": now}
    
    async def get_brand(self, brand_id: str) -> Optional[Dict]:
        """Get brand by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM brands WHERE id = ?", (brand_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
        return None
    
    async def list_brands_with_stats(self) -> List[Dict]:
        """List all brands with document/chunk/vector counts."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT 
                    b.id,
                    b.name,
                    b.created_at,
                    b.last_ingested_at,
                    COUNT(DISTINCT d.id) as documents,
                    COUNT(DISTINCT c.id) as chunks,
                    COUNT(DISTINCT v.id) as vectors
                FROM brands b
                LEFT JOIN documents d ON b.id = d.brand_id
                LEFT JOIN chunks c ON b.id = c.brand_id
                LEFT JOIN vectors v ON b.id = v.brand_id
                GROUP BY b.id
                ORDER BY b.last_ingested_at DESC
            """) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def create_job(self, job_id: str, job_type: str, session_id: Optional[str] = None,
                        model_id: Optional[str] = None, input_data: Optional[Dict] = None,
                        metadata: Optional[Dict] = None) -> Dict:
        """Create a new job record."""
        now = datetime.utcnow().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO jobs (id, session_id, job_type, model_id, status, input_data, created_at, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (job_id, session_id, job_type, model_id, "pending", json.dumps(input_data or {}), now, json.dumps(metadata or {}))
            )
            await db.commit()
        return {"id": job_id, "job_type": job_type, "status": "pending", "created_at": now}
    
    async def update_job(self, job_id: str, status: str, output_data: Optional[Dict] = None) -> bool:
        """Update job status and output."""
        now = datetime.utcnow().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """UPDATE jobs SET status = ?, output_data = ?, completed_at = ? WHERE id = ?""",
                (status, json.dumps(output_data or {}), now, job_id)
            )
            await db.commit()
            return cursor.rowcount > 0
    
    async def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
        return None
