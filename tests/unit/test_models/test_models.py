"""Tests for Pydantic models."""

import pytest
from models import (
    FarmerProfile, FarmContext, Province, Season, SoilType, 
    WaterAvailability, CropStage, Language,
    CropRecommendation, CropPlan, CropCategory,
    FertilizerPlan, FertilizerBag, NPKRequirement, FertilizerType,
    PestDiagnosis, TreatmentPlan, PesticideSafety, PestType, Severity, TreatmentType,
    MandiPrice, ProfitEstimate,
    WeatherForecast, DailyForecast, IrrigationAdvice, WeatherCondition,
    GovtScheme, SchemeMatch, SchemeType, EligibilityCriteria
)
from datetime import date

class TestFarmerModels:
    def test_farmer_profile_creation(self):
        profile = FarmerProfile(
            farmer_id="test_001",
            name="Test Farmer",
            district="faisalabad",
            province=Province.PUNJAB
        )
        assert profile.farmer_id == "test_001"
        assert profile.province == Province.PUNJAB
        assert profile.preferred_language == Language.ENGLISH
    
    def test_farm_context_validation(self):
        context = FarmContext(
            land_size_acres=5.0,
            soil_type=SoilType.LOAM,
            season=Season.RABI,
            water_availability=WaterAvailability.CANAL
        )
        assert context.land_size_acres == 5.0
        assert context.soil_type == SoilType.LOAM
    
    def test_farm_context_invalid_land_size(self):
        with pytest.raises(ValueError):
            FarmContext(
                land_size_acres=-1,
                soil_type=SoilType.LOAM,
                season=Season.RABI,
                water_availability=WaterAvailability.CANAL
            )
        
        with pytest.raises(ValueError):
            FarmContext(
                land_size_acres=2000,
                soil_type=SoilType.LOAM,
                season=Season.RABI,
                water_availability=WaterAvailability.CANAL
            )

class TestCropModels:
    def test_crop_recommendation(self):
        crop = CropRecommendation(
            crop_name="wheat",
            category=CropCategory.CEREAL,
            expected_yield_kg_per_acre=1200,
            expected_price_pkr_per_40kg=4000,
            water_requirement_mm=450,
            growing_days=130,
            fertilizer_npk_kg_per_acre=(90, 45, 30),
            profit_per_acre_pkr=48000,
            suitability_score=0.85
        )
        assert crop.expected_revenue_per_acre_pkr == 120000.0  # 1200/40 * 4000
    
    def test_crop_recommendation_accepts_365_day_crop(self):
        crop = CropRecommendation(
            crop_name="lucerne",
            category=CropCategory.FODDER,
            expected_yield_kg_per_acre=12000,
            expected_price_pkr_per_40kg=1500,
            water_requirement_mm=800,
            growing_days=365,
            fertilizer_npk_kg_per_acre=(50, 30, 30),
            profit_per_acre_pkr=130000,
            suitability_score=0.82
        )
        assert crop.growing_days == 365

    def test_crop_plan(self):
        crop_rec = CropRecommendation(
            crop_name="wheat",
            category=CropCategory.CEREAL,
            expected_yield_kg_per_acre=1200,
            expected_price_pkr_per_40kg=4000,
            water_requirement_mm=450,
            growing_days=130,
            fertilizer_npk_kg_per_acre=(90, 45, 30),
            profit_per_acre_pkr=48000,
            suitability_score=0.85
        )
        
        plan = CropPlan(
            district="faisalabad",
            season="rabi",
            recommendations=[crop_rec],
            primary_recommendation=crop_rec,
            reasoning="Best match for conditions"
        )
        assert plan.primary_recommendation.crop_name == "wheat"

class TestFertilizerModels:
    def test_npk_requirement(self):
        npk = NPKRequirement(
            nitrogen_kg_per_acre=90,
            phosphorus_kg_per_acre=45,
            potassium_kg_per_acre=30
        )
        assert npk.nitrogen_kg_per_acre == 90
    
    def test_fertilizer_bag(self):
        bag = FertilizerBag(
            fertilizer_type=FertilizerType.DAP,
            bags_needed=2.0,
            price_per_bag_pkr=11500
        )
        assert bag.total_weight_kg == 100.0
        assert bag.total_cost_pkr == 23000.0
    
    def test_fertilizer_plan(self):
        npk = NPKRequirement(nitrogen_kg_per_acre=90, phosphorus_kg_per_acre=45, potassium_kg_per_acre=30)
        bags = [
            FertilizerBag(fertilizer_type=FertilizerType.DAP, bags_needed=2.0, price_per_bag_pkr=11500),
            FertilizerBag(fertilizer_type=FertilizerType.UREA, bags_needed=3.0, price_per_bag_pkr=3000)
        ]
        
        plan = FertilizerPlan(
            crop="wheat",
            acres=5.0,
            npk_requirement=npk,
            fertilizer_bags=bags,
            total_cost_pkr=125000,
            application_schedule=[]
        )
        assert plan.cost_per_acre_pkr == 25000.0

