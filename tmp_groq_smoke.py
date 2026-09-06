import asyncio
import os

os.environ.setdefault("GROQ_API_KEY", "your_groq_key_here")
os.environ.setdefault("GROQ_MODEL", "llama-3.3-70b-versatile")

from agents import Runner
from agents.memory.sqlite_session import SQLiteSession
from specialists import triage_agent


async def main():
    session = SQLiteSession(
        session_id="smoke_kisan_test_2",
        db_path=r"D:\agents\AGENTIC AI HACKATHON • TERMINAL AGENT CHALLENGE\kisan-dost\data\sessions.db",
    )
    result = await Runner.run(
        triage_agent,
        "What crop should I plant in Faisalabad this Rabi season on 5 acres?",
        session=session,
    )
    print("FINAL_OUTPUT_START")
    print((result.final_output or "<NO_OUTPUT>")[:1200])
    print("FINAL_OUTPUT_END")


if __name__ == "__main__":
    asyncio.run(main())
