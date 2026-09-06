"""Safety validators for pesticide dosages and crop safety."""

from config.constants import PESTICIDE_SAFETY_LIMITS, PRE_HARVEST_INTERVALS, BANNED_PESTICIDES
from models import PesticideSafety
from typing import Optional, Literal
import logging

logger = logging.getLogger(__name__)

def validate_pesticide_safety(
    pesticide_name: str,
    dosage_ml_per_acre: float,
    crop: Optional[str] = None
) -> PesticideSafety:
    """
    Validate pesticide application safety and return safety constraints.
    
    Args:
        pesticide_name: Name of the pesticide
        dosage_ml_per_acre: Proposed dosage in ml per acre
        crop: Target crop (optional)
        
    Returns:
        PesticideSafety with validated limits
    """
    pesticide_key = pesticide_name.lower().replace(" ", "_").replace("-", "_")
    
    # Check banned
    for banned in BANNED_PESTICIDES:
        if banned in pesticide_key:
            raise ValueError(f"Pesticide {pesticide_name} is banned in Pakistan")
    
    # Get safety limits
    max_dosage = PESTICIDE_SAFETY_LIMITS.get(pesticide_key, 2000)  # Default conservative
    phi = PRE_HARVEST_INTERVALS.get(pesticide_key, 14)  # Default 14 days
    
    # Validate dosage
    if dosage_ml_per_acre > max_dosage:
        logger.warning(f"Dosage {dosage_ml_per_acre} exceeds limit {max_dosage} for {pesticide_name}. Capping.")
        dosage_ml_per_acre = max_dosage
    
    if dosage_ml_per_acre <= 0:
        raise ValueError("Dosage must be positive")
    
    # Check crop-specific bans
    banned_for_crops = []
    if crop:
        crop_lower = crop.lower()
        # Some pesticides banned for specific crops
        crop_bans = {
            "imidacloprid": ["honey_crops", "flowering_crops"],
            "fipronil": ["rice_seedling"],  # Not for rice nursery
        }
        for pest, crops in crop_bans.items():
            if pest in pesticide_key and crop_lower in crops:
                banned_for_crops.append(crop_lower)
    
    return PesticideSafety(
        max_dosage_ml_per_acre=max_dosage,
        pre_harvest_interval_days=phi,
        re_entry_interval_hours=12,  # Default
        banned_for_crops=banned_for_crops,
        protective_equipment=["mask", "gloves", "goggles", "long_sleeves", "boots"],
        bee_toxicity=_get_bee_toxicity(pesticide_key),
        aquatic_toxicity=_get_aquatic_toxicity(pesticide_key)
    )

def _get_bee_toxicity(pesticide_key: str) -> str:
    """Get bee toxicity rating."""
    high_bee = ["imidacloprid", "thiamethoxam", "clothianidin", "fipronil", "chlorpyrifos", "cypermethrin", "lambda_cyhalothrin", "bifenthrin"]
    moderate_bee = ["acetamiprid", "profenofos", "chlorantraniliprole", "flubendiamide", "indoxacarb", "methomyl"]
    
    if pesticide_key in high_bee:
        return "high"
    elif pesticide_key in moderate_bee:
        return "moderate"
    return "low"

def _get_aquatic_toxicity(pesticide_key: str) -> str:
    """Get aquatic toxicity rating."""
    high_aquatic = ["fipronil", "chlorpyrifos", "lambda_cyhalothrin", "bifenthrin", "cypermethrin"]
    moderate_aquatic = ["imidacloprid", "thiamethoxam", "chlorantraniliprole", "flubendiamide", "profenofos"]
    
    if pesticide_key in high_aquatic:
        return "high"
    elif pesticide_key in moderate_aquatic:
        return "moderate"
    return "low"

def get_safe_alternatives(pesticide_name: str, crop: str) -> list[str]:
    """Get safer alternative pesticides for a crop."""
    pesticide_key = pesticide_name.lower().replace(" ", "_")
    
    # IPM alternatives by pest type
    alternatives = {
        "whitefly": ["Yellow sticky traps", "Neem oil", "Insecticidal soap", "Encarsia formosa", "Spinosad"],
        "aphid": ["Neem oil", "Insecticidal soap", "Ladybird beetles", "Reflective mulch", "Pirimicarb"],
        "jassid": ["Early sowing", "Resistant varieties", "Neem extract", "Imidacloprid (if needed)"],
        "thrips": ["Blue sticky traps", "Neem oil", "Spinosad", "Predatory mites"],
        "bollworm": ["Bt cotton", "NPV virus", "Pheromone traps", "Chlorantraniliprole", "Emamectin benzoate"],
        "pink_bollworm": ["PB rope (mating disruption)", "Timely harvest", "Crop residue destruction"],
        "armyworm": ["Bt", "Bird perches", "Early planting", "Emamectin benzoate"],
        "stem_borer": ["Crop rotation", "Destroy stubble", "Resistant varieties", "Trichogramma"],
        "leaf_folder": ["Weed removal", "Balanced fertilizer", "Chlorantraniliprole"],
        "blast": ["Resistant varieties", "Silicon fertilizer", "Tricyclazole", "Avoid excess N"],
        "blight": ["Crop rotation", "Mulching", "Mancozeb", "Copper oxychloride"],
        "rust": ["Resistant varieties", "Early sowing", "Propiconazole", "Tebuconazole"],
        "wilt": ["Crop rotation", "Soil solarization", "Trichoderma", "Resistant varieties"],
    }
    
    return alternatives.get(pesticide_key, ["Consult agriculture officer for IPM options"])

def calculate_max_safe_area(dosage_ml_per_acre: float, pesticide_name: str, available_ml: float) -> float:
    """Calculate maximum safe area that can be treated with available pesticide."""
    if dosage_ml_per_acre <= 0:
        return 0
    return available_ml / dosage_ml_per_acre