"""Profit Estimator Tool."""

from agents import function_tool
from models import ProfitEstimate, FarmContext
from data import crop_loader, mandi_loader
from config.constants import CROP_NPK_REQUIREMENTS, DEFAULT_FERTILIZER_PRICES
from tools.fertilizer_calculator import fertilizer_calculator
import logging
from typing import Optional, Literal

logger = logging.getLogger(__name__)

# Typical input costs per acre (PKR) - baseline for major crops
BASE_COSTS_PER_ACRE = {
    "wheat": {"seed": 3000, "fertilizer": 8000, "pesticide": 2000, "labor": 6000, "irrigation": 3000, "rent": 10000, "transport": 1500},
    "cotton": {"seed": 5000, "fertilizer": 12000, "pesticide": 15000, "labor": 15000, "irrigation": 5000, "rent": 15000, "transport": 3000},
    "rice": {"seed": 4000, "fertilizer": 9000, "pesticide": 3000, "labor": 12000, "irrigation": 8000, "rent": 12000, "transport": 2000},
    "maize": {"seed": 3500, "fertilizer": 10000, "pesticide": 2500, "labor": 8000, "irrigation": 4000, "rent": 10000, "transport": 2000},
    "sugarcane": {"seed": 8000, "fertilizer": 20000, "pesticide": 5000, "labor": 25000, "irrigation": 15000, "rent": 20000, "transport": 5000},
    "chickpea": {"seed": 2500, "fertilizer": 4000, "pesticide": 1500, "labor": 5000, "irrigation": 2000, "rent": 8000, "transport": 1000},
    "lentil": {"seed": 2000, "fertilizer": 3500, "pesticide": 1000, "labor": 4000, "irrigation": 1500, "rent": 7000, "transport": 800},
    "mustard": {"seed": 1500, "fertilizer": 5000, "pesticide": 2000, "labor": 5000, "irrigation": 2500, "rent": 8000, "transport": 1000},
    "groundnut": {"seed": 6000, "fertilizer": 6000, "pesticide": 3000, "labor": 8000, "irrigation": 3000, "rent": 10000, "transport": 1500},
    "sesame": {"seed": 2000, "fertilizer": 4000, "pesticide": 1500, "labor": 5000, "irrigation": 2000, "rent": 8000, "transport": 800},
    "sunflower": {"seed": 3000, "fertilizer": 7000, "pesticide": 2500, "labor": 6000, "irrigation": 3000, "rent": 10000, "transport": 1200},
    "potato": {"seed": 25000, "fertilizer": 15000, "pesticide": 8000, "labor": 20000, "irrigation": 8000, "rent": 15000, "transport": 5000},
    "onion": {"seed": 8000, "fertilizer": 10000, "pesticide": 5000, "labor": 15000, "irrigation": 6000, "rent": 12000, "transport": 3000},
    "tomato": {"seed": 5000, "fertilizer": 12000, "pesticide": 10000, "labor": 20000, "irrigation": 8000, "rent": 15000, "transport": 5000},
    "mungbean": {"seed": 2500, "fertilizer": 3500, "pesticide": 2000, "labor": 5000, "irrigation": 2000, "rent": 8000, "transport": 1000},
    "fodder_maize": {"seed": 2000, "fertilizer": 5000, "pesticide": 1000, "labor": 4000, "irrigation": 3000, "rent": 8000, "transport": 500},
}

