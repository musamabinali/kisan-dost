"""Farmer profile and farm context models."""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from datetime import date
from enum import Enum

class Province(str, Enum):
    PUNJAB = "punjab"
    SINDH = "sindh"
    KPK = "kpk"
    BALOCHISTAN = "balochistan"
    GB = "gilgit_baltistan"
    AJK = "azad_kashmir"

class Season(str, Enum):
    RABI = "rabi"       # Oct-Mar
    KHARIF = "kharif"   # Apr-Sep
    ZAID = "zaid"       # Mar-Jun (summer)

class SoilType(str, Enum):
    CLAY = "clay"
    LOAM = "loam"
    SANDY = "sandy"
    SILT = "silt"
    CLAY_LOAM = "clay_loam"
    SANDY_LOAM = "sandy_loam"

class WaterAvailability(str, Enum):
    RAINFED = "rainfed"
    LIMITED_IRRIGATION = "limited_irrigation"
    FULL_IRRIGATION = "full_irrigation"
    CANAL = "canal"
    TUBEWELL = "tubewell"

class CropStage(str, Enum):
    SOWING = "sowing"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    GRAIN_FILL = "grain_fill"
    HARVEST = "harvest"

class Language(str, Enum):
    ENGLISH = "en"
    URDU = "ur"
    ROMAN_URDU = "roman_ur"

class FarmerProfile(BaseModel):
    """Persistent farmer identity across sessions."""
    farmer_id: str = Field(..., description="Unique identifier (phone/hash)")
    name: Optional[str] = None
    district: str = Field(..., description="Pakistan district name")
    province: Province
    preferred_language: Language = Language.ENGLISH
    created_at: date = Field(default_factory=date.today)
    total_queries: int = 0

class FarmContext(BaseModel):
    """Current farming context for this session."""
    land_size_acres: float = Field(..., gt=0, le=1000)
    soil_type: SoilType
    season: Season
    water_availability: WaterAvailability
    current_crop: Optional[str] = None
    crop_stage: Optional[CropStage] = None
    last_irrigation_date: Optional[date] = None
    fertilizer_applied: bool = False
    
    @field_validator("land_size_acres")
    @classmethod
    def validate_land_size(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Land size must be positive")
        if v > 1000:
            raise ValueError("Land size exceeds reasonable limit for smallholder")
        return round(v, 2)