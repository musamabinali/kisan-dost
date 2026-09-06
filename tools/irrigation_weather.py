"""Irrigation & Weather Tool."""

from agents import function_tool
from models import WeatherForecast, IrrigationAdvice, DailyForecast, WeatherCondition, FarmContext
from config.constants import CROP_WATER_REQUIREMENTS
from config import settings
import httpx
import logging
from datetime import date, datetime, timedelta
from typing import Optional, Literal

logger = logging.getLogger(__name__)

# District coordinates for major Pakistani districts
DISTRICT_COORDS = {
    "faisalabad": (31.45, 73.13),
    "multan": (30.15, 71.45),
    "lahore": (31.55, 74.35),
    "gujranwala": (32.16, 74.19),
    "sargodha": (32.08, 72.67),
    "sahiwal": (30.67, 73.11),
    "bahawalpur": (29.39, 71.68),
    "dg_khan": (29.90, 70.63),
    "rawalpindi": (33.60, 73.06),
    "sialkot": (32.49, 74.53),
    "karachi": (24.86, 67.01),
    "hyderabad": (25.39, 68.37),
    "peshawar": (34.01, 71.58),
    "quetta": (30.18, 66.99),
    "islamabad": (33.68, 73.05),
}

# Crop coefficients (Kc) by stage
CROP_KC = {
    "wheat": {"sowing": 0.3, "vegetative": 0.7, "flowering": 1.15, "grain_fill": 0.7, "harvest": 0.2},
    "cotton": {"sowing": 0.35, "vegetative": 0.7, "flowering": 1.15, "grain_fill": 1.1, "harvest": 0.5},
    "rice": {"sowing": 1.0, "vegetative": 1.1, "flowering": 1.2, "grain_fill": 1.0, "harvest": 0.4},
    "maize": {"sowing": 0.3, "vegetative": 0.7, "flowering": 1.2, "grain_fill": 0.9, "harvest": 0.4},
    "sugarcane": {"sowing": 0.4, "vegetative": 1.0, "flowering": 1.25, "grain_fill": 1.0, "harvest": 0.6},
    "chickpea": {"sowing": 0.3, "vegetative": 0.6, "flowering": 1.0, "grain_fill": 0.5, "harvest": 0.2},
    "default": {"sowing": 0.4, "vegetative": 0.8, "flowering": 1.1, "grain_fill": 0.8, "harvest": 0.3},
}

