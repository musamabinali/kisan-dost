"""Agronomy Agent - handles crop advice, fertilizer, irrigation."""

from config.prompts.system_prompts import AGRONOMY_AGENT_INSTRUCTIONS
from tools import crop_advisor, fertilizer_calculator, irrigation_weather
from models import CropPlan, FertilizerPlan, WeatherForecast
from .base import create_agent

agronomy_agent = create_agent(
    name="agronomy_agent",
    instructions=AGRONOMY_AGENT_INSTRUCTIONS,
    tools=[crop_advisor, fertilizer_calculator, irrigation_weather],
    # output_type can be set per tool, not at agent level in current SDK
)