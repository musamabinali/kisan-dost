"""Fertilizer Calculator Tool."""

from agents import function_tool
from models import FertilizerPlan, FertilizerBag, NPKRequirement, FertilizerType
from data import fertilizer_loader
from config.constants import CROP_NPK_REQUIREMENTS, DEFAULT_FERTILIZER_PRICES
import logging

logger = logging.getLogger(__name__)

# Default fertilizer prices (can be overridden by data file)
FERTILIZER_PRICES = DEFAULT_FERTILIZER_PRICES.copy()

@function_tool(strict_mode=False)
async def fertilizer_calculator(
    crop: str,
    acres: float,
    soil_test_npk: tuple[float, float, float] | None = None,
    target_yield_kg_per_acre: float | None = None
) -> FertilizerPlan:
    """
    Compute NPK need per acre for a crop and convert it into bags of Urea / DAP with total cost in rupees.
    
    Args:
        crop: Crop name (e.g., "wheat", "cotton", "rice")
        acres: Land size in acres
        soil_test_npk: Optional (N, P, K) available in soil kg/acre from soil test
        target_yield_kg_per_acre: Optional target yield to adjust fertilizer rate
        
    Returns:
        FertilizerPlan with bag counts, costs, and application schedule.
    """
    try:
        crop_lower = crop.lower().strip()
        
        # Get base NPK requirement
        base_npk = CROP_NPK_REQUIREMENTS.get(crop_lower)
        if not base_npk:
            # Default NPK for unknown crops
            base_npk = {"N": 80, "P2O5": 40, "K2O": 40}
        
        # Adjust for soil test if provided
        if soil_test_npk:
            soil_n, soil_p, soil_k = soil_test_npk
            # Reduce fertilizer by soil supply (assuming 50% availability)
            n_need = max(base_npk["N"] - soil_n * 0.5, 0)
            p_need = max(base_npk["P2O5"] - soil_p * 0.5, 0)
            k_need = max(base_npk["K2O"] - soil_k * 0.5, 0)
        else:
            n_need = base_npk["N"]
            p_need = base_npk["P2O5"]
            k_need = base_npk["K2O"]
        
        # Adjust for target yield
        if target_yield_kg_per_acre:
            # Typical yield for this crop (rough estimate)
            typical_yields = {
                "wheat": 1200, "cotton": 800, "rice": 2000, "maize": 2500,
                "sugarcane": 25000, "chickpea": 600, "lentil": 500,
                "mustard": 500, "groundnut": 600, "sesame": 300,
                "sunflower": 700, "potato": 8000, "onion": 6000, "tomato": 10000
            }
            typical = typical_yields.get(crop_lower, 1000)
            yield_factor = target_yield_kg_per_acre / typical
            yield_factor = max(0.7, min(1.5, yield_factor))  # Clamp
            n_need *= yield_factor
            p_need *= yield_factor
            k_need *= yield_factor
        
        npk_req = NPKRequirement(
            nitrogen_kg_per_acre=round(n_need, 1),
            phosphorus_kg_per_acre=round(p_need, 1),
            potassium_kg_per_acre=round(k_need, 1)
        )
        
        # Calculate fertilizer bags
        bags = _calculate_bags(npk_req)
        
        # Calculate total cost
        total_cost = sum(b.total_cost_pkr for b in bags) * acres
        
        # Application schedule
        schedule = _get_application_schedule(crop_lower, bags)
        
        # Check subsidy eligibility (simplified)
        subsidy_eligible = crop_lower in ["wheat", "cotton", "rice", "maize", "sugarcane"]
        subsidy_details = "Eligible for Kisan Card fertilizer subsidy (PKR 500-1000/bag)" if subsidy_eligible else None
        
        return FertilizerPlan(
            crop=crop_lower,
            acres=acres,
            npk_requirement=npk_req,
            fertilizer_bags=bags,
            total_cost_pkr=round(total_cost, 0),
            application_schedule=schedule,
            subsidy_eligible=subsidy_eligible,
            subsidy_details=subsidy_details,
            notes=_get_fertilizer_notes(crop_lower)
        )
        
    except Exception as e:
        logger.error(f"Fertilizer calculator error: {e}")
        # Return minimal plan
        return FertilizerPlan(
            crop=crop,
            acres=acres,
            npk_requirement=NPKRequirement(nitrogen_kg_per_acre=0, phosphorus_kg_per_acre=0, potassium_kg_per_acre=0),
            fertilizer_bags=[],
            total_cost_pkr=0,
            application_schedule=[],
            notes=f"Error: {str(e)}"
        )

