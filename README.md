# Kisan Dost — AI Agronomy Agent for Pakistani Farmers

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI%20Agents%20SDK-latest-green.svg)](https://github.com/openai/openai-agents-python)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Kisan Dost (کسان دوست)** — "Farmer's Friend" — is a terminal-based AI agent built with the OpenAI Agents SDK that helps Pakistani smallholder farmers make critical decisions about crops, pests, fertilizers, market prices, irrigation, and government schemes.

## 🎯 Features

### 7 Specialist Tools
| Tool | Description |
|------|-------------|
| **Crop Advisor** | Recommends optimal crops based on district, soil, season, water availability, and land size |
| **Pest & Disease Doctor** | Diagnoses pests/diseases from symptom descriptions with safe treatment plans |
| **Fertilizer Calculator** | Computes NPK needs → Urea/DAP bags with total cost and application schedule |
| **Mandi Price Lookup** | Returns wholesale prices in nearby mandis with trends and sell timing advice |
| **Irrigation & Weather** | Advises irrigation timing from forecast + crop stage with frost/heatwave alerts |
| **Profit Estimator** | Full season budget: costs vs revenue, net margin, break-even, sensitivity analysis |
| **Govt Support Finder** | Surfaces Kisan Card, fertilizer subsidies, agri-loans, crop insurance by province |

### Architecture
- **Multi-Agent System**: Triage agent routes to 3 specialist agents (Agronomy, Pest Doctor, Market & Finance)
- **Structured Outputs**: All tools return typed Pydantic models (CropPlan, FertilizerPlan, PestDiagnosis, etc.)
- **Guardrails**: Input guardrail rejects off-topic/unsafe requests; output guardrail enforces pesticide safety limits
- **Session Memory**: Remembers farmer profile, farm context across conversation turns
- **Urdu Support**: English, Urdu script, and Roman Urdu interfaces
- **Tracing**: Built-in OpenAI Agents SDK tracing for debugging

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key (or Gemini/Groq/Ollama compatible endpoint)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd kisan-dost

# Install dependencies (using uv for speed, or pip)
uv sync
# or
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env

# Edit .env with your API key
# OPENAI_API_KEY=your_key_here
```

### Running

```bash
# Start the app from the project root
python -m cli.main

# Start with a new session using farm details
python -m cli.main --district Multan --acres 5 --crop wheat

# Start with a specific language
python -m cli.main --language ur

# Resume an existing farmer session
python -m cli.main --farmer-id farmer_001
```

### Starting the conversation

Once the app starts, the CLI welcomes you and waits for input:

```text
Assalam-o-Alaikum Mehmood! Main Kisan Dost. Aaj aapki kya madad karoon?

Your question: : what should I plant this Rabi season on 5 acres in Multan
```

You can type a normal farm question directly, or use slash commands at any time:

```text
/help
/lang en
/lang ur
/profile
/context
/history
/reset
/session new
/session list
/quit
```

Common workflow:

1. Start the app with `python -m cli.main`
2. Type `/help` to see commands
3. Optionally switch language with `/lang ur` or `/lang roman_ur`
4. Run questions like:
   - "What should I plant this Rabi season on 5 acres in Multan?"
   - "My cotton leaves are curling with tiny white insects"
   - "How much Urea and DAP for 10 acres of wheat?"
   - "What's the wheat price in Faisalabad mandi?"
5. Use `/session new` or pass `--district --acres --crop` when starting for a faster first run

## 💬 Example Conversation

```
🌾 Kisan Dost - Farmer's Friend 🌾
Terminal Agronomy Agent | OpenAI Agents SDK

Assalam-o-Alaikum! I'm Kisan Dost. How can I help your farm today?

Your question: What should I plant this Rabi season on 5 acres in Faisalabad with canal irrigation?

🌱 Top Recommendation
Primary Recommendation: Wheat (cereal)
- Expected Yield: 1,200 kg/acre
- Expected Price: PKR 4,000/40kg
- Water Need: 450 mm
- NPK Requirement: 90-45-30 kg/acre
- Estimated Profit: PKR 48,000/acre
- Suitability: 85%

Alternative Crops:
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Crop       ┃ Yield       ┃ Price        ┃ Profit        ┃ Suitability ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Chickpea   │ 600         │ 12,000       │ 52,000        │ 78%         │
│ Mustard    │ 500         │ 7,000        │ 25,000        │ 72%         │
└────────────┴─────────────┴──────────────┴───────────────┴─────────────┘

Reasoning: Top pick: wheat (suitability: 85%) | Matches your loam soil and canal water | Expected profit: PKR 48,000/acre
```

## 🛠 Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help |
| `/lang en\|ur\|roman_ur` | Change language |
| `/profile` | Show farmer profile |
| `/context` | Show farm context |
| `/history` | Show conversation history |
| `/reset` | Reset conversation |
| `/session new\|load\|list` | Session management |
| `/quit` | Exit |

## 📁 Project Structure

```
kisan-dost/
├── config/              # Settings, constants, prompts
├── data/                # CSV data files (crops, pests, mandi, govt schemes)
├── models/              # Pydantic models for all tools
├── tools/               # 7 function tools (@function_tool)
├── agents/              # Multi-agent system (triage + 3 specialists)
├── guardrails/          # Input/output safety guardrails
├── sessions/            # Session management (SQLite)
├── tracing/             # SDK tracing setup
├── cli/                 # Rich terminal UI
├── services/            # External API clients (weather, mandi)
├── tests/               # Unit, integration, e2e tests
├── scripts/             # Data seeding, validation, benchmarking
└── docs/                # Architecture, tool specs, deployment
```

## 🔧 Configuration

Key settings in `.env`:

```env
# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4o-mini

# Alternative: Gemini, Groq, Ollama
# LLM_PROVIDER=gemini
# GEMINI_API_KEY=your_key

# Safety
MAX_PESTICIDE_DOSAGE_ML_PER_ACRE=2000.0

# Real APIs (optional)
USE_REAL_APIS=false

# Session
SESSION_BACKEND=sqlite
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=kisan_dost

# Run specific test file
pytest tests/unit/test_tools/test_tools.py -v
```

## 📊 Data Sources

- **Crop Recommendations**: Adapted from [Kaggle Crop Recommendation Dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) + Pakistan-specific data
- **Pest/Disease Data**: Based on [PlantVillage Dataset](https://github.com/spMohanty/PlantVillage-Dataset) + local knowledge
- **Mandi Prices**: [AMIS Punjab](http://www.amis.pk/) daily wholesale rates
- **Government Schemes**: Official provincial agriculture department programs
- **Weather**: [Open-Meteo](https://open-meteo.com/) free API (no key required)

## 🏗 Architecture Details

### Agent Handoff Flow
```
User Query
    ↓
Triage Agent (classifies intent)
    ↓
    ├── Crop/Fertilizer/Irrigation → Agronomy Agent
    ├── Pest/Disease → Pest Doctor Agent
    └── Price/Profit/Govt → Market & Finance Agent
```

### Guardrails
- **Input**: Rejects off-topic, unsafe (medical advice, bombs), PII requests, prompt injection
- **Output**: Enforces pesticide dosage limits, PHI/REI, PPE requirements, bans prohibited chemicals

### Safety First
- Banned pesticides (endosulfan, monocrotophos, etc.) automatically rejected
- Dosages capped at WHO/FAO safe limits
- Pre-harvest intervals enforced
- No human medical advice

## 🌾 Designed for Pakistan

- All prices in PKR per 40kg (maund)
- Land measured in acres
- Crops: Rabi (wheat, chickpea, mustard...), Kharif (cotton, rice, maize...), Zaid
- Provinces: Punjab, Sindh, KPK, Balochistan, GB, AJK
- Districts: 100+ major districts
- Government schemes: Kisan Card, fertilizer subsidies, agri-loans, crop insurance

## 📝 Hackathon Submission

This project was built for the **Agentic AI Hackathon — Terminal Agent Challenge** using the **OpenAI Agents SDK**.

**Grading Criteria Addressed:**
- ✅ 7 working function tools with typed inputs/outputs
- ✅ Multi-agent handoffs (triage → 3 specialists)
- ✅ Structured Pydantic outputs
- ✅ Input + output guardrails (pesticide safety)
- ✅ Session memory with typed farmer context
- ✅ Urdu/English/Roman Urdu support
- ✅ Real API integration ready (Open-Meteo, AMIS Punjab)
- ✅ Clean, documented, tested codebase

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Submit a PR

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- OpenAI Agents SDK team
- Pakistan Agriculture Research Council (PARC)
- AMIS Punjab for market data
- Open-Meteo for free weather API
- Kaggle community for crop datasets

---

**Build something a farmer would actually thank you for.** 🌾