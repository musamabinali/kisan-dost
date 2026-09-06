"""Base agent configuration."""

import os
from agents import Agent, ModelSettings, Runner, set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from config.prompts.system_prompts import *
from config import settings
from tools import ALL_TOOLS


def _provider_safe_model_settings() -> ModelSettings:
    """Avoid provider-specific fields that are rejected by Groq and similar OpenAI-compatible APIs.

    Groq enforces a low output-token quota on some models, so we cap the generation length to keep
    requests within the provider limits while still producing useful agronomy advice.
    """
    return ModelSettings(max_tokens=300, verbosity=None, reasoning=None)


def _build_llm_model():
    """Build the model object for the selected provider. Supports Groq/Gemini via OpenAI-compatible endpoints."""
    groq_key = os.getenv("GROQ_API_KEY") or settings.groq_api_key
    gemini_key = os.getenv("GEMINI_API_KEY") or settings.gemini_api_key
    openai_key = os.getenv("OPENAI_API_KEY") or settings.openai_api_key

    if groq_key:
        set_tracing_disabled(True)
        groq_model = os.getenv("GROQ_MODEL") or os.getenv("OPENAI_MODEL") or settings.openai_model or "llama-3.3-70b-versatile"
        client = AsyncOpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1",
        )
        return OpenAIChatCompletionsModel(model=groq_model, openai_client=client)

    if gemini_key:
        set_tracing_disabled(True)
        gemini_model = os.getenv("GEMINI_MODEL") or os.getenv("OPENAI_MODEL") or settings.openai_model or "gemini-2.0-flash"
        client = AsyncOpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        return OpenAIChatCompletionsModel(model=gemini_model, openai_client=client)

    if openai_key:
        openai_base = os.getenv("OPENAI_BASE_URL") or settings.openai_base_url
        if openai_base:
            set_tracing_disabled(True)
            client = AsyncOpenAI(
                api_key=openai_key,
                base_url=openai_base,
            )
            return OpenAIChatCompletionsModel(
                model=os.getenv("OPENAI_MODEL") or settings.openai_model,
                openai_client=client,
            )
        return os.getenv("OPENAI_MODEL") or settings.openai_model

    return settings.openai_model


def create_agent(
    name: str,
    instructions: str,
    tools: list,
    model: str | None = None,
    output_type=None,
    handoffs: list | None = None,
) -> Agent:
    """Create an agent with common configuration."""
    resolved_model = model or _build_llm_model()
    return Agent(
        name=name,
        instructions=instructions,
        tools=tools,
        model=resolved_model,
        model_settings=_provider_safe_model_settings(),
        handoffs=handoffs or [],
        output_type=output_type,
    )

class BaseAgent:
    """Base class for all Kisan Dost agents."""
    
    def __init__(self, name: str, instructions: str, tools: list, output_type=None):
        self.agent = create_agent(name, instructions, tools, output_type=output_type)
    
    async def run(self, input_text: str, context=None, session=None):
        """Run the agent with input."""
        return await Runner.run(self.agent, input_text, context=context, session=session)