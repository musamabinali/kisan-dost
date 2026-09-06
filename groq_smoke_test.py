import asyncio
import os
from agents import Runner, set_default_openai_key
from specialists import triage_agent

print('MODEL=', os.getenv('OPENAI_MODEL'))
set_default_openai_key(os.getenv('OPENAI_API_KEY'))

async def main():
    result = await Runner.run(
        triage_agent,
        'What should I plant on 5 acres in Faisalabad this Rabi season?',
        session='groq_test_1',
    )
    print('FINAL_OUTPUT_START')
    print((result.final_output or '<NO_OUTPUT>')[:1200])
    print('FINAL_OUTPUT_END')

asyncio.run(main())
