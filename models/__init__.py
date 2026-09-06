"""Models package initialization."""

from .farmer import (
    FarmerProfile, FarmContext, Province, Season, SoilType,
    WaterAvailability, CropStage, Language
)
from .crops import CropRecommendation, CropPlan, CropCategory
from .fertilizers import FertilizerPlan, FertilizerBag, NPKRequirement, FertilizerType
from .pests import PestDiagnosis, TreatmentPlan, PesticideSafety, PestType, Severity, TreatmentType
from .market import MandiPrice, PriceTrend, ProfitEstimate
from .weather import WeatherForecast, DailyForecast, IrrigationAdvice, WeatherCondition
from .government import GovtScheme, SchemeMatch, SchemeType, EligibilityCriteria
from .common import IntentType, AgentName, BaseResponse, ErrorResponse, ValidationError

__all__ = [
    # Farmer
    "FarmerProfile", "FarmContext", "Province", "Season", "SoilType",
    "WaterAvailability", "CropStage", "Language",
    # Crops
    "CropRecommendation", "CropPlan", "CropCategory",
    # Fertilizers
    "FertilizerPlan", "FertilizerBag", "NPKRequirement", "FertilizerType",
    # Pests
    "PestDiagnosis", "TreatmentPlan", "PesticideSafety", "PestType", "Severity", "TreatmentType",
    # Market
    "MandiPrice", "PriceTrend", "ProfitEstimate",
    # Weather
    "WeatherForecast", "DailyForecast", "IrrigationAdvice", "WeatherCondition",
    # Government
    "GovtScheme", "SchemeMatch", "SchemeType", "EligibilityCriteria",
    # Common
    "IntentType", "AgentName", "BaseResponse", "ErrorResponse", "ValidationError",
]