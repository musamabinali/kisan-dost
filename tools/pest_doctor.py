"""Pest & Disease Doctor Tool."""

from agents import function_tool
from models import PestDiagnosis, FarmContext, PestType, Severity, TreatmentType
from data import pest_loader
import logging

logger = logging.getLogger(__name__)

@function_tool(strict_mode=False)
async def pest_disease_doctor(
    symptoms: str,
    farm_context: FarmContext,
    crop_name: str | None = None,
    language: str = "en"
) -> PestDiagnosis:
    """
    Diagnose pest/disease from farmer's symptom description.
    
    Uses keyword matching + fuzzy search against pest database.
    Returns diagnosis with SAFE treatment plan (dosage validated by guardrail).
    
    Args:
        symptoms: Farmer's description (e.g., "cotton leaves curling, tiny white insects")
        farm_context: Current farm context for crop-specific diagnosis
        crop_name: Optional explicit crop (defaults to context.current_crop)
        language: Output language (en/ur/roman_ur)
        
    Returns:
        PestDiagnosis with pest ID, confidence, and validated TreatmentPlan.
    """
    try:
        target_crop = crop_name or farm_context.current_crop
        
        if not target_crop:
            # Try to infer from symptoms
            target_crop = _infer_crop_from_symptoms(symptoms)
        
        matches = pest_loader.search_pests(symptoms, target_crop)
        
        if not matches:
            return _unknown_diagnosis(target_crop, language)
        
        best_match = matches[0]
        treatment = _build_treatment_plan(best_match)
        
        urdu_name = best_match.get("urdu_name") if language in ("ur", "roman_ur") else None
        
        return PestDiagnosis(
            pest_name=best_match["name"],
            pest_type=PestType(best_match["type"]),
            scientific_name=best_match.get("scientific_name"),
            confidence=best_match["confidence"],
            symptoms_matched=best_match["matched_symptoms"],
            affected_crops=[c.strip() for c in str(best_match.get("crops", "")).split(",")],
            severity=Severity(best_match["severity"]),
            treatment=treatment,
            preventive_measures=[m.strip() for m in str(best_match.get("prevention", "")).split(";")],
            economic_threshold=best_match.get("threshold"),
            urdu_name=urdu_name
        )
        
    except Exception as e:
        logger.error(f"Pest doctor error: {e}")
        return _unknown_diagnosis(target_crop if 'target_crop' in locals() else None, language)

def _infer_crop_from_symptoms(symptoms: str) -> str | None:
    """Try to infer crop from symptom keywords."""
    symptom_lower = symptoms.lower()
    crop_keywords = {
        "cotton": ["cotton", "kapas", "boll", "lint"],
        "rice": ["rice", "paddy", "chawal", "tillering", "panicle"],
        "wheat": ["wheat", "gandam", "tillering", "grain fill"],
        "maize": ["maize", "makai", "corn", "cob", "tassel"],
        "sugarcane": ["sugarcane", "gana", "cane"],
        "tomato": ["tomato", "tamatar", "fruit"],
        "chili": ["chili", "mirch", "pepper"],
        "onion": ["onion", "pyaz"],
        "potato": ["potato", "aloo"],
    }
    
    for crop, keywords in crop_keywords.items():
        if any(kw in symptom_lower for kw in keywords):
            return crop
    return None

def _build_treatment_plan(match: dict) -> TreatmentType:
    """Build IPM-first treatment with chemical as last resort."""
    treatments_str = match.get("treatments", "[]")
    
    # Parse treatments - in production, store as proper JSON
    import ast
    try:
        treatments = ast.literal_eval(treatments_str) if isinstance(treatments_str, str) else []
    except:
        treatments = []
    
    # Prefer IPM/cultural/biological first
    for t in treatments:
        if t.get("type") in ("ipm", "cultural", "biological"):
            return TreatmentType(
                treatment_type=TreatmentType(t["type"]),
                pesticide_name=t.get("name"),
                active_ingredient=t.get("active_ingredient"),
                dosage_ml_per_acre=t.get("dosage_ml_per_acre", 0),
                application_method=t.get("method", "spray"),
                timing=t.get("timing", "As needed"),
                frequency=t.get("frequency", "As needed"),
                safety=_parse_safety(t.get("safety", {})),
                cost_per_acre_pkr=t.get("cost_per_acre_pkr", 0)
            )
    
    # Chemical with safety validation
    for t in treatments:
        if t.get("type") == "chemical":
            return TreatmentType(
                treatment_type=TreatmentType.CHEMICAL,
                pesticide_name=t.get("name"),
                active_ingredient=t.get("active_ingredient"),
                dosage_ml_per_acre=t.get("dosage_ml_per_acre", 0),
                application_method=t.get("method", "spray"),
                timing=t.get("timing", "Early morning"),
                frequency=t.get("frequency", "Repeat after 14 days"),
                safety=_parse_safety(t.get("safety", {})),
                cost_per_acre_pkr=t.get("cost_per_acre_pkr", 0),
                alternatives=[TreatmentType(**alt) for alt in treatments if alt.get("type") != "chemical"]
            )
    
    # Fallback
    return TreatmentType(
        treatment_type=TreatmentType.CULTURAL,
        pesticide_name=None,
        active_ingredient=None,
        dosage_ml_per_acre=0,
        application_method="spray",
        timing="Monitor and consult expert",
        frequency="As needed",
        safety=_parse_safety({}),
        cost_per_acre_pkr=0
    )

def _parse_safety(safety_dict: dict) -> 'PesticideSafety':
    from models import PesticideSafety
    return PesticideSafety(
        max_dosage_ml_per_acre=safety_dict.get("max_dosage_ml_per_acre", 0),
        pre_harvest_interval_days=safety_dict.get("pre_harvest_interval_days", 0),
        re_entry_interval_hours=safety_dict.get("re_entry_interval_hours", 0),
        banned_for_crops=safety_dict.get("banned_for_crops", []),
        protective_equipment=safety_dict.get("protective_equipment", ["mask", "gloves", "goggles"]),
        bee_toxicity=safety_dict.get("bee_toxicity", "moderate"),
        aquatic_toxicity=safety_dict.get("aquatic_toxicity", "moderate")
    )

def _unknown_diagnosis(crop: str | None, language: str) -> PestDiagnosis:
    from models import TreatmentType, PesticideSafety
    urdu_msgs = {
        "unknown_pest": "نامعلوم",
        "consult_expert": "مقامی ماہر زراعت سے مشورہ لیں",
    }
    
    return PestDiagnosis(
        pest_name="Unknown",
        pest_type=PestType.INSECT,
        confidence=0.0,
        symptoms_matched=[],
        affected_crops=[crop] if crop else [],
        severity=Severity.LOW,
        treatment=TreatmentType(
            treatment_type=TreatmentType.CULTURAL,
            dosage_ml_per_acre=0,
            application_method="spray",
            timing="N/A",
            frequency="N/A",
            safety=PesticideSafety(
                max_dosage_ml_per_acre=0,
                pre_harvest_interval_days=0,
                re_entry_interval_hours=0
            ),
            cost_per_acre_pkr=0
        ),
        preventive_measures=[urdu_msgs["consult_expert"] if language in ("ur", "roman_ur") else "Consult local agriculture officer for field diagnosis"],
        urdu_name=urdu_msgs["unknown_pest"] if language in ("ur", "roman_ur") else None
    )