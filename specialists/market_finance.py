"""Market & Finance Agent - handles prices, profit, govt schemes."""

from config.prompts.system_prompts import MARKET_FINANCE_AGENT_INSTRUCTIONS
from tools import mandi_price_lookup, profit_estimator, govt_support_finder
from models import ProfitEstimate
from .base import create_agent

market_finance_agent = create_agent(
    name="market_finance_agent",
    instructions=MARKET_FINANCE_AGENT_INSTRUCTIONS,
    tools=[mandi_price_lookup, profit_estimator, govt_support_finder],
)