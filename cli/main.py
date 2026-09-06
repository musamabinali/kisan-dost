"""Main CLI entry point for Kisan Dost."""

import asyncio
import os
from pathlib import Path

import click
from dotenv import load_dotenv

# Load environment variables FIRST from the Kisan Dost project root, not whichever directory
# the terminal happens to be in.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Setup LLM provider BEFORE importing agents
from config import settings
if settings.llm_provider == "groq" and settings.groq_api_key:
    os.environ["OPENAI_API_KEY"] = settings.groq_api_key
    os.environ["OPENAI_BASE_URL"] = "https://api.groq.com/openai/v1"
elif settings.openai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key

# Now import agents and other modules
from rich.console import Console
from cli.console import KisanDostConsole
from cli.commands import CommandHandler
from cli.urdu_renderer import UrduRenderer
from agents import Runner, set_default_openai_key
from sessions import session_manager
from models import FarmerProfile, FarmContext
import logging

logger = logging.getLogger(__name__)

@click.command()
@click.option("--farmer-id", "-f", help="Farmer ID to load existing session")
@click.option("--language", "-l", type=click.Choice(["en", "ur", "roman_ur"]), default="en", help="Interface language")
@click.option("--district", "-d", help="District (for new session)")
@click.option("--acres", "-a", type=float, help="Land size in acres (for new session)")
@click.option("--crop", "-c", help="Current crop (for new session)")
@click.option("--debug", is_flag=True, help="Enable debug logging")
def main(farmer_id: str, language: str, district: str, acres: float, crop: str, debug: bool):
    """Kisan Dost - AI Agronomy Agent for Pakistani Farmers"""
    
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run async main
    asyncio.run(run_kisan_dost(farmer_id, language, district, acres, crop))

async def run_kisan_dost(farmer_id: str, language: str, district: str, acres: float, crop: str):
    """Main async entry point."""
    
    # Import agents here to avoid circular imports
    from specialists import triage_agent
    from sessions import ContextManager
    
    # Initialize console
    kisan_console = KisanDostConsole(language=language)
    urdu_renderer = UrduRenderer(mode=language)
    cmd_handler = CommandHandler(kisan_console)
    
    # Print header
    kisan_console.print_header()
    
    # Load or create session
    session_id = None
    profile = None
    context = None
    
    if farmer_id:
        # Try to load existing session
        existing = session_manager.get_session_by_farmer(farmer_id)
        if existing:
            session_id = existing["session_id"]
            ctx_manager = ContextManager(session_id)
            profile = ctx_manager.get_profile()
            context = ctx_manager.get_context()
            cmd_handler.current_session_id = session_id
            cmd_handler.farmer_profile = profile
            cmd_handler.farm_context = context
            kisan_console.print_info(f"Loaded existing session: {session_id}")
        else:
            kisan_console.print_warning(f"No existing session for farmer {farmer_id}")
    
    if not session_id:
        # Create new session if params provided
        if district and acres:
            profile = FarmerProfile(
                farmer_id=farmer_id or "farmer_001",
                district=district,
                province="punjab",  # Default
                preferred_language=language
            )
            context = FarmContext(
                land_size_acres=acres,
                soil_type="loam",  # Default
                season="rabi",  # Default
                water_availability="canal",  # Default
                current_crop=crop
            )
            session_id = session_manager.create_session(
                farmer_id=profile.farmer_id,
                farmer_profile=profile,
                farm_context=context
            )
            cmd_handler.current_session_id = session_id
            cmd_handler.farmer_profile = profile
            cmd_handler.farm_context = context
            kisan_console.print_info(f"Created new session: {session_id}")
        else:
            # Interactive session creation
            kisan_console.print_info("No session loaded. Use '/session new' to create one.")
    
    # Print greeting
    kisan_console.print_greeting(profile.name if profile else None)
    
    # Show context summary if available
    if context:
        ctx_manager = ContextManager(session_id) if session_id else None
        if ctx_manager:
            summary = ctx_manager.format_context_summary()
            kisan_console.print_info(f"Context: {summary}")
    
    kisan_console.print_info("Type '/help' for commands. Ask me anything about your farm!")
    kisan_console.console.print()
    
    # Main conversation loop
    try:
        while True:
            # Get user input
            user_input = kisan_console.get_input()
            
            if not user_input.strip():
                continue
            
            # Check for commands
            if user_input.strip().startswith("/"):
                handled = cmd_handler.handle_command(user_input.strip())
                if handled:
                    continue
            
            # Process with agent
            await process_query(user_input, kisan_console, cmd_handler, urdu_renderer)
            
    except KeyboardInterrupt:
        kisan_console.print_info("\nAllah Hafiz! Happy farming! 🌾")
    except SystemExit:
        pass
    except Exception as e:
        logger.exception("Fatal error in main loop")
        kisan_console.print_error(f"Fatal error: {e}")

async def process_query(
    user_input: str,
    kisan_console: KisanDostConsole,
    cmd_handler: CommandHandler,
    urdu_renderer: UrduRenderer
):
    """Process a user query through the agent system."""
    from agents import Runner
    from specialists import triage_agent
    from sessions import ContextManager
    
    if not cmd_handler.current_session_id:
        kisan_console.print_error("No active session. Use '/session new' to create one.")
        return
    
    # Build context for agent
    ctx_manager = ContextManager(cmd_handler.current_session_id)
    agent_context = ctx_manager.build_agent_context()
    
    # Add session context to input
    context_str = ""
    if agent_context:
        context_items = []
        if agent_context.get("district"):
            context_items.append(f"District: {agent_context['district']}")
        if agent_context.get("land_size_acres"):
            context_items.append(f"Land: {agent_context['land_size_acres']} acres")
        if agent_context.get("current_crop"):
            context_items.append(f"Crop: {agent_context['current_crop']}")
        if agent_context.get("crop_stage"):
            context_items.append(f"Stage: {agent_context['crop_stage']}")
        
        if context_items:
            context_str = f"[Context: {' | '.join(context_items)}] "
    
    full_input = f"{context_str}{user_input}"
    
    try:
        # Run agent
        result = await Runner.run(
            triage_agent,
            full_input,
            context=agent_context,
        )
        
        # Print result
        output = result.final_output
        
        # Translate if needed
        if kisan_console.urdu_mode:
            output = urdu_renderer.translate(output)
        
        kisan_console.console.print()
        kisan_console.console.print(output)
        kisan_console.console.print()
        
        # Save to session
        session_manager.add_message(
            cmd_handler.current_session_id,
            "user",
            user_input
        )
        session_manager.add_message(
            cmd_handler.current_session_id,
            "assistant",
            output,
            agent_name=getattr(result, 'last_agent', None) and result.last_agent.name
        )
        
        # Update farmer query count
        if cmd_handler.farmer_profile:
            cmd_handler.farmer_profile.total_queries += 1
            session_manager.update_session(
                cmd_handler.current_session_id,
                farmer_profile=cmd_handler.farmer_profile
            )
        
    except Exception as e:
        logger.exception("Error processing query")
        kisan_console.print_error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()