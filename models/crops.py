"""Crop recommendation and plan models."""

from pydantic import BaseModel, Field, computed_field
from typing import Optional, Literal
from enum import Enum

class CropCategory(str, Enum):
    CEREAL = "cereal"
    PULSE = "pulse"
    OILSEED = "oilseed"
    CASH_CROP = "cash_crop"
    VEGETABLE = "vegetable"
    FODDER = "fodder"

class CropRecommendation(BaseModel):
    crop_name: str
    category: CropCategory
    expected_yield_kg_per_acre: float = Field(..., ge=0)
    expected_price_pkr_per_40kg: float = Field(..., ge=0)
    water_requirement_mm: float = Field(..., ge=0)
    growing_days: int = Field(..., ge=30, le=300)
    fertilizer_npk_kg_per_acre: tuple[float, float, float]  # N, P, K
    profit_per_acre_pkr: float
    suitability_score: float = Field(..., ge=0, le=1)
    risk_factors: list[str] = Field(default_factory=list)
    notes: Optional[str] = None

    @computed_field
    @property
    def expected_revenue_per_acre_pkr(self) -> float:
        return (self.expected_yield_kg_per_acre / 40) * self.expected_price_pkr_per_40kg

class CropPlan(BaseModel):
    district: str
    season: str
    recommendations: list[CropRecommendation] = Field(..., min_length=1, max_length=5)
    primary_recommendation: CropRecommendation
    alternative_crops: list[CropRecommendation] = Field(default_factory=list)
    reasoning: str
    data_source: Literal["mock", "kaggle", "faostat", "hybrid"] = "mock"