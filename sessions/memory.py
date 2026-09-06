"""Conversation memory and summarization."""

from typing import List, Dict, Any, Optional
from sessions.manager import session_manager
import json
import logging

logger = logging.getLogger(__name__)

class ConversationMemory:
    """Manages conversation memory with summarization."""
    
    def __init__(self, session_id: str, max_messages: int = 20):
        self.session_id = session_id
        self.max_messages = max_messages
        self._summary: Optional[str] = None
    
    def get_recent_messages(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get recent messages from session."""
        limit = limit or self.max_messages
        return session_manager.get_messages(self.session_id, limit)
    
    def get_context_window(self, max_tokens: int = 4000) -> List[Dict[str, Any]]:
        """
        Get messages that fit within token budget.
        In production, use actual token counting.
        """
        messages = self.get_recent_messages(self.max_messages)
        
        # Simple heuristic: ~4 chars per token, aim for max_tokens
        # Keep system + recent user/assistant pairs
        if len(messages) <= 10:
            return messages
        
        # Keep first message (system/greeting) and last 8
        return [messages[0]] + messages[-8:]
    
    def build_summary(self) -> str:
        """Build a summary of the conversation so far."""
        if self._summary:
            return self._summary
        
        messages = self.get_recent_messages(50)
        
        if not messages:
            return "New conversation."
        
        # Extract key information
        topics = set()
        crops_mentioned = set()
        tools_used = set()
        
        for msg in messages:
            content = msg.get("content", "").lower()
            agent = msg.get("agent_name")
            
            if agent:
                tools_used.add(agent)
            
            # Detect topics
            if any(kw in content for kw in ["crop", "fasal", "plant", "boai"]):
                topics.add("crop_advice")
            if any(kw in content for kw in ["pest", "keera", "disease", "bimari", "insect"]):
                topics.add("pest_management")
            if any(kw in content for kw in ["fertilizer", "khad", "urea", "dap"]):
                topics.add("fertilizer")
            if any(kw in content for kw in ["price", "mandi", "sell", "rate"]):
                topics.add("market_prices")
            if any(kw in content for kw in ["water", "irrigation", "pani", "abpashi"]):
                topics.add("irrigation")
            if any(kw in content for kw in ["profit", "cost", "budget", "munafa"]):
                topics.add("financial_planning")
            if any(kw in content for kw in ["scheme", "subsidy", "kisan card", "loan"]):
                topics.add("government_support")
            
            # Detect crops
            crop_keywords = ["wheat", "cotton", "rice", "maize", "sugarcane", "chickpea", 
                           "lentil", "mustard", "onion", "potato", "tomato", "mungbean"]
            for crop in crop_keywords:
                if crop in content:
                    crops_mentioned.add(crop)
        
        summary_parts = []
        
        if topics:
            summary_parts.append(f"Topics discussed: {', '.join(sorted(topics))}")
        
        if crops_mentioned:
            summary_parts.append(f"Crops mentioned: {', '.join(sorted(crops_mentioned))}")
        
        if tools_used:
            summary_parts.append(f"Specialists consulted: {', '.join(sorted(tools_used))}")
        
        # Last user query
        user_msgs = [m for m in messages if m.get("role") == "user"]
        if user_msgs:
            last_query = user_msgs[-1].get("content", "")[:100]
            summary_parts.append(f"Last query: {last_query}")
        
        self._summary = " | ".join(summary_parts)
        return self._summary
    
    def clear_summary_cache(self):
        """Clear cached summary."""
        self._summary = None
    
    def get_agent_context_summary(self) -> str:
        """Get formatted summary for agent context."""
        return self.build_summary()


def format_messages_for_llm(messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Format session messages for LLM consumption."""
    formatted = []
    
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        agent = msg.get("agent_name")
        
        if role == "assistant" and agent:
            content = f"[{agent}]: {content}"
        
        formatted.append({"role": role, "content": content})
    
    return formatted