"""Mandi Price Lookup Tool."""

from agents import function_tool
from models import MandiPrice, PriceTrend
from data import mandi_loader
from config.constants import PUNJAB_MANDIS
import logging
from datetime import date, timedelta
from typing import Optional, Literal

logger = logging.getLogger(__name__)

# District to nearby mandis mapping
DISTRICT_MANDIS = {
    "faisalabad": ["faisalabad_grain_market", "faisalabad_vegetable_market"],
    "multan": ["multan_grain_market", "multan_fruit_market", "multan_cotton_market"],
    "lahore": ["lahore_grain_market", "lahore_vegetable_market"],
    "gujranwala": ["gujranwala_grain_market", "gujranwala_vegetable_market"],
    "sargodha": ["sargodha_grain_market", "sargodha_citrus_market"],
    "sahiwal": ["sahiwal_grain_market", "sahiwal_vegetable_market"],
    "bahawalpur": ["bahawalpur_grain_market", "bahawalpur_cotton_market"],
    "dg_khan": ["dg_khan_grain_market", "dg_khan_cotton_market"],
    "rawalpindi": ["rawalpindi_grain_market", "rawalpindi_vegetable_market"],
    "sialkot": ["sialkot_grain_market", "sialkot_vegetable_market"],
}

# Crop to commodity mapping
CROP_COMMODITY_MAP = {
    "wheat": "wheat",
    "cotton": "cotton",
    "rice": "rice",
    "maize": "maize",
    "sugarcane": "sugarcane",
    "chickpea": "chickpea",
    "lentil": "lentil",
    "mustard": "mustard",
    "onion": "onion",
    "potato": "potato",
    "tomato": "tomato",
    "mungbean": "mungbean",
}

