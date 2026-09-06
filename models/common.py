"""Common base models, enums, and validators."""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from enum import Enum
from datetime import datetime

class IntentType(str, Enum):
    CROP_ADVICE = "crop_advice"
    PEST_DIAGNOSIS = "pest_diagnosis"
    FERTILIZER_CALC = "fertilizer_calc"
    MANDI_PRICE = "mandi_price"
    IRRIGATION_WEATHER = "irrigation_weather"
    PROFIT_ESTIMATE = "profit_estimate"
    GOVT_SCHEME = "govt_scheme"
    GENERAL_CHAT = "general_chat"
    OFF_TOPIC = "off_topic"
    UNSAFE = "unsafe"

class AgentName(str, Enum):
    TRIAGE = "triage"
    AGRONOMY = "agronomy"
    PEST_DOCTOR = "pest_doctor"
    MARKET_FINANCE = "market_finance"

class BaseResponse(BaseModel):
    """Base response model for all tools."""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    tool_name: str

class ErrorResponse(BaseResponse):
    success: bool = False
    error_code: str
    error_details: Optional[str] = None

class ValidationError(BaseModel):
    field: str
    message: str
    value: Optional[str] = None

# Safety validators
def validate_pesticide_dosage(dosage_ml_per_acre: float, pesticide: str, max_limit: float) -> float:
    """Validate pesticide dosage against safety limits."""
    if dosage_ml_per_acre > max_limit:
        raise ValueError(f"Dosage {dosage_ml_per_acre} ml/acre exceeds safe limit of {max_limit} for {pesticide}")
    if dosage_ml_per_acre <= 0:
        raise ValueError("Dosage must be positive")
    return dosage_ml_per_acre

def validate_crop_name(crop: str, valid_crops: list[str]) -> str:
    """Validate crop name against known crops."""
    crop_lower = crop.lower().strip()
    if crop_lower not in [c.lower() for c in valid_crops]:
        raise ValueError(f"Unknown crop: {crop}. Valid crops: {', '.join(valid_crops[:10])}...")
    return crop_lower

def validate_district(district: str, valid_districts: list[str]) -> str:
    """Validate district name."""
    district_lower = district.lower().strip()
    if district_lower not in [d.lower() for d in valid_districts]:
        raise ValueError(f"Unknown district: {district}")
    return district_lower