@function_tool(strict_mode=False)
async def profit_estimator(
    crop: str,
    acres: float,
    farm_context: FarmContext,
    expected_yield_kg_per_acre: float | None = None,
    expected_price_pkr_per_40kg: float | None = None
) -> ProfitEstimate:
    """
    Full season budget: input costs vs expected revenue, giving net margin and break-even yield.
    
    Args:
        crop: Crop name
        acres: Land size in acres
        farm_context: Farm context for cost adjustments
        expected_yield_kg_per_acre: Override expected yield
        expected_price_pkr_per_40kg: Override expected price
        
    Returns:
        ProfitEstimate with detailed breakdown, margin, break-even, and sensitivity.
    """
    try:
        crop_lower = crop.lower().strip()
        
        # Get expected yield and price
        if expected_yield_kg_per_acre is None or expected_price_pkr_per_40kg is None:
            crop_data = crop_loader.get_crop_requirements(crop_lower)
            if crop_data:
                expected_yield_kg_per_acre = expected_yield_kg_per_acre or crop_data.get("yield_kg_per_acre", 1000)
                expected_price_pkr_per_40kg = expected_price_pkr_per_40kg or crop_data.get("price_pkr_per_40kg", 3000)
            else:
                expected_yield_kg_per_acre = expected_yield_kg_per_acre or 1000
                expected_price_pkr_per_40kg = expected_price_pkr_per_40kg or 3000
        
        # Get base costs
        base_costs = BASE_COSTS_PER_ACRE.get(crop_lower, BASE_COSTS_PER_ACRE["wheat"])
        
        # Adjust costs based on context
        costs = _adjust_costs(base_costs, farm_context, crop_lower, acres)
        
        # Calculate fertilizer cost using calculator
        fert_plan = await fertilizer_calculator(crop_lower, acres)
        costs["fertilizer"] = fert_plan.cost_per_acre_pkr
        
        total_input_cost_per_acre = sum(costs.values())
        total_input_cost = total_input_cost_per_acre * acres
        
        # Revenue
        expected_yield_total = expected_yield_kg_per_acre * acres
        expected_revenue = (expected_yield_total / 40) * expected_price_pkr_per_40kg
        
        # Profit
        net_profit = expected_revenue - total_input_cost
        profit_margin = (net_profit / expected_revenue * 100) if expected_revenue > 0 else 0
        
        # Break-even
        break_even_yield = (total_input_cost_per_acre / expected_price_pkr_per_40kg) * 40
        break_even_price = (total_input_cost_per_acre / expected_yield_kg_per_acre) * 40
        
        # Sensitivity analysis
        sensitivity = {
            "yield_plus_10%": round((expected_yield_kg_per_acre * 1.1 / 40 * expected_price_pkr_per_40kg - total_input_cost_per_acre) / acres, 0),
            "yield_minus_10%": round((expected_yield_kg_per_acre * 0.9 / 40 * expected_price_pkr_per_40kg - total_input_cost_per_acre) / acres, 0),
            "price_plus_10%": round((expected_yield_kg_per_acre / 40 * expected_price_pkr_per_40kg * 1.1 - total_input_cost_per_acre) / acres, 0),
            "price_minus_10%": round((expected_yield_kg_per_acre / 40 * expected_price_pkr_per_40kg * 0.9 - total_input_cost_per_acre) / acres, 0),
            "both_plus_10%": round((expected_yield_kg_per_acre * 1.1 / 40 * expected_price_pkr_per_40kg * 1.1 - total_input_cost_per_acre) / acres, 0),
            "both_minus_10%": round((expected_yield_kg_per_acre * 0.9 / 40 * expected_price_pkr_per_40kg * 0.9 - total_input_cost_per_acre) / acres, 0),
        }
        
        # Risk factors
        risks = _get_risk_factors(crop_lower, farm_context, expected_yield_kg_per_acre, expected_price_pkr_per_40kg)
        
        # Recommendation
        if profit_margin > 20:
            recommendation = "profitable"
        elif profit_margin > 5:
            recommendation = "marginal"
        else:
            recommendation = "loss_risk"
        
        return ProfitEstimate(
            crop=crop_lower,
            acres=acres,
            input_costs=costs,
            total_input_cost_pkr=round(total_input_cost, 0),
            expected_yield_kg=round(expected_yield_total, 0),
            expected_price_pkr_per_40kg=round(expected_price_pkr_per_40kg, 0),
            expected_revenue_pkr=round(expected_revenue, 0),
            net_profit_pkr=round(net_profit, 0),
            profit_margin_percent=round(profit_margin, 1),
            break_even_yield_kg_per_acre=round(break_even_yield, 1),
            break_even_price_pkr_per_40kg=round(break_even_price, 1),
            sensitivity_analysis=sensitivity,
            risk_factors=risks,
            recommendation=recommendation
        )
        
    except Exception as e:
        logger.error(f"Profit estimator error: {e}")
        return _error_profit(crop, acres, str(e))

def _adjust_costs(base_costs: dict, ctx: FarmContext, crop: str, acres: float) -> dict:
    """Adjust base costs based on farm context."""
    costs = base_costs.copy()
    
    # Adjust for land size (economies of scale)
    if acres > 50:
        scale_factor = 0.9
    elif acres > 25:
        scale_factor = 0.95
    elif acres < 5:
        scale_factor = 1.1
    else:
        scale_factor = 1.0
    
    # Apply to variable costs
    for key in ["labor", "transport", "pesticide"]:
        costs[key] = round(costs[key] * scale_factor)
    
    # Adjust irrigation cost based on water availability
    irrigation_factor = {
        "rainfed": 0.1,
        "limited_irrigation": 0.6,
        "full_irrigation": 1.0,
        "canal": 0.8,
        "tubewell": 1.2,  # Diesel/electricity cost
    }
    costs["irrigation"] = round(costs["irrigation"] * irrigation_factor.get(ctx.water_availability.value, 1.0))
    
    # Adjust rent based on soil quality
    soil_factor = {"clay": 1.0, "loam": 1.0, "clay_loam": 1.05, "sandy_loam": 0.95, "sandy": 0.85, "silt": 0.9}
    costs["rent"] = round(costs["rent"] * soil_factor.get(ctx.soil_type.value, 1.0))
    
    return costs

def _get_risk_factors(crop: str, ctx: FarmContext, yield_est: float, price_est: float) -> list[str]:
    """Identify key risk factors."""
    risks = []
    
    if ctx.water_availability.value == "rainfed" and crop in ["rice", "sugarcane", "cotton"]:
        risks.append(f"Rainfed {crop} - high yield risk in dry spell")
    
    if ctx.soil_type.value == "sandy" and crop in ["rice", "wheat"]:
        risks.append("Sandy soil - low water/nutrient holding capacity")
    
    if crop == "cotton":
        risks.append("Pink bollworm risk - budget for 2-3 sprays")
    
    if crop in ["wheat", "rice"] and price_est < 3500:
        risks.append("Price below support level - market risk")
    
    if ctx.land_size_acres < 5:
        risks.append("Small holding - limited economies of scale")
    
    if ctx.season.value == "kharif" and crop == "cotton":
        risks.append("Monsoon timing critical - late rain affects quality")
    
    return risks

def _error_profit(crop: str, acres: float, error: str) -> ProfitEstimate:
    return ProfitEstimate(
        crop=crop, acres=acres,
        input_costs={}, total_input_cost_pkr=0,
        expected_yield_kg=0, expected_price_pkr_per_40kg=0,
        expected_revenue_pkr=0, net_profit_pkr=0,
        profit_margin_percent=0, break_even_yield_kg_per_acre=0,
        break_even_price_pkr_per_40kg=0,
        sensitivity_analysis={}, risk_factors=[f"Error: {error}"],
        recommendation="loss_risk"
    )