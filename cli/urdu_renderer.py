"""Urdu text rendering for terminal."""

from config import (
    URDU_PROMPTS, CROP_URDU_NAMES, PEST_URDU_NAMES,
    SOIL_URDU_NAMES, SEASON_URDU_NAMES, WATER_URDU_NAMES, URDU_TERMS
)
from typing import Optional, Literal

class UrduRenderer:
    """Renders text in Urdu script or Roman Urdu."""
    
    def __init__(self, mode: str = "roman_ur"):
        """
        Args:
            mode: "ur" for Urdu script, "roman_ur" for Roman Urdu, "en" for English
        """
        self.mode = mode
    
    def translate(self, english_text: str, context: str = "") -> str:
        """Translate English text to Urdu/Roman Urdu."""
        if self.mode == "en":
            return english_text
        
        # Simple keyword replacement - in production use proper translation
        text = english_text
        
        # Translate crop names
        for eng, urdu in CROP_URDU_NAMES.items():
            text = text.replace(eng, urdu)
            text = text.replace(eng.title(), urdu)
            text = text.replace(eng.upper(), urdu)
        
        # Translate pest names
        for eng, urdu in PEST_URDU_NAMES.items():
            text = text.replace(eng, urdu)
            text = text.replace(eng.title(), urdu)
        
        # Translate soil types
        for eng, urdu in SOIL_URDU_NAMES.items():
            text = text.replace(eng, urdu)
        
        # Translate seasons
        for eng, urdu in SEASON_URDU_NAMES.items():
            text = text.replace(eng, urdu)
        
        # Translate water availability
        for eng, urdu in WATER_URDU_NAMES.items():
            text = text.replace(eng, urdu)
        
        # Translate common terms
        for eng, urdu in URDU_TERMS.items():
            text = text.replace(f" {eng} ", f" {urdu} ")
            text = text.replace(f" {eng}.", f" {urdu}.")
            text = text.replace(f" {eng},", f" {urdu},")
        
        return text
    
    def get_prompt(self, key: str) -> str:
        """Get a prompt in current language."""
        if self.mode == "en":
            # Return English version from URDU_PROMPTS (need to add)
            return key.replace("_", " ").title()
        
        if self.mode == "ur":
            return URDU_PROMPTS.get(key, key)
        else:  # roman_ur
            return URDU_PROMPTS.get(f"{key}_roman", URDU_PROMPTS.get(key, key))
    
    def format_crop_name(self, crop: str) -> str:
        """Format crop name in current language."""
        if self.mode == "en":
            return crop.title()
        
        return CROP_URDU_NAMES.get(crop.lower(), crop.title())
    
    def format_pest_name(self, pest: str) -> str:
        """Format pest name in current language."""
        if self.mode == "en":
            return pest.replace("_", " ").title()
        
        return PEST_URDU_NAMES.get(pest.lower(), pest.replace("_", " ").title())
    
    def format_soil_type(self, soil: str) -> str:
        """Format soil type in current language."""
        if self.mode == "en":
            return soil.replace("_", " ").title()
        
        return SOIL_URDU_NAMES.get(soil.lower(), soil.replace("_", " ").title())
    
    def format_season(self, season: str) -> str:
        """Format season in current language."""
        if self.mode == "en":
            return season.title()
        
        return SEASON_URDU_NAMES.get(season.lower(), season.title())
    
    def format_water_availability(self, water: str) -> str:
        """Format water availability in current language."""
        if self.mode == "en":
            return water.replace("_", " ").title()
        
        return WATER_URDU_NAMES.get(water.lower(), water.replace("_", " ").title())
    
    def format_number(self, number: float, unit: str = "") -> str:
        """Format number with Urdu digits if in Urdu mode."""
        if self.mode == "ur":
            # Convert to Urdu digits
            urdu_digits = "۰۱۲۳۴۵۶۷۸۹"
            english_digits = "0123456789"
            trans = str.maketrans(english_digits, urdu_digits)
            num_str = f"{number:,.1f}".translate(trans)
            return f"{num_str} {unit}"
        return f"{number:,.1f} {unit}"