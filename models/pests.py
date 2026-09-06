"""Pest and disease diagnosis models."""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from enum import Enum

class PestType(str, Enum):
    INSECT = "insect"
    DISEASE = "disease"
    WEED = "weed"
    NEMATODE = "nematode"
    RODENT = "rodent"

class Severity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class TreatmentType(str, Enum):
    CHEMICAL = "chemical"
    BIOLOGICAL = "biological"
    CULTURAL = "cultural"
    MECHANICAL = "mechanical"
    IPM = "ipm"

class PesticideSafety(BaseModel):
    """Safety constraints for pesticide application."""
    max_dosage_ml_per_acre: float = Field(..., gt=0)
    pre_harvest_interval_days: int = Field(..., ge=0)
    re_entry_interval_hours: int = Field(..., ge=0)
    banned_for_crops: list[str] = Field(default_factory=list)
    protective_equipment: list[str] = Field(default_factory=list)
    bee_toxicity: Literal["low", "moderate", "high"] = "moderate"
    aquatic_toxicity: Literal["low", "moderate", "high"] = "moderate"

class TreatmentPlan(BaseModel):
    treatment_type: TreatmentType
    pesticide_name: Optional[str] = None
    active_ingredient: Optional[str] = None
    dosage_ml_per_acre: float = Field(..., ge=0)
    application_method: Literal["spray", "soil_drench", "seed_treatment", "broadcast"]
    timing: str
    frequency: str
    safety: PesticideSafety
    cost_per_acre_pkr: float = Field(..., ge=0)
    alternatives: list["TreatmentPlan"] = Field(default_factory=list)
    
    @field_validator("dosage_ml_per_acre")
    @classmethod
    def validate_safe_dosage(cls, v: float, info) -> float:
        if info.data.get("safety") and v > info.data["safety"].max_dosage_ml_per_acre:
            raise ValueError(f"Dosage {v} ml/acre exceeds safe limit")
        return v

class PestDiagnosis(BaseModel):
    pest_name: str
    pest_type: PestType
    scientific_name: Optional[str] = None
    confidence: float = Field(..., ge=0, le=1)
    symptoms_matched: list[str]
    affected_crops: list[str]
    severity: Severity
    treatment: TreatmentPlan
    preventive_measures: list[str]
    economic_threshold: Optional[str] = None
    urdu_name: Optional[str] = None