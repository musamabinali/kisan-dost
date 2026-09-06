"""Market price and profit estimation models."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date
from enum import Enum

class MandiPrice(BaseModel):
    commodity: str
    mandi_name: str
    district: str
    province: str
    min_price_pkr_per_40kg: float = Field(..., ge=0)
    max_price_pkr_per_40kg: float = Field(..., ge=0)
    modal_price_pkr_per_40kg: float = Field(..., ge=0)
    date: date
    arrivals_tonnes: Optional[float] = None
    source: Literal["amis", "mock", "farmer_report"] = "mock"

class PriceTrend(BaseModel):
    commodity: str
    mandi_name: str
    trend_7d: Literal["rising", "falling", "stable"]
    change_percent_7d: float
    trend_30d: Literal["rising", "falling", "stable"]
    change_percent_30d: float
    best_sell_window: Optional[str] = None

class ProfitEstimate(BaseModel):
    crop: str
    acres: float
    input_costs: dict[str, float]  # seeds, fertilizer, pesticide, labor, irrigation, rent
    total_input_cost_pkr: float
    expected_yield_kg: float
    expected_price_pkr_per_40kg: float
    expected_revenue_pkr: float
    net_profit_pkr: float
    profit_margin_percent: float
    break_even_yield_kg_per_acre: float
    break_even_price_pkr_per_40kg: float
    sensitivity_analysis: dict[str, float]  # profit at ±10% yield/price
    risk_factors: list[str]
    recommendation: Literal["profitable", "marginal", "loss_risk"]