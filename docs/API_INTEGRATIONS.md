# API Integrations

## Overview

Kisan Dost supports both mock data (for development/hackathon) and real API integrations (for production). All external API calls are wrapped in service classes with graceful fallbacks.

## Open-Meteo Weather API

### Purpose
Free weather forecasts and historical data for irrigation advice.

### Endpoint
```
https://api.open-meteo.com/v1/forecast
```

### Parameters
| Parameter | Value |
|-----------|-------|
| latitude | District latitude |
| longitude | District longitude |
| current | temperature_2m,relative_humidity_2m |
| daily | temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean,windspeed_10m_max,weathercode |
| timezone | Asia/Karachi |
| forecast_days | 7-14 |

### No Authentication Required
Completely free, no API key needed.

### Geocoding
```
https://geocoding-api.open-meteo.com/v1/search?name={district}&country=Pakistan
```

### Integration
```python
from services.weather import weather_service

# Get coordinates
coords = await weather_service.get_coordinates("faisalabad")
# Returns: (31.45, 73.13)

# Get forecast
forecast = await weather_service.get_forecast(31.45, 73.13, days=7)
```

### Fallback
If API fails, `_mock_forecast()` generates realistic synthetic data.

## AMIS Punjab Mandi Prices

### Purpose
Official daily wholesale prices for 100+ Punjab markets.

### Source
http://www.amis.pk/ - Agriculture Marketing Information System Punjab

### Status
**No public API available** - requires web scraping.

### Current Implementation
Mock data in `data/mandi_prices.csv` with realistic prices for major commodities.

### Future Integration
```python
# In services/mandi_api.py
async def scrape_latest(self):
    # Use httpx + BeautifulSoup to scrape amis.pk
    # Parse HTML tables for commodity prices
    pass
```

### Target Data Structure
```python
{
    "commodity": "wheat",
    "mandi_name": "faisalabad_grain_market",
    "district": "faisalabad",
    "province": "punjab",
    "min_price_pkr_per_40kg": 3800,
    "max_price_pkr_per_40kg": 4100,
    "modal_price_pkr_per_40kg": 3950,
    "arrivals_tonnes": 500,
    "date": "2024-01-15"
}
```

## LLM Provider Configuration

### OpenAI (Default)
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### Google Gemini
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=...
# Uses OpenAI-compatible endpoint
```

### Groq
```env
LLM_PROVIDER=groq
GROQ_API_KEY=...
```

### Ollama (Local)
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

### SDK Configuration
The Agents SDK uses `set_default_openai_key()` and respects `OPENAI_BASE_URL` for compatible endpoints.

## Kaggle Crop Recommendation Dataset

### Source
https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset

### Description
2,200 rows mapping soil N-P-K, temperature, humidity, pH, rainfall → 22 crops

### Usage
Download `Crop_recommendation.csv` and run custom script to:
1. Filter for Pakistan-relevant crops
2. Add profit estimates using local prices
3. Add water requirements
4. Export to `data/crops.csv`

### Columns Used
- N, P, K (kg/ha) → convert to kg/acre
- temperature, humidity, ph, rainfall
- label (crop name)

## PlantVillage Disease Dataset

### Source
https://github.com/spMohanty/PlantVillage-Dataset

### Description
50,000+ labeled crop leaf images across 38 classes

### Usage
For hackathon: symptom-to-pest mapping in `data/pests_diseases.csv`
For production: Train custom vision model for image-based diagnosis

### Integration Path
1. Download dataset
2. Train classifier (MobileNet/EfficientNet)
3. Deploy as API endpoint
4. Add image upload to CLI

## FAOSTAT Pakistan Statistics

### Source
https://www.fao.org/faostat/en/#country/165

### Data Available
- Crop production, yield, area harvested
- Fertilizer consumption
- Pesticide use
- Land use

### Usage
Ground truth for yield/price estimates in profit calculator.

## Pakistan Bureau of Statistics

### Source
https://www.pbs.gov.pk/

### Data Available
- Agricultural census data
- District-level crop statistics
- Price indices
- Rural household surveys

## Government Scheme APIs

### Status
No centralized API - schemes managed by provincial departments.

### Current Data
Static CSV in `data/govt_schemes.csv` with 25+ schemes across 4 provinces.

### Future Enhancement
Build scrapers for:
- https://kisan.punjab.gov.pk/
- https://agri.sindh.gov.pk/
- https://agriculture.kp.gov.pk/
- https://agri.balochistan.gov.pk/

## Enabling Real APIs

Set in `.env`:
```env
USE_REAL_APIS=true
```

This switches:
- `irrigation_weather` → Open-Meteo (always works)
- `mandi_price_lookup` → AMIS scraper (when implemented)
- Crop recommendations → Kaggle-trained model (when implemented)

## Rate Limits & Error Handling

| API | Rate Limit | Timeout | Retry |
|-----|------------|---------|-------|
| Open-Meteo | Generous | 10s | 3x exponential backoff |
| AMIS (scraping) | Respectful | 15s | 2x |
| LLM Provider | Per provider | 60s | SDK handles |

All services use `tenacity` for retries with exponential backoff.

## Monitoring

Enable tracing to monitor API calls:
```env
AGENTS_SDK_TRACING_ENABLED=true
AGENTS_SDK_TRACE_EXPORT=file
AGENTS_SDK_TRACE_FILE=traces/kisan_dost.jsonl
```