class TestPestModels:
    def test_pesticide_safety(self):
        safety = PesticideSafety(
            max_dosage_ml_per_acre=200,
            pre_harvest_interval_days=14,
            re_entry_interval_hours=12,
            protective_equipment=["mask", "gloves", "goggles"]
        )
        assert safety.max_dosage_ml_per_acre == 200
    
    def test_treatment_plan_dosage_validation(self):
        safety = PesticideSafety(
            max_dosage_ml_per_acre=200,
            pre_harvest_interval_days=14,
            re_entry_interval_hours=12
        )
        
        # Valid dosage
        treatment = TreatmentPlan(
            treatment_type=TreatmentType.CHEMICAL,
            pesticide_name="Imidacloprid",
            dosage_ml_per_acre=100,
            application_method="spray",
            timing="Early morning",
            frequency="14 days",
            safety=safety,
            cost_per_acre_pkr=400
        )
        assert treatment.dosage_ml_per_acre == 100
        
        # Invalid dosage - should raise error
        with pytest.raises(ValueError):
            TreatmentPlan(
                treatment_type=TreatmentType.CHEMICAL,
                pesticide_name="Imidacloprid",
                dosage_ml_per_acre=300,  # Exceeds max 200
                application_method="spray",
                timing="Early morning",
                frequency="14 days",
                safety=safety,
                cost_per_acre_pkr=400
            )
    
    def test_pest_diagnosis(self):
        safety = PesticideSafety(
            max_dosage_ml_per_acre=200,
            pre_harvest_interval_days=14,
            re_entry_interval_hours=12
        )
        treatment = TreatmentPlan(
            treatment_type=TreatmentType.CHEMICAL,
            pesticide_name="Imidacloprid",
            dosage_ml_per_acre=100,
            application_method="spray",
            timing="Early morning",
            frequency="14 days",
            safety=safety,
            cost_per_acre_pkr=400
        )
        
        diagnosis = PestDiagnosis(
            pest_name="Whitefly",
            pest_type=PestType.INSECT,
            confidence=0.9,
            symptoms_matched=["leaves curling", "white insects"],
            affected_crops=["cotton"],
            severity=Severity.MODERATE,
            treatment=treatment,
            preventive_measures=["Yellow sticky traps"]
        )
        assert diagnosis.pest_name == "Whitefly"
        assert diagnosis.confidence == 0.9

class TestMarketModels:
    def test_mandi_price(self):
        price = MandiPrice(
            commodity="wheat",
            mandi_name="faisalabad_grain_market",
            district="faisalabad",
            province="punjab",
            min_price_pkr_per_40kg=3800,
            max_price_pkr_per_40kg=4100,
            modal_price_pkr_per_40kg=3950,
            date=date.today()
        )
        assert price.commodity == "wheat"
    
    def test_profit_estimate(self):
        estimate = ProfitEstimate(
            crop="wheat",
            acres=5.0,
            input_costs={"seed": 3000, "fertilizer": 8000},
            total_input_cost_pkr=55000,
            expected_yield_kg=6000,
            expected_price_pkr_per_40kg=4000,
            expected_revenue_pkr=600000,
            net_profit_pkr=545000,
            profit_margin_percent=90.8,
            break_even_yield_kg_per_acre=550,
            break_even_price_pkr_per_40kg=1100,
            sensitivity_analysis={},
            risk_factors=[],
            recommendation="profitable"
        )
        assert estimate.recommendation == "profitable"

class TestWeatherModels:
    def test_daily_forecast(self):
        forecast = DailyForecast(
            date=date.today(),
            temp_max_c=35.0,
            temp_min_c=20.0,
            humidity_percent=60,
            precipitation_mm=0.0,
            wind_speed_kmh=10.0,
            condition=WeatherCondition.CLEAR
        )
        assert forecast.condition == WeatherCondition.CLEAR
    
    def test_irrigation_advice(self):
        advice = IrrigationAdvice(
            should_irrigate=True,
            reason="Net need 15mm",
            water_amount_mm=15.0,
            method="furrow",
            urgency="medium",
            crop_stage_context="wheat at vegetative"
        )
        assert advice.should_irrigate is True

class TestGovernmentModels:
    def test_eligibility_criteria(self):
        criteria = EligibilityCriteria(
            min_land_acres=0.5,
            max_land_acres=50.0,
            required_crops=["wheat", "cotton"],
            farmer_categories=["small", "medium"],
            documents_required=["CNIC", "Land record"]
        )
        assert criteria.min_land_acres == 0.5
    
    def test_govt_scheme(self):
        scheme = GovtScheme(
            scheme_id="kisan_card_punjab",
            name="Kisan Card Punjab",
            scheme_type=SchemeType.KISAN_CARD,
            province="punjab",
            department="Agriculture Department Punjab",
            description="Smart card for subsidies",
            benefits=["Fertilizer subsidy", "Seed subsidy"],
            eligibility=EligibilityCriteria(min_land_acres=0.5),
            application_method="both"
        )
        assert scheme.scheme_type == SchemeType.KISAN_CARD