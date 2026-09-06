"""Triage Agent - routes to specialist agents."""

from agents import function_tool
from models import FarmerProfile, FarmContext, IntentType
from config.prompts.system_prompts import TRIAGE_AGENT_INSTRUCTIONS
from tools import ALL_TOOLS
from .base import create_agent
import logging

logger = logging.getLogger(__name__)

# Triage agent doesn't need tools - it routes via handoffs
# But we can add a classification tool for explicit intent detection

@function_tool(strict_mode=False)
async def classify_intent(user_message: str, farm_context: dict | None = None) -> IntentType:
    """
    Classify the user's intent to route to the correct specialist agent.

    Args:
        user_message: The farmer's question
        farm_context: Current farm context for better classification.

    Returns:
        IntentType enum indicating which specialist should handle this.
    """
    msg = user_message.lower()
    context = farm_context or {}
    if isinstance(context, dict):
        crop_stage = str(context.get("crop_stage", "")).lower()
        current_crop = str(context.get("current_crop", "")).lower()
    else:
        crop_stage = ""
        current_crop = ""
    
    # Crop advice keywords
    crop_keywords = ["what to plant", "which crop", "crop recommend", "fasal", "kasht", "boai", "kis fasal", "better crop"]
    if any(kw in msg for kw in crop_keywords):
        return IntentType.CROP_ADVICE
    
    # Pest/disease keywords
    pest_keywords = ["pest", "disease", "insect", "keera", "bimari", "attack", "eating", "holes", "spots", "curling", "yellowing", "wilting", "whitefly", "aphid", "jassid", "bollworm", "blast", "blight", "rust", "wilt"]
    if any(kw in msg for kw in pest_keywords):
        return IntentType.PEST_DIAGNOSIS
    
    # Fertilizer keywords
    fert_keywords = ["fertilizer", "khad", "urea", "dap", "npk", "nitrogen", "phosphorus", "potash", "bag", "bori", "khurs"]
    if any(kw in msg for kw in fert_keywords):
        return IntentType.FERTILIZER_CALC
    
    # Market/price keywords
    market_keywords = ["price", "rate", "mandi", "sell", "bech", "market", "bhav", "kimat", "mahsul", "mandi rate"]
    if any(kw in msg for kw in market_keywords):
        return IntentType.MANDI_PRICE
    
    # Irrigation/weather keywords
    water_keywords = ["water", "irrigation", "pani", "abpashi", "rain", "barish", "weather", "mosam", "forecast", "frost", "heatwave", "when to irrigate"]
    if any(kw in msg for kw in water_keywords):
        return IntentType.IRRIGATION_WEATHER
    
    # Profit/finance keywords
    profit_keywords = ["profit", "loss", "munafa", "nuqsaan", "cost", "kharcha", "budget", "break even", "break-even", "economics", "return"]
    if any(kw in msg for kw in profit_keywords):
        return IntentType.PROFIT_ESTIMATE
    
    # Government scheme keywords
    govt_keywords = ["scheme", "subsidy", "kisan card", "loan", "qarz", "insurance", "insurance", "sarkari", "skim", "support"]
    if any(kw in msg for kw in govt_keywords):
        return IntentType.GOVT_SCHEME
    
    # Unsafe/off-topic detection
    unsafe_keywords = ["medical", "doctor", "human", "health", "medicine", "drug", "bomb", "weapon", "kill", "suicide", "hurt"]
    if any(kw in msg for kw in unsafe_keywords):
        return IntentType.UNSAFE
    
    off_topic_keywords = ["cricket", "movie", "song", "politics", "news", "weather karachi", "lahore weather"]
    if any(kw in msg for kw in off_topic_keywords):
        return IntentType.OFF_TOPIC
    
    # Default to crop advice if unclear but farming-related
    farming_words = ["farm", "khet", "zameen", "acre", "hectare", "crop", "fasal", "seed", "beej", "tractor", "tube well"]
    if any(kw in msg for kw in farming_words):
        return IntentType.CROP_ADVICE
    
    return IntentType.GENERAL_CHAT

# Triage agent with handoffs (will be set up in agents/__init__.py)
triage_agent = create_agent(
    name="triage_agent",
    instructions=TRIAGE_AGENT_INSTRUCTIONS,
    tools=[classify_intent],
)