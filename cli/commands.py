"""CLI command handlers."""

from typing import Optional, Literal
from cli.console import KisanDostConsole
from models import FarmerProfile, FarmContext
from sessions import session_manager, ContextManager
import logging

logger = logging.getLogger(__name__)

class CommandHandler:
    """Handles slash commands in the CLI."""
    
    def __init__(self, console: KisanDostConsole):
        self.console = console
        self.current_session_id: Optional[str] = None
        self.farmer_profile: Optional[FarmerProfile] = None
        self.farm_context: Optional[FarmContext] = None
    
    def handle_command(self, command: str) -> bool:
        """
        Handle a slash command.
        Returns True if command was handled, False otherwise.
        """
        parts = command.strip().split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        handlers = {
            "/help": self.cmd_help,
            "/lang": self.cmd_lang,
            "/profile": self.cmd_profile,
            "/context": self.cmd_context,
            "/history": self.cmd_history,
            "/reset": self.cmd_reset,
            "/quit": self.cmd_quit,
            "/exit": self.cmd_quit,
            "/session": self.cmd_session,
        }
        
        handler = handlers.get(cmd)
        if handler:
            return handler(args)
        
        return False
    
    def cmd_help(self, args: list) -> bool:
        self.console.print_help()
        return True
    
    def cmd_lang(self, args: list) -> bool:
        if not args:
            self.console.print_info(f"Current language: {self.console.language}")
            return True
        
        lang = args[0].lower()
        if lang in ["en", "ur", "roman_ur"]:
            self.console.language = lang
            self.console.urdu_mode = lang in ("ur", "roman_ur")
            self.console.print_info(f"Language changed to: {lang}")
        else:
            self.console.print_error("Invalid language. Use: en, ur, or roman_ur")
        return True
    
    def cmd_profile(self, args: list) -> bool:
        if self.farmer_profile:
            self.console.print_farmer_profile(self.farmer_profile)
        else:
            self.console.print_warning("No farmer profile loaded. Use /session to load one.")
        return True
    
    def cmd_context(self, args: list) -> bool:
        if self.farm_context:
            self.console.print_farm_context(self.farm_context)
        else:
            self.console.print_warning("No farm context loaded. Use /session to load one.")
        return True
    
    def cmd_history(self, args: list) -> bool:
        if not self.current_session_id:
            self.console.print_warning("No active session.")
            return True
        
        messages = session_manager.get_messages(self.current_session_id, 20)
        if not messages:
            self.console.print_info("No conversation history.")
            return True
        
        from rich.table import Table
        table = Table(title="Conversation History", border_style="cyan")
        table.add_column("Role", style="bold")
        table.add_column("Agent")
        table.add_column("Content")
        
        for msg in messages:
            role = msg.get("role", "")
            agent = msg.get("agent_name", "") or ""
            content = msg.get("content", "")[:100] + ("..." if len(msg.get("content", "")) > 100 else "")
            table.add_row(role, agent, content)
        
        self.console.console.print(table)
        return True
    
    def cmd_reset(self, args: list) -> bool:
        if self.console.confirm("Reset current conversation? This will create a new session."):
            self.current_session_id = None
            self.farmer_profile = None
            self.farm_context = None
            self.console.print_info("Conversation reset. Starting fresh...")
        return True
    
    def cmd_quit(self, args: list) -> bool:
        self.console.print_info("Allah Hafiz! Happy farming! 🌾")
        raise SystemExit(0)
    
    def cmd_session(self, args: list) -> bool:
        if not args:
            # Show current session
            if self.current_session_id:
                self.console.print_info(f"Current session: {self.current_session_id}")
                stats = session_manager.get_stats()
                self.console.print_info(f"Total sessions: {stats['total_sessions']}, Active: {stats['active_sessions']}")
            else:
                self.console.print_warning("No active session.")
            return True
        
        subcmd = args[0]
        
        if subcmd == "new":
            self._create_new_session(args[1:] if len(args) > 1 else [])
        elif subcmd == "load":
            self._load_session(args[1] if len(args) > 1 else None)
        elif subcmd == "list":
            self._list_sessions()
        else:
            self.console.print_error(f"Unknown session command: {subcmd}. Use: new, load, list")
        
        return True
    
    def _create_new_session(self, args: list):
        """Create a new farmer session interactively."""
        self.console.print_info("Creating new farmer profile...")
        
        # Get farmer ID (phone or CNIC hash)
        farmer_id = Prompt.ask("Farmer ID (phone/CNIC)", default="farmer_001")
        
        # Check existing
        existing = session_manager.get_session_by_farmer(farmer_id)
        if existing:
            if self.console.confirm(f"Farmer {farmer_id} has existing session. Load it?"):
                self._load_session(existing["session_id"])
                return
        
        # Get profile info
        name = Prompt.ask("Farmer name (optional)", default="")
        district = Prompt.ask("District", default="faisalabad")
        province = Prompt.ask("Province", choices=["punjab", "sindh", "kpk", "balochistan", "gilgit_baltistan", "azad_kashmir"], default="punjab")
        language = Prompt.ask("Preferred language", choices=["en", "ur", "roman_ur"], default="en")
        
        profile = FarmerProfile(
            farmer_id=farmer_id,
            name=name or None,
            district=district,
            province=province,
            preferred_language=language
        )
        
        # Get farm context
        self.console.print_info("Now entering farm context...")
        land_size = float(Prompt.ask("Land size (acres)", default="5"))
        soil_type = Prompt.ask("Soil type", choices=["clay", "loam", "sandy", "silt", "clay_loam", "sandy_loam"], default="loam")
        season = Prompt.ask("Season", choices=["rabi", "kharif", "zaid"], default="rabi")
        water = Prompt.ask("Water availability", choices=["rainfed", "limited_irrigation", "full_irrigation", "canal", "tubewell"], default="canal")
        
        context = FarmContext(
            land_size_acres=land_size,
            soil_type=soil_type,
            season=season,
            water_availability=water
        )
        
        # Create session
        self.current_session_id = session_manager.create_session(
            farmer_id=farmer_id,
            farmer_profile=profile,
            farm_context=context
        )
        
        self.farmer_profile = profile
        self.farm_context = context
        
        self.console.print_info(f"Session created: {self.current_session_id}")
        self.console.print_farmer_profile(profile)
        self.console.print_farm_context(context)
    
    def _load_session(self, session_id: Optional[str]):
        """Load an existing session."""
        if not session_id:
            # List available sessions for this farmer
            if self.farmer_profile:
                existing = session_manager.get_session_by_farmer(self.farmer_profile.farmer_id)
                if existing:
                    session_id = existing["session_id"]
        
        if not session_id:
            self.console.print_error("No session ID provided and no default found.")
            return
        
        session = session_manager.get_session(session_id)
        if not session:
            self.console.print_error(f"Session {session_id} not found or expired.")
            return
        
        self.current_session_id = session_id
        
        # Restore profile and context
        ctx_manager = ContextManager(session_id)
        self.farmer_profile = ctx_manager.get_profile()
        self.farm_context = ctx_manager.get_context()
        
        self.console.print_info(f"Loaded session: {session_id}")
        if self.farmer_profile:
            self.console.print_farmer_profile(self.farmer_profile)
        if self.farm_context:
            self.console.print_farm_context(self.farm_context)
    
    def _list_sessions(self):
        """List all sessions (simplified)."""
        stats = session_manager.get_stats()
        self.console.print_info(f"Total sessions: {stats['total_sessions']}, Active: {stats['active_sessions']}")