"""Crop Advisor Tool."""

from agents import function_tool
from models import CropPlan, FarmContext, FarmerProfile
from data import crop_loader
from config.constants import CROP_WATER_REQUIREMENTS
from config.prompts.urdu_prompts import (
    SEASON_URDU_NAMES, SOIL_URDU_NAMES, WATER_URDU_NAMES
)
import logging

logger = logging.getLogger(__name__)

# Water availability to mm mapping
WATER_AVAILABILITY_MM = {
    "rainfed": 300,
    "limited_irrigation": 450,
    "full_irrigation": 800,
    "canal": 600,
    "tubewell": 700,
}

# Soil compatibility matrix
SOIL_COMPATIBILITY = {
    "wheat": {"clay_loam": 1.0, "loam": 0.9, "clay": 0.8, "sandy_loam": 0.7, "sandy": 0.5, "silt": 0.6},
    "cotton": {"loam": 1.0, "sandy_loam": 0.9, "clay_loam": 0.8, "clay": 0.6, "sandy": 0.5, "silt": 0.7},
    "rice": {"clay": 1.0, "clay_loam": 0.9, "silt": 0.8, "loam": 0.6, "sandy_loam": 0.4, "sandy": 0.2},
    "maize": {"loam": 1.0, "clay_loam": 0.9, "sandy_loam": 0.8, "clay": 0.7, "silt": 0.7, "sandy": 0.6},
    "sugarcane": {"clay_loam": 1.0, "clay": 0.9, "loam": 0.8, "silt": 0.7, "sandy_loam": 0.6, "sandy": 0.4},
    "chickpea": {"sandy_loam": 1.0, "loam": 0.9, "sandy": 0.8, "clay_loam": 0.7, "silt": 0.6, "clay": 0.4},
    "lentil": {"sandy_loam": 1.0, "loam": 0.9, "sandy": 0.8, "clay_loam": 0.6, "silt": 0.5, "clay": 0.3},
    "mungbean": {"sandy_loam": 1.0, "loam": 0.9, "sandy": 0.8, "clay_loam": 0.7, "silt": 0.6, "clay": 0.4},
}

@function_tool(strict_mode=False)
async def crop_advisor(
    farm_context: FarmContext,
    farmer_profile: FarmerProfile | None = None
) -> CropPlan:
    """
    Recommend optimal crops for the farmer's conditions.
    
    Uses soil type, season, water availability, and land size to rank crops
    by suitability score (yield × price × water match × risk).
    
    Args:
        farm_context: Current farm conditions (district, soil, season, water, acres)
        farmer_profile: Optional farmer identity for personalization
        
    Returns:
        CropPlan with ranked recommendations, primary pick, and reasoning.
    """
    try:
        crops_df = crop_loader.load_crop_recommendations()
        
        # Filter by season
        season_crops = crops_df[crops_df["season"] == farm_context.season.value]
        
        if season_crops.empty:
            return CropPlan(
                district=farmer_profile.district if farmer_profile else "unknown",
                season=farm_context.season.value,
                recommendations=[],
                primary_recommendation=None,
                alternative_crops=[],
                reasoning=f"No crop data available for {farm_context.season.value} season",
                data_source="mock"
            )
        
        # Score each crop
        scored = []
        water_mm = WATER_AVAILABILITY_MM.get(farm_context.water_availability.value, 400)
        
        for _, row in season_crops.iterrows():
            crop_name = row["crop"]
            score = _calculate_suitability(row, farm_context, water_mm)
            
            if score > 0.3:  # Minimum threshold
                risk_factors = _get_risk_factors(row, farm_context, water_mm)
                
                scored.append(CropPlan.__fields__["recommendations"].annotation.__args__[0](  # type: ignore
                    crop_name=crop_name,
                    category=row["category"],
                    expected_yield_kg_per_acre=row["yield_kg_per_acre"],
                    expected_price_pkr_per_40kg=row["price_pkr_per_40kg"],
                    water_requirement_mm=row["water_mm"],
                    growing_days=row["days"],
                    fertilizer_npk_kg_per_acre=(row["n"], row["p"], row["k"]),
                    profit_per_acre_pkr=row["profit_pkr"],
                    suitability_score=score,
                    risk_factors=risk_factors,
                    notes=_get_crop_notes(crop_name, farm_context)
                ))
        
        scored.sort(key=lambda x: x.suitability_score, reverse=True)
        top_5 = scored[:5]
        
        primary = top_5[0] if top_5 else None
        alternatives = top_5[1:3] if len(top_5) > 1 else []
        
        reasoning = _generate_reasoning(primary, farm_context) if primary else "No suitable crops found for your conditions"
        
        return CropPlan(
            district=farmer_profile.district if farmer_profile else "unknown",
            season=farm_context.season.value,
            recommendations=top_5,
            primary_recommendation=primary,
            alternative_crops=alternatives,
            reasoning=reasoning,
            data_source="kaggle"
        )
        
    except Exception as e:
        logger.error(f"Crop advisor error: {e}")
        return CropPlan(
            district=farmer_profile.district if farmer_profile else "unknown",
            season=farm_context.season.value,
            recommendations=[],
            primary_recommendation=None,
            alternative_crops=[],
            reasoning=f"Error generating recommendations: {str(e)}",
            data_source="mock"
        )

