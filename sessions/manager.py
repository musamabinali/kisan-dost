"""Session management for conversation persistence."""

import sqlite3
import json
import uuid
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any, List
from pathlib import Path
from config import settings
from models import FarmerProfile, FarmContext
import logging

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles date/datetime objects."""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

class SessionManager:
    """Manages conversation sessions with SQLite backend."""
    
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.session_db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    farmer_id TEXT NOT NULL,
                    farmer_profile TEXT,
                    farm_context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    message_count INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    agent_name TEXT,
                    tool_calls TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_farmer 
                ON sessions (farmer_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON messages (session_id)
            """)
            
            conn.commit()
    
    def create_session(
        self, 
        farmer_id: str,
        farmer_profile: FarmerProfile | None = None,
        farm_context: FarmContext | None = None
    ) -> str:
        """Create a new session."""
        session_id = str(uuid.uuid4())[:8]  # Short ID for readability
        expires_at = datetime.now() + timedelta(hours=settings.session_ttl_hours)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO sessions (session_id, farmer_id, farmer_profile, farm_context, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                farmer_id,
                json.dumps(farmer_profile.model_dump(), cls=DateTimeEncoder) if farmer_profile else None,
                json.dumps(farm_context.model_dump(), cls=DateTimeEncoder) if farm_context else None,
                expires_at.isoformat()
            ))
            conn.commit()
        
        logger.info(f"Created session {session_id} for farmer {farmer_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT * FROM sessions WHERE session_id = ? AND expires_at > ?
            """, (session_id, datetime.now().isoformat())).fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_session_by_farmer(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        """Get active session for a farmer."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT * FROM sessions 
                WHERE farmer_id = ? AND expires_at > ?
                ORDER BY updated_at DESC LIMIT 1
            """, (farmer_id, datetime.now().isoformat())).fetchone()
            
            if row:
                return dict(row)
            return None
    
    def update_session(
        self, 
        session_id: str,
        farmer_profile: FarmerProfile | None = None,
        farm_context: FarmContext | None = None
    ):
        """Update session data."""
        with sqlite3.connect(self.db_path) as conn:
            updates = []
            params = []
            
            if farmer_profile:
                updates.append("farmer_profile = ?")
                params.append(json.dumps(farmer_profile.model_dump(), cls=DateTimeEncoder))
            
            if farm_context:
                updates.append("farm_context = ?")
                params.append(json.dumps(farm_context.model_dump(), cls=DateTimeEncoder))
            
            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(session_id)
                
                conn.execute(f"""
                    UPDATE sessions SET {', '.join(updates)} WHERE session_id = ?
                """, params)
                conn.commit()
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        agent_name: str | None = None,
        tool_calls: list | None = None
    ):
        """Add a message to session history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO messages (session_id, role, content, agent_name, tool_calls)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                role,
                content,
                agent_name,
                json.dumps(tool_calls) if tool_calls else None
            ))
            
            # Update message count
            conn.execute("""
                UPDATE sessions SET message_count = message_count + 1, updated_at = ?
                WHERE session_id = ?
            """, (datetime.now().isoformat(), session_id))
            
            conn.commit()
    
    def get_messages(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent messages for a session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM messages 
                WHERE session_id = ? 
                ORDER BY timestamp DESC LIMIT ?
            """, (session_id, limit)).fetchall()
            
            return [dict(row) for row in reversed(rows)]
    
    def get_farmer_context(self, session_id: str) -> tuple[FarmerProfile | None, FarmContext | None]:
        """Get farmer profile and farm context from session."""
        session = self.get_session(session_id)
        if not session:
            return None, None
        
        profile = None
        context = None
        
        if session.get("farmer_profile"):
            try:
                profile = FarmerProfile.model_validate(json.loads(session["farmer_profile"]))
            except Exception as e:
                logger.warning(f"Failed to parse farmer profile: {e}")
        
        if session.get("farm_context"):
            try:
                context = FarmContext.model_validate(json.loads(session["farm_context"]))
            except Exception as e:
                logger.warning(f"Failed to parse farm context: {e}")
        
        return profile, context
    
    def cleanup_expired(self) -> int:
        """Remove expired sessions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM sessions WHERE expires_at < ?
            """, (datetime.now().isoformat(),))
            conn.commit()
            return cursor.rowcount
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            active = conn.execute("""
                SELECT COUNT(*) FROM sessions WHERE expires_at > ?
            """, (datetime.now().isoformat(),)).fetchone()[0]
            total_messages = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            
            return {
                "total_sessions": total,
                "active_sessions": active,
                "total_messages": total_messages,
                "db_path": self.db_path
            }


# Global session manager instance
session_manager = SessionManager()