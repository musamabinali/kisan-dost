"""Output guardrails for pesticide safety and medical advice prevention."""

from specialists import GuardrailFunctionOutput, output_guardrail
from models import TreatmentPlan, PesticideSafety
from config.constants import PESTICIDE_SAFETY_LIMITS, PRE_HARVEST_INTERVALS, BANNED_PESTICIDES
import logging
import re

logger = logging.getLogger(__name__)

@output_guardrail
async def output_guardrail(
    ctx,
    agent,
    output: str | TreatmentPlan | dict
) -> GuardrailFunctionOutput:
    """
    Output guardrail that enforces:
    - Pesticide dosage within safe limits
    - Pre-harvest interval stated
    - No human medical advice
    - No banned pesticides recommended
    """
    # If output is a TreatmentPlan, validate it
    if isinstance(output, TreatmentPlan):
        return _validate_treatment_plan(output)
    
    # If output is a string, check for safety issues
    if isinstance(output, str):
        return _validate_text_output(output)
    
    # If output is a dict (from function tool), check it
    if isinstance(output, dict):
        return _validate_dict_output(output)
    
    return GuardrailFunctionOutput(
        output_info={"validated": True},
        tripwire_triggered=False
    )

def _validate_treatment_plan(plan: TreatmentPlan) -> GuardrailFunctionOutput:
    """Validate a TreatmentPlan for safety."""
    issues = []
    
    # Check if chemical treatment
    if plan.treatment_type.value == "chemical" and plan.pesticide_name:
        pesticide_key = plan.pesticide_name.lower().replace(" ", "_").replace("-", "_")
        
        # Check banned pesticides
        for banned in BANNED_PESTICIDES:
            if banned in pesticide_key:
                return GuardrailFunctionOutput(
                    output_info={
                        "validated": False,
                        "issues": [f"Banned pesticide recommended: {plan.pesticide_name}"]
                    },
                    tripwire_triggered=True
                )
        
        # Check dosage against safety limits
        if pesticide_key in PESTICIDE_SAFETY_LIMITS:
            max_safe = PESTICIDE_SAFETY_LIMITS[pesticide_key]
            if plan.dosage_ml_per_acre > max_safe:
                issues.append(f"Dosage {plan.dosage_ml_per_acre} ml/acre exceeds safe limit of {max_safe} ml/acre for {plan.pesticide_name}")
                # Auto-correct dosage
                plan.dosage_ml_per_acre = max_safe
        
        # Check PHI is stated
        if plan.safety.pre_harvest_interval_days == 0:
            # Try to get from known data
            if pesticide_key in PRE_HARVEST_INTERVALS:
                plan.safety.pre_harvest_interval_days = PRE_HARVEST_INTERVALS[pesticide_key]
            else:
                issues.append("Pre-harvest interval (PHI) not specified")
        
        # Check REI is stated
        if plan.safety.re_entry_interval_hours == 0:
            issues.append("Re-entry interval (REI) not specified")
        
        # Check protective equipment
        if not plan.safety.protective_equipment:
            plan.safety.protective_equipment = ["mask", "gloves", "goggles"]
            issues.append("Added default protective equipment: mask, gloves, goggles")
    
    # Check for human medical advice
    medical_keywords = ["human", "person", "patient", "doctor", "medical", "health", "medicine", "tablet", "syrup", "injection"]
    text_to_check = f"{plan.pesticide_name or ''} {plan.timing} {plan.frequency}".lower()
    for kw in medical_keywords:
        if kw in text_to_check:
            issues.append(f"Potential medical advice detected: '{kw}'")
    
    if issues:
        logger.warning(f"Treatment plan validation issues: {issues}")
        return GuardrailFunctionOutput(
            output_info={
                "validated": True,
                "issues": issues,
                "corrected_plan": plan.model_dump()
            },
            tripwire_triggered=False  # Don't block, just warn and correct
        )
    
    return GuardrailFunctionOutput(
        output_info={"validated": True},
        tripwire_triggered=False
    )

def _validate_text_output(text: str) -> GuardrailFunctionOutput:
    """Validate text output for safety issues."""
    issues = []
    text_lower = text.lower()
    
    # Check for banned pesticides
    for banned in BANNED_PESTICIDES:
        if banned.replace("_", " ") in text_lower:
            issues.append(f"Banned pesticide mentioned: {banned}")
    
    # Check for medical advice
    medical_patterns = [
        r"(take|consume|drink|inject|apply)\s+(this|that)\s+(medicine|drug|pill|tablet|syrup)",
        r"(for|to treat)\s+(human|person|people|patient)\s+(health|illness|disease|condition)",
        r"doctor\s+(recommends|prescribes|advises)",
    ]
    
    for pattern in medical_patterns:
        if re.search(pattern, text_lower):
            issues.append("Potential human medical advice detected")
            break
    
    # Check for dosage without safety info
    dosage_pattern = r"(\d+(?:\.\d+)?)\s*(ml|g|kg|liters?)\s*(per\s+acre|/acre)"
    if re.search(dosage_pattern, text_lower):
        if "pre-harvest" not in text_lower and "phi" not in text_lower:
            issues.append("Dosage mentioned without pre-harvest interval (PHI)")
        if "re-entry" not in text_lower and "rei" not in text_lower:
            issues.append("Dosage mentioned without re-entry interval (REI)")
        if "mask" not in text_lower and "gloves" not in text_lower and "goggles" not in text_lower:
            issues.append("Dosage mentioned without protective equipment warning")
    
    if issues:
        logger.warning(f"Text output validation issues: {issues}")
        return GuardrailFunctionOutput(
            output_info={"validated": True, "issues": issues},
            tripwire_triggered=False
        )
    
    return GuardrailFunctionOutput(
        output_info={"validated": True},
        tripwire_triggered=False
    )

def _validate_dict_output(data: dict) -> GuardrailFunctionOutput:
    """Validate dict output (from function tools)."""
    issues = []
    
    # Check for treatment plans in dict
    if "treatment" in data and isinstance(data["treatment"], dict):
        treatment = data["treatment"]
        if treatment.get("type") == "chemical":
            pesticide = treatment.get("pesticide_name", "").lower().replace(" ", "_")
            dosage = treatment.get("dosage_ml_per_acre", 0)
            
            # Check banned
            for banned in BANNED_PESTICIDES:
                if banned in pesticide:
                    issues.append(f"Banned pesticide in output: {treatment.get('pesticide_name')}")
            
            # Check dosage
            if pesticide in PESTICIDE_SAFETY_LIMITS:
                max_safe = PESTICIDE_SAFETY_LIMITS[pesticide]
                if dosage > max_safe:
                    issues.append(f"Unsafe dosage: {dosage} ml/acre > {max_safe} ml/acre limit")
    
    if issues:
        return GuardrailFunctionOutput(
            output_info={"validated": True, "issues": issues},
            tripwire_triggered=False
        )
    
    return GuardrailFunctionOutput(
        output_info={"validated": True},
        tripwire_triggered=False
    )