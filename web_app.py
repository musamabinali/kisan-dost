"""Minimal web frontend for Kisan Dost.

This keeps the proven CLI backend intact and adds a thin API + HTML layer on top.
It intentionally reuses the same session manager and agent runner instead of rewriting
core logic.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

from config import settings

if settings.llm_provider == "groq" and settings.groq_api_key:
    os.environ["OPENAI_API_KEY"] = settings.groq_api_key
    os.environ["OPENAI_BASE_URL"] = "https://api.groq.com/openai/v1"
elif settings.openai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key

from agents import Runner
from models import (
    FarmerProfile,
    FarmContext,
    Language,
    Province,
    Season,
    SoilType,
    WaterAvailability,
)
from sessions import session_manager
from sessions.context import ContextManager
from specialists import triage_agent

app = FastAPI(title="Kisan Dost", version="0.1.0")
app.mount("/static", StaticFiles(directory=PROJECT_ROOT / "static"), name="static")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    farmer_id: str = "web_farmer"
    district: str = "Multan"
    acres: float = Field(default=5.0, gt=0)
    crop: str | None = None
    soil_type: str = "loam"
    season: str = "rabi"
    water_availability: str = "canal"
    language: str = "en"


def _safe_enum(value: str, enum_type: type[Any], fallback: Any) -> Any:
    if not value:
        return fallback
    cleaned = value.strip().lower().replace(" ", "_")
    try:
        return enum_type(cleaned)
    except ValueError:
        return fallback


def _build_context_prompt(agent_context: dict[str, Any], user_message: str) -> str:
    context_items: list[str] = []
    for key, label in {
        "district": "District",
        "land_size_acres": "Land",
        "current_crop": "Crop",
        "crop_stage": "Stage",
        "season": "Season",
        "soil_type": "Soil",
        "water_availability": "Water",
    }.items():
        value = agent_context.get(key)
        if value:
            context_items.append(f"{label}: {value}")

    prefix = f"[Context: {' | '.join(context_items)}] " if context_items else ""
    return f"{prefix}{user_message}"


async def _ask_agent(question: str, session_id: str) -> str:
    context_manager = ContextManager(session_id)
    agent_context = context_manager.build_agent_context()
    result = await Runner.run(
        triage_agent,
        _build_context_prompt(agent_context, question),
        context=agent_context,
    )
    return result.final_output


@app.get("/")
async def serve_index() -> FileResponse:
    return FileResponse(PROJECT_ROOT / "templates" / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(request: ChatRequest) -> dict[str, Any]:
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    profile = FarmerProfile(
        farmer_id=request.farmer_id,
        name=request.farmer_id,
        district=request.district,
        province=Province.PUNJAB,
        preferred_language=_safe_enum(request.language, Language, Language.ENGLISH),
    )
    context = FarmContext(
        land_size_acres=request.acres,
        soil_type=_safe_enum(request.soil_type, SoilType, SoilType.LOAM),
        season=_safe_enum(request.season, Season, Season.RABI),
        water_availability=_safe_enum(
            request.water_availability,
            WaterAvailability,
            WaterAvailability.CANAL,
        ),
        current_crop=request.crop,
    )

    existing = session_manager.get_session_by_farmer(request.farmer_id)
    if existing:
        session_id = existing["session_id"]
        session_manager.update_session(session_id, farmer_profile=profile, farm_context=context)
    else:
        session_id = session_manager.create_session(
            farmer_id=request.farmer_id,
            farmer_profile=profile,
            farm_context=context,
        )

    response_text = await _ask_agent(request.message, session_id)

    session_manager.add_message(session_id, "user", request.message)
    session_manager.add_message(
        session_id,
        "assistant",
        response_text,
        agent_name="triage_agent",
    )

    return {"response": response_text, "session_id": session_id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("web_app:app", host="0.0.0.0", port=8000, reload=False)
