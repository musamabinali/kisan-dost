"""Fertilizer calculation models."""

from pydantic import BaseModel, Field, computed_field
from typing import Literal, Optional
from enum import Enum

class FertilizerType(str, Enum):
    UREA = "urea"
    DAP = "dap"
    NPK_20_20_20 = "npk_20_20_20"
    NPK_12_32_16 = "npk_12_32_16"
    SSP = "ssp"
    MOP = "mop"
    ZINC_SULFATE = "zinc_sulfate"
    BORON = "boron"

class NPKRequirement(BaseModel):
    nitrogen_kg_per_acre: float = Field(..., ge=0)
    phosphorus_kg_per_acre: float = Field(..., ge=0)
    potassium_kg_per_acre: float = Field(..., ge=0)
    zinc_kg_per_acre: float = 0.0
    boron_kg_per_acre: float = 0.0

class FertilizerBag(BaseModel):
    fertilizer_type: FertilizerType
    bags_needed: float = Field(..., ge=0)
    weight_per_bag_kg: float = Field(default=50, ge=0)
    price_per_bag_pkr: float = Field(..., ge=0)
    
    @computed_field
    @property
    def total_weight_kg(self) -> float:
        return self.bags_needed * self.weight_per_bag_kg
    
    @computed_field
    @property
    def total_cost_pkr(self) -> float:
        return self.bags_needed * self.price_per_bag_pkr

class FertilizerPlan(BaseModel):
    crop: str
    acres: float
    npk_requirement: NPKRequirement
    fertilizer_bags: list[FertilizerBag]
    total_cost_pkr: float
    application_schedule: list[dict]  # [{stage, fertilizer, bags, timing}]
    subsidy_eligible: bool = False
    subsidy_details: Optional[str] = None
    notes: Optional[str] = None
    
    @computed_field
    @property
    def cost_per_acre_pkr(self) -> float:
        return self.total_cost_pkr / self.acres if self.acres > 0 else 0