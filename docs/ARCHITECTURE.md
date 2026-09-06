# Kisan Dost Architecture

## Overview

Kisan Dost is a multi-agent AI system built on the OpenAI Agents SDK. The architecture follows a hub-and-spoke pattern with a central triage agent routing to three specialist agents.

## System Components

### 1. Triage Agent (Router)
- **Role**: Classify user intent and route to appropriate specialist
- **Tools**: `classify_intent` function tool
- **Handoffs**: Agronomy Agent, Pest Doctor Agent, Market & Finance Agent
- **Guardrails**: Input guardrail attached

### 2. Agronomy Agent
- **Role**: Crop recommendations, fertilizer calculations, irrigation advice
- **Tools**: `crop_advisor`, `fertilizer_calculator`, `irrigation_weather`
- **Output Types**: `CropPlan`, `FertilizerPlan`, `WeatherForecast`

### 3. Pest & Disease Doctor Agent
- **Role**: Pest/disease diagnosis with safe treatment plans
- **Tools**: `pest_disease_doctor`
- **Output Type**: `PestDiagnosis`
- **Guardrails**: Output guardrail validates pesticide safety

### 4. Market & Finance Agent
- **Role**: Market prices, profit estimation, government schemes
- **Tools**: `mandi_price_lookup`, `profit_estimator`, `govt_support_finder`
- **Output Types**: Price data, `ProfitEstimate`, `SchemeMatch[]`

## Data Flow

```
User Input
    ↓
Input Guardrail (validates safety/relevance)
    ↓
Triage Agent (classifies intent)
    ↓
    ├── Crop/Fertilizer/Weather → Agronomy Agent
    ├── Pest/Disease → Pest Doctor Agent
    └── Price/Profit/Govt → Market & Finance Agent
    ↓
Specialist Agent executes tools
    ↓
Output Guardrail (validates pesticide safety)
    ↓
Structured Response → User
```

## Session Management

- **Backend**: SQLite (default), Redis, or in-memory
- **Context**: FarmerProfile + FarmContext injected per turn
- **Memory**: Last N messages + summarized context
- **TTL**: 24 hours (configurable)

## Guardrails

### Input Guardrail
Checks for:
- Off-topic queries (non-agriculture)
- Unsafe requests (medical advice, dangerous content)
- PII requests
- Prompt injection attempts
- Banned pesticide mentions

### Output Guardrail
Validates:
- Pesticide dosage ≤ safety limit
- Pre-harvest interval (PHI) specified
- Re-entry interval (REI) specified
- Protective equipment listed
- No human medical advice
- No banned pesticides

## Data Layer

All data stored as CSV files in `data/`:
- `crops.csv` - 22 crops with yield, price, NPK, water needs
- `fertilizers.csv` - 8 fertilizer types with composition & prices
- `mandi_prices.csv` - Historical wholesale prices
- `pests_diseases.csv` - 15 pests/diseases with symptoms & treatments
- `govt_schemes.csv` - 25+ government schemes by province

## External Integrations

| Service | Purpose | Auth |
|---------|---------|------|
| Open-Meteo | Weather forecasts | None (free) |
| AMIS Punjab | Mandi prices | Scraping |
| Kaggle/FAOSTAT | Training data | Manual download |

## Deployment

### Local Development
```bash
python -m kisan_dost.cli.main
```

### Production Considerations
- Use Redis for session backend
- Enable OTLP tracing to Jaeger/Grafana
- Set up log aggregation
- Use real API keys in `.env`
- Run behind process manager (systemd, PM2)

## Scaling

The stateless agent design allows horizontal scaling:
- Multiple agent instances can share session DB
- Tools are pure functions (easy to cache/memoize)
- Data layer is read-heavy (CSV → consider SQLite/PostgreSQL)