"""Government Support Finder Tool."""

from agents import function_tool
from models import SchemeMatch, GovtScheme, EligibilityCriteria, FarmerProfile, FarmContext
from data import govt_loader
import logging
from typing import Optional, Literal

logger = logging.getLogger(__name__)

@function_tool(strict_mode=False)
async def govt_support_finder(
    farmer_profile: FarmerProfile,
    farm_context: FarmContext,
    need_type: str | None = None  # "fertilizer", "seed", "loan", "insurance", "machinery", "all"
) -> list[SchemeMatch]:
    """
    Surface the Kisan Card, subsidized fertilizer or agri-loan schemes relevant to the farmer's province and need.
    
    Args:
        farmer_profile: Farmer's identity (district, province)
        farm_context: Current farm context (crop, land size)
        need_type: Type of support needed (optional filter)
        
    Returns:
        List of SchemeMatch with eligibility and next steps.
    """
    try:
        province = farmer_profile.province.value
        district = farmer_profile.district
        crop = farm_context.current_crop
        land_acres = farm_context.land_size_acres
        farmer_category = _get_farmer_category(land_acres)
        
        # Get matching schemes
        matches = govt_loader.get_schemes_for_farmer(
            province=province,
            district=district,
            crop=crop,
            land_acres=land_acres,
            farmer_category=farmer_category
        )
        
        # Filter by need_type if specified
        if need_type:
            need_type = need_type.lower()
            matches = [m for m in matches if need_type in m["scheme"].get("scheme_type", "").lower()]
        
        # Convert to SchemeMatch objects
        results = []
        for match in matches[:10]:  # Top 10
            scheme_data = match["scheme"]
            scheme = _dict_to_scheme(scheme_data)
            
            next_steps = _generate_next_steps(scheme, match["missing_criteria"])
            
            results.append(SchemeMatch(
                scheme=scheme,
                match_score=match["match_score"],
                matched_criteria=match["matched_criteria"],
                missing_criteria=match["missing_criteria"],
                next_steps=next_steps
            ))
        
        # Always include Kisan Card if in Punjab/Sindh/KPK and not already in results
        kisan_card_schemes = [m for m in results if "kisan_card" in m.scheme.scheme_id]
        if not kisan_card_schemes and province in ["punjab", "sindh", "kpk"]:
            kc_scheme = _get_kisan_card_scheme(province)
            if kc_scheme:
                results.insert(0, SchemeMatch(
                    scheme=kc_scheme,
                    match_score=0.9,
                    matched_criteria=["province", "farmer_category"],
                    missing_criteria=[],
                    next_steps=["Register at nearest agriculture office or online portal", "Bring CNIC, land record, and bank account details"]
                ))
        
        return results
        
    except Exception as e:
        logger.error(f"Govt support finder error: {e}")
        return []

def _get_farmer_category(land_acres: float) -> str:
    if land_acres <= 12.5:  # < 5 hectares
        return "small"
    elif land_acres <= 50:
        return "medium"
    else:
        return "large"

def _dict_to_scheme(data: dict) -> GovtScheme:
    """Convert dict to GovtScheme model."""
    eligibility = EligibilityCriteria(
        min_land_acres=data.get("min_land_acres"),
        max_land_acres=data.get("max_land_acres"),
        required_crops=[c.strip() for c in str(data.get("required_crops", "")).split(",")] if data.get("required_crops") else [],
        provinces=[data.get("province", "")],
        districts=[d.strip() for c in str(data.get("districts", "")).split(",")] if data.get("districts") else [],
        farmer_categories=[c.strip() for c in str(data.get("farmer_categories", "")).split(",")] if data.get("farmer_categories") else [],
        documents_required=[d.strip() for c in str(data.get("documents_required", "")).split(",")] if data.get("documents_required") else [],
    )
    
    return GovtScheme(
        scheme_id=data.get("scheme_id", ""),
        name=data.get("name", ""),
        name_urdu=data.get("name_urdu"),
        scheme_type=data.get("scheme_type", ""),
        province=data.get("province", ""),
        department=data.get("department", ""),
        description=data.get("description", ""),
        benefits=[b.strip() for b in str(data.get("benefits", "")).split(";")] if data.get("benefits") else [],
        eligibility=eligibility,
        application_deadline=data.get("application_deadline"),
        application_method=data.get("application_method", "both"),
        application_url=data.get("application_url"),
        contact_info=data.get("contact_info"),
        is_active=data.get("is_active", True),
        last_updated=data.get("last_updated")
    )

