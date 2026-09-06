"""Tests for function tools."""

import pytest
from tools import (
    crop_advisor, pest_disease_doctor, fertilizer_calculator,
    mandi_price_lookup, irrigation_weather, profit_estimator, govt_support_finder
)
from models import FarmerProfile, FarmContext, Province, Season, SoilType, WaterAvailability

@pytest.fixture
def sample_farmer():
    return FarmerProfile(
        farmer_id="test_001",
        district="faisalabad",
        province=Province.PUNJAB
    )

@pytest.fixture
def sample_context_rabi():
    return FarmContext(
        land_size_acres=5.0,
        soil_type=SoilType.LOAM,
        season=Season.RABI,
        water_availability=WaterAvailability.CANAL
    )

@pytest.fixture
def sample_context_kharif():
    return FarmContext(
        land_size_acres=10.0,
        soil_type=SoilType.CLAY_LOAM,
        season=Season.KHARIF,
        water_availability=WaterAvailability.FULL_IRRIGATION,
        current_crop="cotton",
        crop_stage="flowering"
    )

class TestCropAdvisor:
    @pytest.mark.asyncio
    async def test_crop_advisor_rabi(self, sample_farmer, sample_context_rabi):
        result = await crop_advisor(sample_context_rabi, sample_farmer)
        
        assert result is not None
        assert result.season == "rabi"
        assert result.district == "faisalabad"
        assert len(result.recommendations) > 0
        assert result.primary_recommendation is not None
        assert result.primary_recommendation.crop_name in ["wheat", "chickpea", "lentil", "mustard"]
    
    @pytest.mark.asyncio
    async def test_crop_advisor_kharif(self, sample_farmer, sample_context_kharif):
        result = await crop_advisor(sample_context_kharif, sample_farmer)
        
        assert result.season == "kharif"
        assert result.primary_recommendation.crop_name in ["cotton", "rice", "maize", "sugarcane"]

class TestFertilizerCalculator:
    @pytest.mark.asyncio
    async def test_fertilizer_calculator_wheat(self, sample_farmer):
        result = await fertilizer_calculator("wheat", 5.0)
        
        assert result.crop == "wheat"
        assert result.acres == 5.0
        assert result.total_cost_pkr > 0
        assert len(result.fertilizer_bags) > 0
        assert result.npk_requirement.nitrogen_kg_per_acre > 0
    
    @pytest.mark.asyncio
    async def test_fertilizer_calculator_cotton(self, sample_farmer):
        result = await fertilizer_calculator("cotton", 10.0)
        
        assert result.crop == "cotton"
        assert result.acres == 10.0
        # Cotton needs more fertilizer
        assert result.npk_requirement.nitrogen_kg_per_acre >= 100

class TestPestDoctor:
    @pytest.mark.asyncio
    async def test_pest_whitefly(self, sample_farmer, sample_context_kharif):
        result = await pest_disease_doctor(
            "cotton leaves curling, tiny white insects on underside",
            sample_context_kharif
        )
        
        assert result.pest_name.lower() == "whitefly"
        assert result.confidence > 0.5
        assert result.treatment is not None
    
    @pytest.mark.asyncio
    async def test_pest_aphid(self, sample_farmer, sample_context_kharif):
        result = await pest_disease_doctor(
            "okra leaves curled, sticky honeydew, black sooty mold",
            sample_context_kharif,
            crop_name="okra"
        )
        
        assert result.pest_name.lower() == "aphid"
        assert result.confidence > 0.5

class TestMandiLookup:
    @pytest.mark.asyncio
    async def test_mandi_wheat(self, sample_farmer):
        result = await mandi_price_lookup("wheat", "faisalabad")
        
        assert result["commodity"] == "wheat"
        assert result["district"] == "faisalabad"
        assert len(result["prices"]) > 0
        assert "trends" in result

class TestIrrigationWeather:
    @pytest.mark.asyncio
    async def test_irrigation_wheat(self, sample_farmer, sample_context_rabi):
        result = await irrigation_weather(sample_context_rabi, "faisalabad")
        
        assert result.district == "faisalabad"
        assert len(result.forecast) > 0
        assert result.irrigation_advice is not None

class TestProfitEstimator:
    @pytest.mark.asyncio
    async def test_profit_wheat(self, sample_farmer, sample_context_rabi):
        result = await profit_estimator("wheat", 5.0, sample_context_rabi)
        
        assert result.crop == "wheat"
        assert result.acres == 5.0
        assert result.total_input_cost_pkr > 0
        assert result.expected_revenue_pkr > 0
        assert result.recommendation in ["profitable", "marginal", "loss_risk"]

class TestGovtSupport:
    @pytest.mark.asyncio
    async def test_govt_support_punjab(self, sample_farmer, sample_context_rabi):
        result = await govt_support_finder(sample_farmer, sample_context_rabi)
        
        assert len(result) > 0
        # Should include Kisan Card
        scheme_names = [m.scheme.name for m in result]
        assert any("kisan card" in name.lower() for name in scheme_names)