@function_tool(strict_mode=False)
async def mandi_price_lookup(
    crop: str,
    district: str,
    province: str = "punjab",
    days_back: int = 7
) -> dict:
    """
    Return current or typical wholesale prices in nearby mandis so the farmer knows when and where to sell.
    
    Args:
        crop: Crop name (e.g., "wheat", "cotton")
        district: Farmer's district
        province: Province (default: punjab)
        days_back: How many days of price history to consider for trends
        
    Returns:
        Dict with prices, trends, and best sell window advice.
    """
    try:
        crop_lower = crop.lower().strip()
        district_lower = district.lower().strip()
        province_lower = province.lower().strip()
        
        commodity = CROP_COMMODITY_MAP.get(crop_lower, crop_lower)
        
        # Get nearby mandis
        mandis = DISTRICT_MANDIS.get(district_lower, [])
        if not mandis:
            # Fallback to province-level mandis
            if province_lower == "punjab":
                mandis = PUNJAB_MANDIS[:5]
        
        # Load price data
        prices_df = mandi_loader.get_prices_for_commodity(commodity, district_lower)
        
        if prices_df.empty:
            # Return mock data with disclaimer
            return _mock_price_response(commodity, mandis, district)
        
        # Filter to relevant mandis and recent dates
        cutoff_date = date.today() - timedelta(days=days_back)
        prices_df["date"] = pd.to_datetime(prices_df["date"]).dt.date
        recent = prices_df[prices_df["date"] >= cutoff_date]
        
        # Get latest price per mandi
        latest = recent.sort_values("date", ascending=False).drop_duplicates(subset=["mandi_name"])
        
        mandi_prices = []
        for _, row in latest.iterrows():
            mandi_prices.append(MandiPrice(
                commodity=commodity,
                mandi_name=row["mandi_name"],
                district=row["district"],
                province=row["province"],
                min_price_pkr_per_40kg=row["min_price_pkr_per_40kg"],
                max_price_pkr_per_40kg=row["max_price_pkr_per_40kg"],
                modal_price_pkr_per_40kg=row["modal_price_pkr_per_40kg"],
                date=row["date"],
                arrivals_tonnes=row.get("arrivals_tonnes"),
                source=row.get("source", "amis")
            ))
        
        # Calculate trends
        trends = _calculate_trends(prices_df, commodity, mandis)
        
        # Best sell window
        best_window = _get_sell_advice(trends, commodity)
        
        return {
            "commodity": commodity,
            "district": district,
            "prices": [p.model_dump() for p in mandi_prices],
            "trends": [t.model_dump() for t in trends],
            "best_sell_window": best_window,
            "data_source": "amis" if not prices_df.empty else "mock",
            "last_updated": date.today().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Mandi price lookup error: {e}")
        return _mock_price_response(CROP_COMMODITY_MAP.get(crop.lower(), crop.lower()), 
                                     DISTRICT_MANDIS.get(district.lower(), []), district)

def _calculate_trends(prices_df, commodity: str, mandis: list[str]) -> list[PriceTrend]:
    """Calculate 7-day and 30-day price trends."""
    trends = []
    
    for mandi in mandis:
        mandi_data = prices_df[prices_df["mandi_name"] == mandi].sort_values("date")
        if len(mandi_data) < 2:
            continue
        
        modal_prices = mandi_data["modal_price_pkr_per_40kg"].values
        latest = modal_prices[-1]
        
        # 7-day trend
        week_ago_idx = max(0, len(modal_prices) - 8)
        week_ago = modal_prices[week_ago_idx]
        change_7d = ((latest - week_ago) / week_ago) * 100 if week_ago > 0 else 0
        
        # 30-day trend
        month_ago_idx = max(0, len(modal_prices) - 31)
        month_ago = modal_prices[month_ago_idx]
        change_30d = ((latest - month_ago) / month_ago) * 100 if month_ago > 0 else 0
        
        trend_7d = "rising" if change_7d > 2 else "falling" if change_7d < -2 else "stable"
        trend_30d = "rising" if change_30d > 5 else "falling" if change_30d < -5 else "stable"
        
        trends.append(PriceTrend(
            commodity=commodity,
            mandi_name=mandi,
            trend_7d=trend_7d,
            change_percent_7d=round(change_7d, 1),
            trend_30d=trend_30d,
            change_percent_30d=round(change_30d, 1),
            best_sell_window=_get_sell_advice_single(trend_7d, trend_30d)
        ))
    
    return trends

def _get_sell_advice(trends: list[PriceTrend], commodity: str) -> str:
    """Generate sell timing advice."""
    if not trends:
        return "Monitor prices daily. Sell when price exceeds your cost of production + 20% margin."
    
    rising_7d = sum(1 for t in trends if t.trend_7d == "rising")
    falling_7d = sum(1 for t in trends if t.trend_7d == "falling")
    
    if rising_7d > falling_7d:
        return "Prices trending up in most mandis. Consider holding 1-2 weeks for better price, but watch for reversal."
    elif falling_7d > rising_7d:
        return "Prices trending down. Consider selling soon to avoid further decline. Check if futures/forward contracts available."
    else:
        return "Prices stable. Sell at current price if it covers your cost + margin. No strong signal to hold or rush."

def _get_sell_advice_single(trend_7d: str, trend_30d: str) -> str:
    if trend_7d == "rising" and trend_30d == "rising":
        return "Strong uptrend - consider holding"
    elif trend_7d == "falling" and trend_30d == "falling":
        return "Downtrend - consider selling soon"
    elif trend_7d == "rising" and trend_30d == "falling":
        return "Short-term bounce in long downtrend - cautious"
    elif trend_7d == "falling" and trend_30d == "rising":
        return "Short-term dip in uptrend - could be buying opportunity"
    return "Stable - sell at target price"

def _mock_price_response(commodity: str, mandis: list[str], district: str) -> dict:
    """Fallback mock prices when no data available."""
    mock_prices = {
        "wheat": 3950, "cotton": 8500, "rice": 3400, "maize": 2800,
        "sugarcane": 350, "chickpea": 12000, "lentil": 14000,
        "mustard": 6800, "onion": 2500, "potato": 2000, "tomato": 3000,
        "mungbean": 13000,
    }
    
    base_price = mock_prices.get(commodity, 3000)
    
    prices = []
    for mandi in mandis[:3]:
        prices.append({
            "commodity": commodity,
            "mandi_name": mandi,
            "district": district,
            "province": "punjab",
            "min_price_pkr_per_40kg": round(base_price * 0.95),
            "max_price_pkr_per_40kg": round(base_price * 1.05),
            "modal_price_pkr_per_40kg": base_price,
            "date": date.today().isoformat(),
            "arrivals_tonnes": None,
            "source": "mock"
        })
    
    trends = []
    for mandi in mandis[:3]:
        trends.append({
            "commodity": commodity,
            "mandi_name": mandi,
            "trend_7d": "stable",
            "change_percent_7d": 0.0,
            "trend_30d": "stable",
            "change_percent_30d": 0.0,
            "best_sell_window": "Stable - sell at target price"
        })
    
    return {
        "commodity": commodity,
        "district": district,
        "prices": prices,
        "trends": trends,
        "best_sell_window": "Prices stable (mock data). Sell at target price covering cost + 20% margin.",
        "data_source": "mock",
        "last_updated": date.today().isoformat()
    }

# Need pandas import
import pandas as pd