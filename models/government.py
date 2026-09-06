"""Government scheme models."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date
from enum import Enum

class SchemeType(str, Enum):
    KISAN_CARD = "kisan_card"
    FERTILIZER_SUBSIDY = "fertilizer_subsidy"
    AGRI_LOAN = "agri_loan"
    CROP_INSURANCE = "crop_insurance"
    SEED_SUBSIDY = "seed_subsidy"
    MACHINERY_SUBSIDY = "machinery_subsidy"
    SOLAR_TUBEWELL = "solar_tubewell"
    TRAINING = "training"

class EligibilityCriteria(BaseModel):
    min_land_acres: Optional[float] = None
    max_land_acres: Optional[float] = None
    required_crops: list[str] = Field(default_factory=list)
    provinces: list[str] = Field(default_factory=list)
    districts: list[str] = Field(default_factory=list)
    farmer_categories: list[str] = Field(default_factory=list)
    documents_required: list[str] = Field(default_factory=list)

class GovtScheme(BaseModel):
    scheme_id: str
    name: str
    name_urdu: Optional[str] = None
    scheme_type: SchemeType
    province: str
    department: str
    description: str
    benefits: list[str]
    eligibility: EligibilityCriteria
    application_deadline: Optional[date] = None
    application_method: Literal["online", "offline", "both"] = "both"
    application_url: Optional[str] = None
    contact_info: Optional[str] = None
    is_active: bool = True
    last_updated: date = Field(default_factory=date.today)

class SchemeMatch(BaseModel):
    scheme: GovtScheme
    match_score: float = Field(..., ge=0, le=1)
    matched_criteria: list[str]
    missing_criteria: list[str]
    next_steps: list[str]