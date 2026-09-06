"""Pest & Disease Doctor Agent."""

from config.prompts.system_prompts import PEST_DOCTOR_AGENT_INSTRUCTIONS
from tools import pest_disease_doctor
from models import PestDiagnosis
from .base import create_agent

pest_doctor_agent = create_agent(
    name="pest_doctor_agent",
    instructions=PEST_DOCTOR_AGENT_INSTRUCTIONS,
    tools=[pest_disease_doctor],
)