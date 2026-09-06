"""Weather service using Open-Meteo API."""

import httpx
import logging
from datetime import date, datetime
from typing import Optional, Literal
from config import settings
from config.constants import DISTRICT_COORDS

logger = logging.getLogger(__name__)

class WeatherService:
    """Open-Meteo weather service client."""
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.timeout = httpx.Timeout(settings.open_meteo_timeout)
    
    async def get_coordinates(self, district: str) -> tuple[float, float] | None:
        """Get lat/lon for a district."""
        # Check local cache first
        if district.lower() in DISTRICT_COORDS:
            return DISTRICT_COORDS[district.lower()]
        
        # Try geocoding API
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    self.geocoding_url,
                    params={"name": district, "country": "Pakistan", "count": 1}
                )
                resp.raise_for_status()
                data = resp.json()
                
                if data.get("results"):
                    result = data["results"][0]
                    return (result["latitude"], result["longitude"])
        except Exception as e:
            logger.warning(f"Geocoding failed for {district}: {e}")
        
        return None
    
    async def get_forecast(
        self, 
        latitude: float, 
        longitude: float, 
        days: int = 7
    ) -> dict | None:
        """Get weather forecast."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    self.base_url,
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "current": "temperature_2m,relative_humidity_2m",
                        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean,windspeed_10m_max,weathercode",
                        "timezone": "Asia/Karachi",
                        "forecast_days": min(days, 14),
                    }
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return None
    
    async def get_historical(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date
    ) -> dict | None:
        """Get historical weather."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://archive-api.open-meteo.com/v1/archive",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                        "timezone": "Asia/Karachi",
                    }
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"Historical weather API error: {e}")
            return None


# Global service instance
weather_service = WeatherService()