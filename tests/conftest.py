"""Test configuration and fixtures."""

import pytest
import asyncio
from config import settings
from models import FarmerProfile, FarmContext, Province, Season, SoilType, WaterAvailability

# Test settings
settings.use_real_apis = False
settings.session_backend = "memory"

@pytest.fixture
def sample_farmer_profile():
    return FarmerProfile(
        farmer_id="test_farmer_001",
        name="Test Farmer",
        district="faisalabad",
        province=Province.PUNJAB,
        preferred_language="en"
    )

@pytest.fixture
def sample_farm_context():
    return FarmContext(
        land_size_acres=5.0,
        soil_type=SoilType.LOAM,
        season=Season.RABI,
        water_availability=WaterAvailability.CANAL,
        current_crop="wheat",
        crop_stage=None
    )

@pytest.fixture
def sample_farm_context_kharif():
    return FarmContext(
        land_size_acres=10.0,
        soil_type=SoilType.CLAY_LOAM,
        season=Season.KHARIF,
        water_availability=WaterAvailability.FULL_IRRIGATION,
        current_crop="cotton",
        crop_stage="flowering"
    )

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()