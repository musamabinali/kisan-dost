"""Config package initialization."""

from .settings import settings
from .constants import *
from .prompts.system_prompts import *
from .prompts.urdu_prompts import *

__all__ = [
    "settings",
    "DISTRICTS_BY_PROVINCE",
    "ALL_DISTRICTS",
    "RABI_CROPS",
    "KHARIF_CROPS",
    "ZAID_CROPS",
    "FERTILIZER_COMPOSITION",
    "DEFAULT_FERTILIZER_PRICES",
    "CROP_NPK_REQUIREMENTS",
    "CROP_WATER_REQUIREMENTS",
    "PUNJAB_MANDIS",
    "GOVT_SCHEMES_BY_PROVINCE",
    "PESTICIDE_SAFETY_LIMITS",
    "PRE_HARVEST_INTERVALS",
    "URDU_TERMS",
    "TRIAGE_AGENT_INSTRUCTIONS",
    "AGRONOMY_AGENT_INSTRUCTIONS",
    "PEST_DOCTOR_AGENT_INSTRUCTIONS",
    "MARKET_FINANCE_AGENT_INSTRUCTIONS",
    "GUARDRAIL_INSTRUCTIONS",
    "URDU_PROMPTS",
    "CROP_URDU_NAMES",
    "PEST_URDU_NAMES",
    "SOIL_URDU_NAMES",
    "SEASON_URDU_NAMES",
    "WATER_URDU_NAMES",
]