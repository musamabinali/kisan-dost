import os, asyncio
from agents import Runner, set_default_openai_key
from specialists import triage_agent

set_default_openai_key(os.getenv('OPENAI_API_KEY'))

async def main():
    result = await Runner.run(
        triage_agent,
        'What should I plant on 5 acres in Faisalabad this Rabi season?',
    )
    print('FINAL_OUTPUT_START')
    print((result.final_output or '<NO_OUTPUT>')[:2000])
    print('FINAL_OUTPUT_END')

asyncio.run(main())
