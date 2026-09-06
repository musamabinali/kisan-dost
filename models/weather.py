"""Weather and irrigation models."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date, datetime
from enum import Enum

class WeatherCondition(str, Enum):
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    LIGHT_RAIN = "light_rain"
    MODERATE_RAIN = "moderate_rain"
    HEAVY_RAIN = "heavy_rain"
    THUNDERSTORM = "thunderstorm"
    FOG = "fog"
    DUST_STORM = "dust_storm"
    HEATWAVE = "heatwave"
    FROST = "frost"

class DailyForecast(BaseModel):
    date: date
    temp_max_c: float
    temp_min_c: float
    humidity_percent: float
    precipitation_mm: float
    wind_speed_kmh: float
    condition: WeatherCondition
    uv_index: Optional[float] = None

class IrrigationAdvice(BaseModel):
    should_irrigate: bool
    reason: str
    recommended_date: Optional[date] = None
    water_amount_mm: float = 0
    method: Literal["flood", "furrow", "sprinkler", "drip", "skip"]
    urgency: Literal["low", "medium", "high", "critical"]
    crop_stage_context: str
    weather_risk: Optional[str] = None

class WeatherForecast(BaseModel):
    district: str
    latitude: float
    longitude: float
    current_temp_c: float
    current_humidity: float
    forecast: list[DailyForecast] = Field(..., min_length=7, max_length=14)
    irrigation_advice: IrrigationAdvice
    alerts: list[str] = Field(default_factory=list)
    source: Literal["open_meteo", "mock"] = "mock"
    fetched_at: datetime = Field(default_factory=datetime.now)