"""Agents package initialization - creates the multi-agent system with handoffs."""

from config.prompts.system_prompts import TRIAGE_AGENT_INSTRUCTIONS
from .triage import triage_agent as base_triage_agent, classify_intent
from .agronomy import agronomy_agent
from .pest_doctor import pest_doctor_agent
from .market_finance import market_finance_agent
from .base import create_agent

# Create the complete triage agent with handoffs to all specialists
triage_agent = create_agent(
    name="Triage Agent",
    instructions=TRIAGE_AGENT_INSTRUCTIONS,
    tools=[classify_intent],
    handoffs=[agronomy_agent, pest_doctor_agent, market_finance_agent],
)

# Export all agents
__all__ = [
    "triage_agent",
    "agronomy_agent", 
    "pest_doctor_agent",
    "market_finance_agent",
    "classify_intent",
]