def _generate_next_steps(scheme: GovtScheme, missing: list[str]) -> list[str]:
    """Generate actionable next steps."""
    steps = []
    
    if scheme.application_method in ["online", "both"] and scheme.application_url:
        steps.append(f"Apply online: {scheme.application_url}")
    
    if scheme.application_method in ["offline", "both"]:
        steps.append(f"Visit {scheme.department} office in your district")
    
    if scheme.contact_info:
        steps.append(f"Call helpline: {scheme.contact_info}")
    
    # Documents
    if scheme.eligibility.documents_required:
        docs = ", ".join(scheme.eligibility.documents_required)
        steps.append(f"Prepare documents: {docs}")
    
    # Missing criteria
    if missing:
        for m in missing:
            if m == "land_size":
                steps.append("Check if your land size qualifies - some schemes have min/max limits")
            elif m == "crop":
                steps.append(f"This scheme may be for specific crops: {', '.join(scheme.eligibility.required_crops)}")
            elif m == "category":
                steps.append(f"Scheme targets: {', '.join(scheme.eligibility.farmer_categories)} farmers")
    
    if scheme.application_deadline:
        steps.append(f"Deadline: {scheme.application_deadline}")
    
    return steps if steps else ["Contact local agriculture office for guidance"]

def _get_kisan_card_scheme(province: str) -> GovtScheme | None:
    """Get Kisan Card scheme for province."""
    kc_data = {
        "punjab": {
            "scheme_id": "kisan_card_punjab",
            "name": "Kisan Card Punjab",
            "name_urdu": "کسان کارڈ پنجاب",
            "scheme_type": "kisan_card",
            "province": "punjab",
            "department": "Agriculture Department Punjab",
            "description": "Smart card for direct subsidy transfer on fertilizer, seeds, pesticides",
            "benefits": [
                "Direct subsidy on fertilizer (PKR 1000/bag DAP, 500/bag Urea)",
                "Seeds subsidy",
                "Pesticides subsidy",
                "Access to agri-loans"
            ],
            "eligibility": EligibilityCriteria(
                min_land_acres=0.5,
                max_land_acres=50.0,
                required_crops=["wheat", "cotton", "rice", "maize", "sugarcane"],
                farmer_categories=["small", "medium"],
                documents_required=["CNIC", "Land ownership/tenancy proof", "Bank account"]
            ),
            "application_deadline": "2024-06-30",
            "application_method": "both",
            "application_url": "https://kisan.punjab.gov.pk",
            "contact_info": "0800-17000 (Agriculture Helpline)"
        },
        "sindh": {
            "scheme_id": "kisan_card_sindh",
            "name": "Kisan Card Sindh",
            "name_urdu": "کسان کارڈ سندھ",
            "scheme_type": "kisan_card",
            "province": "sindh",
            "department": "Agriculture Department Sindh",
            "description": "Digital farmer registration and subsidy delivery",
            "benefits": [
                "Fertilizer subsidy",
                "Seed subsidy",
                "Access to credit",
                "Crop insurance linkage"
            ],
            "eligibility": EligibilityCriteria(
                min_land_acres=0.5,
                max_land_acres=50.0,
                required_crops=["wheat", "cotton", "rice", "sugarcane"],
                farmer_categories=["small", "medium"],
                documents_required=["CNIC", "Land record (Form VII)", "Bank account"]
            ),
            "application_deadline": "2024-06-30",
            "application_method": "both",
            "application_url": "https://agri.sindh.gov.pk/kisan-card",
            "contact_info": "0800-12345"
        },
        "kpk": {
            "scheme_id": "kisan_card_kpk",
            "name": "Kisan Card KPK",
            "name_urdu": "کسان کارڈ کے پی کے",
            "scheme_type": "kisan_card",
            "province": "kpk",
            "department": "Agriculture Department KPK",
            "description": "Digital farmer registration and subsidy delivery",
            "benefits": [
                "Fertilizer, seed, pesticide subsidies",
                "Credit access",
                "Training programs"
            ],
            "eligibility": EligibilityCriteria(
                min_land_acres=0.5,
                max_land_acres=50.0,
                required_crops=["wheat", "maize", "sugarcane", "orchards"],
                farmer_categories=["small", "medium"],
                documents_required=["CNIC", "Land record", "Bank account"]
            ),
            "application_deadline": "2024-06-30",
            "application_method": "both",
            "application_url": "https://agriculture.kp.gov.pk/kisan-card",
            "contact_info": "0800-12345"
        },
    }
    
    data = kc_data.get(province)
    if data:
        return _dict_to_scheme(data)
    return None