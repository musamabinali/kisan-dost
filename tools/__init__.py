"""Tools package initialization."""

from .crop_advisor import crop_advisor
from .pest_doctor import pest_disease_doctor
from .fertilizer_calculator import fertilizer_calculator
from .mandi_lookup import mandi_price_lookup
from .irrigation_weather import irrigation_weather
from .profit_estimator import profit_estimator
from .govt_support import govt_support_finder

# Export all tools for easy import
ALL_TOOLS = [
    crop_advisor,
    pest_disease_doctor,
    fertilizer_calculator,
    mandi_price_lookup,
    irrigation_weather,
    profit_estimator,
    govt_support_finder,
]

__all__ = [
    "crop_advisor",
    "pest_disease_doctor",
    "fertilizer_calculator",
    "mandi_price_lookup",
    "irrigation_weather",
    "profit_estimator",
    "govt_support_finder",
    "ALL_TOOLS",
]