def _calculate_suitability(row, ctx: FarmContext, water_mm: float) -> float:
    """Multi-factor suitability scoring."""
    crop = row["crop"]
    
    # Water match (30% weight)
    crop_water = row["water_mm"]
    water_match = 1.0 - min(abs(crop_water - water_mm) / 1000, 1.0)
    
    # Soil match (25% weight)
    soil_match = SOIL_COMPATIBILITY.get(crop, {}).get(ctx.soil_type.value, 0.5)
    
    # Profit score (25% weight)
    profit_score = min(row["profit_pkr"] / 150000, 1.0)
    
    # Season match (20% weight)
    season_match = 1.0 if row["season"] == ctx.season.value else 0.0
    
    total = round(0.30*water_match + 0.25*soil_match + 0.25*profit_score + 0.20*season_match, 3)
    return max(0.0, min(1.0, total))

def _get_risk_factors(row, ctx: FarmContext, water_mm: float) -> list[str]:
    risks = []
    crop = row["crop"]
    
    if row["water_mm"] > water_mm + 100:
        risks.append(f"High water need ({row['water_mm']}mm) vs available ({water_mm}mm)")
    
    soil_score = SOIL_COMPATIBILITY.get(crop, {}).get(ctx.soil_type.value, 0.5)
    if soil_score < 0.6:
        risks.append(f"Soil type {ctx.soil_type.value} not ideal for {crop}")
    
    if row["days"] > 150 and ctx.season.value == "kharif":
        risks.append("Long season - risk of late harvest in monsoon")
    
    if crop in ["cotton", "sugarcane"] and ctx.water_availability.value == "rainfed":
        risks.append("Rainfed not recommended for this crop")
    
    return risks

def _get_crop_notes(crop: str, ctx: FarmContext) -> str:
    notes = []
    if crop == "wheat" and ctx.season.value == "rabi":
        notes.append("Sow by mid-November for best yield")
    elif crop == "cotton" and ctx.season.value == "kharif":
        notes.append("Plant early (April-May) to avoid pink bollworm")
    elif crop == "rice":
        notes.append("Requires standing water - ensure irrigation access")
    return "; ".join(notes) if notes else ""

def _generate_reasoning(primary, ctx: FarmContext) -> str:
    if not primary:
        return "No suitable crops found"
    
    parts = [
        f"Top pick: {primary.crop_name} (suitability: {primary.suitability_score:.0%})",
        f"Matches your {ctx.soil_type.value} soil and {ctx.water_availability.value} water",
        f"Expected profit: PKR {primary.profit_per_acre_pkr:,.0f}/acre",
    ]
    return " | ".join(parts)