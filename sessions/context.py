"""Context injection and management."""

from typing import Optional, Dict, Any
from models import FarmerProfile, FarmContext
from sessions.manager import session_manager
import logging

logger = logging.getLogger(__name__)

class ContextManager:
    """Manages typed context injection for agents."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self._cached_profile: Optional[FarmerProfile] = None
        self._cached_context: Optional[FarmContext] = None
    
    def get_profile(self) -> Optional[FarmerProfile]:
        """Get farmer profile from session."""
        if self._cached_profile is None:
            profile, _ = session_manager.get_farmer_context(self.session_id)
            self._cached_profile = profile
        return self._cached_profile
    
    def get_context(self) -> Optional[FarmContext]:
        """Get farm context from session."""
        if self._cached_context is None:
            _, context = session_manager.get_farmer_context(self.session_id)
            self._cached_context = context
        return self._cached_context
    
    def update_profile(self, profile: FarmerProfile):
        """Update farmer profile in session and cache."""
        self._cached_profile = profile
        session_manager.update_session(self.session_id, farmer_profile=profile)
    
    def update_context(self, context: FarmContext):
        """Update farm context in session and cache."""
        self._cached_context = context
        session_manager.update_session(self.session_id, farm_context=context)
    
    def build_agent_context(self) -> Dict[str, Any]:
        """Build context dict for agent injection."""
        profile = self.get_profile()
        context = self.get_context()
        
        ctx = {}
        
        if profile:
            ctx["farmer_id"] = profile.farmer_id
            ctx["farmer_name"] = profile.name
            ctx["district"] = profile.district
            ctx["province"] = profile.province.value
            ctx["preferred_language"] = profile.preferred_language.value
        
        if context:
            ctx["land_size_acres"] = context.land_size_acres
            ctx["soil_type"] = context.soil_type.value
            ctx["season"] = context.season.value
            ctx["water_availability"] = context.water_availability.value
            ctx["current_crop"] = context.current_crop
            ctx["crop_stage"] = context.crop_stage.value if context.crop_stage else None
            ctx["last_irrigation_date"] = context.last_irrigation_date.isoformat() if context.last_irrigation_date else None
            ctx["fertilizer_applied"] = context.fertilizer_applied
        
        return ctx
    
    def format_context_summary(self) -> str:
        """Format context as human-readable summary."""
        profile = self.get_profile()
        context = self.get_context()
        
        parts = []
        
        if profile:
            parts.append(f"Farmer: {profile.name or profile.farmer_id}")
            parts.append(f"Location: {profile.district}, {profile.province.value}")
        
        if context:
            parts.append(f"Land: {context.land_size_acres} acres")
            parts.append(f"Soil: {context.soil_type.value}")
            parts.append(f"Season: {context.season.value}")
            parts.append(f"Water: {context.water_availability.value}")
            
            if context.current_crop:
                parts.append(f"Current crop: {context.current_crop}")
            if context.crop_stage:
                parts.append(f"Crop stage: {context.crop_stage.value}")
        
        return " | ".join(parts) if parts else "No context available"


def create_context_for_agent(session_id: str) -> Dict[str, Any]:
    """Helper to create agent context from session."""
    manager = ContextManager(session_id)
    return manager.build_agent_context()