def _calculate_bags(npk: NPKRequirement) -> list[FertilizerBag]:
    """Calculate optimal fertilizer bag combination."""
    bags = []
    
    # Strategy: Use DAP for P, then Urea for remaining N, then MOP for K
    # 1. DAP for phosphorus (also provides some N)
    dap_bags = 0
    if npk.phosphorus_kg_per_acre > 0:
        # DAP: 46% P2O5, 18% N per 50kg bag
        p_per_bag = 50 * 0.46  # 23 kg P2O5 per bag
        dap_bags = npk.phosphorus_kg_per_acre / p_per_bag
        n_from_dap = dap_bags * 50 * 0.18  # 9 kg N per bag
    else:
        n_from_dap = 0
    
    if dap_bags > 0:
        bags.append(FertilizerBag(
            fertilizer_type=FertilizerType.DAP,
            bags_needed=round(dap_bags, 2),
            weight_per_bag_kg=50,
            price_per_bag_pkr=FERTILIZER_PRICES.get("dap", 11500)
        ))
    
    # 2. Urea for remaining nitrogen
    remaining_n = max(npk.nitrogen_kg_per_acre - n_from_dap, 0)
    if remaining_n > 0:
        # Urea: 46% N per 50kg bag = 23 kg N per bag
        urea_bags = remaining_n / 23
        bags.append(FertilizerBag(
            fertilizer_type=FertilizerType.UREA,
            bags_needed=round(urea_bags, 2),
            weight_per_bag_kg=50,
            price_per_bag_pkr=FERTILIZER_PRICES.get("urea", 3000)
        ))
    
    # 3. MOP for potassium
    if npk.potassium_kg_per_acre > 0:
        # MOP: 60% K2O per 50kg bag = 30 kg K2O per bag
        mop_bags = npk.potassium_kg_per_acre / 30
        bags.append(FertilizerBag(
            fertilizer_type=FertilizerType.MOP,
            bags_needed=round(mop_bags, 2),
            weight_per_bag_kg=50,
            price_per_bag_pkr=FERTILIZER_PRICES.get("mop", 4500)
        ))
    
    # 4. Zinc sulfate if needed (for rice, wheat, maize, citrus)
    zinc_crops = ["rice", "wheat", "maize", "citrus", "cotton"]
    if npk.nitrogen_kg_per_acre > 0:  # Simplified - add zinc for major crops
        bags.append(FertilizerBag(
            fertilizer_type=FertilizerType.ZINC_SULFATE,
            bags_needed=0.5,  # 25kg bag, half bag per acre
            weight_per_bag_kg=25,
            price_per_bag_pkr=FERTILIZER_PRICES.get("zinc_sulfate", 2500)
        ))
    
    return bags

def _get_application_schedule(crop: str, bags: list[FertilizerBag]) -> list[dict]:
    """Generate application schedule based on crop and fertilizers."""
    schedule = []
    
    crop_schedules = {
        "wheat": [
            {"stage": "Basal (at sowing)", "fertilizer": "DAP", "bags_per_acre": 1.0, "timing": "With seed drill"},
            {"stage": "First irrigation (21 DAS)", "fertilizer": "Urea", "bags_per_acre": 0.75, "timing": "Broadcast before irrigation"},
            {"stage": "Second irrigation (45 DAS)", "fertilizer": "Urea", "bags_per_acre": 0.5, "timing": "Broadcast before irrigation"},
        ],
        "cotton": [
            {"stage": "Basal (at sowing)", "fertilizer": "DAP", "bags_per_acre": 1.0, "timing": "In furrow with seed"},
            {"stage": "Squaring (45 DAS)", "fertilizer": "Urea", "bags_per_acre": 1.0, "timing": "Side dress"},
            {"stage": "Flowering (75 DAS)", "fertilizer": "Urea", "bags_per_acre": 0.5, "timing": "Side dress"},
        ],
        "rice": [
            {"stage": "Basal (puddling)", "fertilizer": "DAP", "bags_per_acre": 1.0, "timing": "Broadcast in standing water"},
            {"stage": "Tillering (21 DAT)", "fertilizer": "Urea", "bags_per_acre": 1.0, "timing": "Broadcast in standing water"},
            {"stage": "Panicle initiation (45 DAT)", "fertilizer": "Urea", "bags_per_acre": 0.5, "timing": "Broadcast in standing water"},
        ],
        "maize": [
            {"stage": "Basal (at sowing)", "fertilizer": "DAP", "bags_per_acre": 1.0, "timing": "In furrow with seed"},
            {"stage": "Knee-high (30 DAS)", "fertilizer": "Urea", "bags_per_acre": 1.5, "timing": "Side dress + earthing up"},
            {"stage": "Tasseling (50 DAS)", "fertilizer": "Urea", "bags_per_acre": 0.5, "timing": "Side dress if needed"},
        ],
        "sugarcane": [
            {"stage": "Basal (at planting)", "fertilizer": "DAP", "bags_per_acre": 2.0, "timing": "In furrow with setts"},
            {"stage": "Tillering (45 DAP)", "fertilizer": "Urea", "bags_per_acre": 2.0, "timing": "Side dress + earthing up"},
            {"stage": "Grand growth (90 DAP)", "fertilizer": "Urea", "bags_per_acre": 1.5, "timing": "Side dress + earthing up"},
        ],
    }
    
    default_schedule = [
        {"stage": "Basal", "fertilizer": "DAP", "bags_per_acre": 1.0, "timing": "At sowing"},
        {"stage": "Top dress 1", "fertilizer": "Urea", "bags_per_acre": 1.0, "timing": "3-4 weeks after sowing"},
        {"stage": "Top dress 2", "fertilizer": "Urea", "bags_per_acre": 0.5, "timing": "6-8 weeks after sowing"},
    ]
    
    return crop_schedules.get(crop, default_schedule)

def _get_fertilizer_notes(crop: str) -> str:
    notes = {
        "wheat": "Apply zinc sulfate if soil test shows <1 ppm Zn. Split urea in 2-3 doses.",
        "cotton": "Avoid late nitrogen after flowering. Potassium improves boll weight.",
        "rice": "Use nitrification inhibitors (neem-coated urea) for better N efficiency. Keep 2-3cm water after urea.",
        "maize": "All P & K at planting. Split N: 1/3 basal, 1/3 knee-high, 1/3 tasseling.",
        "sugarcane": "High K requirement. Apply press mud/compost for organic matter.",
        "chickpea": "No nitrogen needed if inoculated with rhizobium. P is critical.",
        "potato": "High K for tuber bulking. Split N: 1/2 basal, 1/2 tuber initiation.",
    }
    return notes.get(crop, "Follow soil test recommendations. Split nitrogen applications for efficiency.")