@function_tool(strict_mode=False)
async def irrigation_weather(
    farm_context: FarmContext,
    district: str,
    days_ahead: int = 7
) -> WeatherForecast:
    """
    Given the forecast and crop stage, advise irrigation timing and warn about frost or heatwave risk.
    
    Args:
        farm_context: Current farm context (crop, stage, last irrigation, soil, water availability)
        district: District name for weather lookup
        days_ahead: Days of forecast to fetch (default 7)
        
    Returns:
        WeatherForecast with irrigation advice and alerts.
    """
    try:
        district_lower = district.lower().strip()
        coords = DISTRICT_COORDS.get(district_lower)
        
        if not coords:
            # Default to Faisalabad
            coords = (31.45, 73.13)
            logger.warning(f"No coords for {district}, using Faisalabad")
        
        lat, lon = coords
        
        # Fetch weather
        if settings.use_real_apis:
            forecast_data = await _fetch_open_meteo(lat, lon, days_ahead)
            source = "open_meteo"
        else:
            forecast_data = _mock_forecast(lat, lon, days_ahead)
            source = "mock"
        
        # Generate irrigation advice
        irrigation = _generate_irrigation_advice(farm_context, forecast_data)
        
        # Check for alerts
        alerts = _check_weather_alerts(forecast_data, farm_context)
        
        return WeatherForecast(
            district=district,
            latitude=lat,
            longitude=lon,
            current_temp_c=forecast_data["current"]["temperature_2m"],
            current_humidity=forecast_data["current"]["relative_humidity_2m"],
            forecast=forecast_data["daily"],
            irrigation_advice=irrigation,
            alerts=alerts,
            source=source,
            fetched_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Irrigation weather error: {e}")
        return _error_forecast(district, str(e))

async def _fetch_open_meteo(lat: float, lon: float, days: int) -> dict:
    """Fetch weather from Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean,windspeed_10m_max,weathercode",
        "timezone": "Asia/Karachi",
        "forecast_days": min(days, 14),
    }
    
    timeout = httpx.Timeout(settings.open_meteo_timeout)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
    
    return _parse_open_meteo(data)

def _parse_open_meteo(data: dict) -> dict:
    """Parse Open-Meteo response into our format."""
    current = data.get("current", {})
    daily = data.get("daily", {})
    
    forecasts = []
    for i in range(len(daily.get("time", []))):
        weather_code = daily.get("weathercode", [0])[i] if i < len(daily.get("weathercode", [])) else 0
        condition = _weather_code_to_condition(weather_code, 
                                               daily.get("precipitation_sum", [0])[i] if i < len(daily.get("precipitation_sum", [])) else 0,
                                               daily.get("temperature_2m_max", [0])[i] if i < len(daily.get("temperature_2m_max", [])) else 0)
        
        forecasts.append(DailyForecast(
            date=date.fromisoformat(daily["time"][i]),
            temp_max_c=daily["temperature_2m_max"][i],
            temp_min_c=daily["temperature_2m_min"][i],
            humidity_percent=daily.get("relative_humidity_2m_mean", [50])[i] if i < len(daily.get("relative_humidity_2m_mean", [])) else 50,
            precipitation_mm=daily.get("precipitation_sum", [0])[i] if i < len(daily.get("precipitation_sum", [])) else 0,
            wind_speed_kmh=daily.get("windspeed_10m_max", [10])[i] if i < len(daily.get("windspeed_10m_max", [])) else 10,
            condition=condition,
            uv_index=None
        ))
    
    return {
        "current": {
            "temperature_2m": current.get("temperature_2m", 25),
            "relative_humidity_2m": current.get("relative_humidity_2m", 60)
        },
        "daily": forecasts
    }

def _weather_code_to_condition(code: int, precip_mm: float, temp_max: float) -> WeatherCondition:
    """Convert WMO weather code to our condition enum."""
    if code in [0]: return WeatherCondition.CLEAR
    if code in [1, 2]: return WeatherCondition.PARTLY_CLOUDY
    if code in [3]: return WeatherCondition.CLOUDY
    if code in [45, 48]: return WeatherCondition.FOG
    if code in [51, 53, 55]: return WeatherCondition.LIGHT_RAIN
    if code in [56, 57, 61, 63, 65]: return WeatherCondition.MODERATE_RAIN
    if code in [66, 67, 80, 81, 82]: return WeatherCondition.HEAVY_RAIN
    if code in [95, 96, 99]: return WeatherCondition.THUNDERSTORM
    if temp_max > 42: return WeatherCondition.HEATWAVE
    if temp_max < 5: return WeatherCondition.FROST
    return WeatherCondition.CLEAR

def _mock_forecast(lat: float, lon: float, days: int) -> dict:
    """Generate mock forecast for testing."""
    import random
    base_date = date.today()
    forecasts = []
    
    for i in range(days):
        d = base_date + timedelta(days=i)
        temp_max = random.randint(28, 42)
        temp_min = random.randint(15, 25)
        humidity = random.randint(40, 80)
        precip = random.choice([0, 0, 0, 0, 2, 5, 10, 20])
        wind = random.randint(5, 25)
        
        if precip > 10:
            condition = WeatherCondition.MODERATE_RAIN
        elif precip > 0:
            condition = WeatherCondition.LIGHT_RAIN
        elif temp_max > 42:
            condition = WeatherCondition.HEATWAVE
        elif temp_max < 8:
            condition = WeatherCondition.FROST
        else:
            condition = WeatherCondition.CLEAR
        
        forecasts.append(DailyForecast(
            date=d,
            temp_max_c=temp_max,
            temp_min_c=temp_min,
            humidity_percent=humidity,
            precipitation_mm=precip,
            wind_speed_kmh=wind,
            condition=condition
        ))
    
    return {
        "current": {"temperature_2m": 30, "relative_humidity_2m": 60},
        "daily": forecasts
    }

def _generate_irrigation_advice(ctx: FarmContext, forecast_data: dict) -> IrrigationAdvice:
    """Generate irrigation advice based on forecast and crop stage."""
    crop = ctx.current_crop or "wheat"
    stage = ctx.crop_stage.value if ctx.crop_stage else "vegetative"
    
    # Get crop water requirement
    crop_water_mm = CROP_WATER_REQUIREMENTS.get(crop, 500)
    kc = CROP_KC.get(crop, CROP_KC["default"]).get(stage, 0.8)
    
    # Calculate ETc (crop evapotranspiration) - simplified
    # Use average of next 3 days
    daily_forecasts = forecast_data["daily"][:3]
    avg_temp = sum(f.temp_max_c for f in daily_forecasts) / len(daily_forecasts)
    avg_humidity = sum(f.humidity_percent for f in daily_forecasts) / len(daily_forecasts)
    total_precip = sum(f.precipitation_mm for f in daily_forecasts)
    
    # Simplified ET0 (reference evapotranspiration) - Hargreaves
    et0 = 0.0023 * (avg_temp + 17.8) * (avg_temp - 10) ** 0.5 * 0.408  # mm/day approx
    etc_daily = et0 * kc
    etc_3day = etc_daily * 3
    
    # Net irrigation requirement
    net_need = max(etc_3day - total_precip, 0)
    
    # Adjust for soil type
    soil_factor = {"clay": 0.8, "clay_loam": 0.9, "loam": 1.0, "sandy_loam": 1.1, "sandy": 1.3, "silt": 0.9}
    net_need *= soil_factor.get(ctx.soil_type.value, 1.0)
    
    # Adjust for water availability
    if ctx.water_availability.value == "rainfed":
        should_irrigate = False
        reason = "Rainfed system - no irrigation available"
        urgency = "low"
    elif ctx.water_availability.value == "limited_irrigation":
        should_irrigate = net_need > 15  # Only if significant deficit
        reason = f"Limited irrigation - need {net_need:.0f}mm over 3 days"
        urgency = "medium" if should_irrigate else "low"
    else:
        should_irrigate = net_need > 10
        reason = f"Crop ETc {etc_3day:.0f}mm - Rain {total_precip:.0f}mm = Net need {net_need:.0f}mm"
        urgency = "high" if net_need > 30 else "medium" if net_need > 15 else "low"
    
    # Check for rain in next 2 days
    rain_soon = any(f.precipitation_mm > 5 for f in daily_forecasts[:2])
    if rain_soon and should_irrigate:
        should_irrigate = False
        reason += " - Rain expected in 48h, delay irrigation"
        urgency = "low"
    
    # Method based on water availability
    method_map = {
        "rainfed": "skip",
        "limited_irrigation": "furrow",
        "full_irrigation": "flood",
        "canal": "flood",
        "tubewell": "sprinkler",
    }
    method = method_map.get(ctx.water_availability.value, "furrow")
    
    return IrrigationAdvice(
        should_irrigate=should_irrigate,
        reason=reason,
        recommended_date=date.today() + timedelta(days=1) if should_irrigate else None,
        water_amount_mm=round(net_need, 1),
        method=method,
        urgency=urgency,
        crop_stage_context=f"{crop} at {stage} stage (Kc={kc})",
        weather_risk=_get_weather_risk(forecast_data)
    )

def _get_weather_risk(forecast_data: dict) -> Optional[str]:
    """Check for weather risks."""
    for f in forecast_data["daily"][:3]:
        if f.condition == WeatherCondition.FROST:
            return "⚠️ FROST RISK: Protect sensitive crops. Irrigate before frost if possible."
        if f.condition == WeatherCondition.HEATWAVE:
            return "⚠️ HEATWAVE RISK: Increase irrigation frequency. Avoid midday spray."
        if f.condition == WeatherCondition.HEAVY_RAIN:
            return "⚠️ HEAVY RAIN EXPECTED: Ensure drainage. Delay fertilizer/pesticide application."
        if f.condition == WeatherCondition.THUNDERSTORM:
            return "⚠️ THUNDERSTORM RISK: Avoid field work. Secure equipment."
    return None

def _check_weather_alerts(forecast_data: dict, ctx: FarmContext) -> list[str]:
    """Generate weather alerts."""
    alerts = []
    risk = _get_weather_risk(forecast_data)
    if risk:
        alerts.append(risk)
    
    # Heatwave alert for flowering stage
    if ctx.crop_stage and ctx.crop_stage.value == "flowering":
        hot_days = sum(1 for f in forecast_data["daily"][:3] if f.temp_max_c > 40)
        if hot_days > 0:
            alerts.append(f"⚠️ {hot_days} day(s) >40°C during flowering - risk of pollen sterility. Ensure adequate soil moisture.")
    
    return alerts

def _error_forecast(district: str, error: str) -> WeatherForecast:
    """Error fallback forecast."""
    return WeatherForecast(
        district=district,
        latitude=0, longitude=0,
        current_temp_c=0, current_humidity=0,
        forecast=[],
        irrigation_advice=IrrigationAdvice(
            should_irrigate=False,
            reason=f"Weather service unavailable: {error}",
            method="skip",
            urgency="low",
            crop_stage_context="Unknown"
        ),
        alerts=[f"Error: {error}"],
        source="error"
    )