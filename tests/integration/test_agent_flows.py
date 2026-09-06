"""Integration tests for agent flows."""

import pytest
from agents.memory.sqlite_session import SQLiteSession
from specialists import Runner
from specialists import triage_agent
from models import FarmerProfile, FarmContext, Province, Season, SoilType, WaterAvailability
from sessions import session_manager, ContextManager

@pytest.fixture
def sample_farmer():
    return FarmerProfile(
        farmer_id="integration_test_001",
        district="faisalabad",
        province=Province.PUNJAB
    )

@pytest.fixture
def sample_context():
    return FarmContext(
        land_size_acres=5.0,
        soil_type=SoilType.LOAM,
        season=Season.RABI,
        water_availability=WaterAvailability.CANAL
    )

@pytest.fixture
def session_with_context(sample_farmer, sample_context):
    session_id = session_manager.create_session(
        farmer_id=sample_farmer.farmer_id,
        farmer_profile=sample_farmer,
        farm_context=sample_context
    )
    yield session_id
    # Cleanup - not needed for memory backend

class TestAgentFlows:
    @pytest.mark.asyncio
    async def test_crop_advice_flow(self, session_with_context, sample_farmer, sample_context):
        ctx_manager = ContextManager(session_with_context)
        agent_context = ctx_manager.build_agent_context()
        
        session_obj = SQLiteSession(session_id=session_with_context, db_path='data/sessions.db')
        result = await Runner.run(
            triage_agent,
            "What should I plant this Rabi season on 5 acres in Faisalabad?",
            context=agent_context,
            session=session_obj,
        )
        
        assert result.final_output is not None
        assert len(result.final_output) > 0
        # Should mention crops
        output_lower = result.final_output.lower()
        assert any(crop in output_lower for crop in ["wheat", "chickpea", "lentil", "mustard"])
    
    @pytest.mark.asyncio
    async def test_pest_diagnosis_flow(self, session_with_context):
        # Update context to have cotton
        ctx_manager = ContextManager(session_with_context)
        ctx_manager.update_context(FarmContext(
            land_size_acres=10.0,
            soil_type=SoilType.CLAY_LOAM,
            season=Season.KHARIF,
            water_availability=WaterAvailability.FULL_IRRIGATION,
            current_crop="cotton",
            crop_stage="flowering"
        ))
        agent_context = ctx_manager.build_agent_context()
        
        session_obj = SQLiteSession(session_id=session_with_context, db_path='data/sessions.db')
        result = await Runner.run(
            triage_agent,
            "My cotton leaves are curling and I see tiny white insects",
            context=agent_context,
            session=session_obj,
        )
        
        assert result.final_output is not None
        output_lower = result.final_output.lower()
        assert "whitefly" in output_lower or "سفید مکھی" in output_lower
    
    @pytest.mark.asyncio
    async def test_fertilizer_flow(self, session_with_context):
        ctx_manager = ContextManager(session_with_context)
        agent_context = ctx_manager.build_agent_context()
        
        session_obj = SQLiteSession(session_id=session_with_context, db_path='data/sessions.db')
        result = await Runner.run(
            triage_agent,
            "How much Urea and DAP for 5 acres of wheat?",
            context=agent_context,
            session=session_obj,
        )
        
        assert result.final_output is not None
        output_lower = result.final_output.lower()
        assert "urea" in output_lower or "یوریا" in output_lower
        assert "dap" in output_lower or "ڈی اے پی" in output_lower
    
    @pytest.mark.asyncio
    async def test_session_memory(self, session_with_context):
        ctx_manager = ContextManager(session_with_context)
        agent_context = ctx_manager.build_agent_context()
        
        # First query
session_obj = SQLiteSession(session_id=session_with_context, db_path='data/sessions.db')
        await Runner.run(
            triage_agent,
            "What's the wheat price in Faisalabad?",
            context=agent_context,
            session=session_obj,
        )

        # Second query - should remember context
        result = await Runner.run(
            triage_agent,
            "And what about cotton price?",
            context=agent_context,
            session=session_obj,
        )
        
        assert result.final_output is not None
        # Should know we're in Faisalabad without repeating
        output_lower = result.final_output.lower()
        assert "cotton" in output_lower

class TestSessionPersistence:
    @pytest.mark.asyncio
    async def test_session_restores_context(self, sample_farmer, sample_context):
        # Create session
        session_id = session_manager.create_session(
            farmer_id=sample_farmer.farmer_id,
            farmer_profile=sample_farmer,
            farm_context=sample_context
        )
        
        # Create new context manager (simulating restart)
        ctx_manager = ContextManager(session_id)
        profile = ctx_manager.get_profile()
        context = ctx_manager.get_context()
        
        assert profile is not None
        assert profile.farmer_id == sample_farmer.farmer_id
        assert profile.district == "faisalabad"
        
        assert context is not None
        assert context.land_size_acres == 5.0
        assert context.soil_type == SoilType.LOAM