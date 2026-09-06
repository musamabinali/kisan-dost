# Guardrails Specification

## Overview

Kisan Dost implements both input and output guardrails to ensure safety, relevance, and compliance with agricultural best practices.

## Input Guardrail

### Location
`guardrails/input_guardrail.py` - `@input_guardrail` decorator on `input_guardrail()` function

### Checks Performed

#### 1. Prompt Injection Detection
Patterns detected:
- "ignore previous instructions"
- "forget everything you know"
- "you are now a/an"
- "system:", "assistant:", "user:" markers
- Code block injections (```)
- Token smuggling (<|...|>)

**Action**: Tripwire triggered, request rejected

#### 2. Unsafe Content Detection
Patterns detected:
- Human medical advice requests
- Dangerous content (bombs, weapons, poison, self-harm)
- Illegal pesticide requests

**Action**: Tripwire triggered, request rejected with safety message

#### 3. PII Protection
Patterns detected:
- CNIC numbers (#####-#######-#)
- Phone numbers (11 digits)
- Email addresses

**Action**: Tripwire triggered, request rejected

#### 4. Off-Topic Filtering
Allows queries containing farming context words:
- farm, khet, zameen, acre, hectare
- crop, fasal, seed, beej
- tractor, tube well, irrigation
- fertilizer, khad, pest, keera, disease, bimari
- mandi, price, rate, sell, bech
- profit, munafa, cost, kharcha
- weather, mosam, rain, barish
- government, sarkari, subsidy, kisan, card, loan, qarz

Rejects queries matching:
- cricket, football, movie, politics, news
- recipes, cooking
- programming, software, AI
- religion

**Action**: Tripwire triggered, polite redirect to farming topics

#### 5. Banned Pesticide Detection
Checks for any mention of banned pesticides:
- endosulfan, monocrotophos, phosphamidon
- methyl_parathion, carbofuran

**Action**: Tripwire triggered, explains ban and offers alternatives

### Response Format
```python
GuardrailFunctionOutput(
    output_info={
        "rejected": True,
        "reason": "prompt_injection|unsafe|pii|off_topic|banned_pesticide",
        "message": "User-friendly explanation"
    },
    tripwire_triggered=True
)
```

## Output Guardrail

### Location
`guardrails/output_guardrail.py` - `@output_guardrail` decorator on `output_guardrail()` function

### Checks Performed

#### 1. TreatmentPlan Validation
When output is a `TreatmentPlan`:
- **Banned pesticide check**: Cross-references against BANNED_PESTICIDES list
- **Dosage limit check**: Compares `dosage_ml_per_acre` against `PESTICIDE_SAFETY_LIMITS`
- **PHI check**: Ensures `pre_harvest_interval_days` > 0, fills from `PRE_HARVEST_INTERVALS` if missing
- **REI check**: Ensures `re_entry_interval_hours` > 0
- **PPE check**: Adds default ["mask", "gloves", "goggles"] if missing
- **Medical advice check**: Scans for human medical keywords

**Action**: Auto-corrects dosage, fills missing safety fields, logs issues (doesn't tripwire)

#### 2. Text Output Validation
When output is a string:
- **Banned pesticide mentions**: Flags any banned pesticide names
- **Medical advice patterns**: Detects "take this medicine", "for human health", "doctor recommends"
- **Dosage without safety info**: Checks for dosage patterns without PHI/REI/PPE

**Action**: Logs issues, doesn't block (educational)

#### 3. Dict Output Validation
When output is a dict (from function tools):
- Validates nested treatment plans
- Checks dosage limits
- Flags banned pesticides

### Response Format
```python
GuardrailFunctionOutput(
    output_info={
        "validated": True,
        "issues": ["Issue 1", "Issue 2"],
        "corrected_plan": {...}  # if TreatmentPlan was corrected
    },
    tripwire_triggered=False  # Never blocks, only corrects
)
```

## Pesticide Safety Reference

### Safety Limits (ml/acre)
| Pesticide | Max Dosage | PHI (days) | Bee Toxicity | Aquatic Toxicity |
|-----------|------------|------------|--------------|------------------|
| imidacloprid | 200 | 14 | high | moderate |
| thiamethoxam | 100 | 14 | high | moderate |
| acetamiprid | 150 | 7 | moderate | low |
| chlorpyrifos | 500 | 21 | low | moderate |
| profenofos | 1000 | 14 | low | moderate |
| cypermethrin | 200 | 7 | low | moderate |
| lambda_cyhalothrin | 100 | 7 | low | moderate |
| bifenthrin | 150 | 14 | low | moderate |
| fipronil | 100 | 30 | high | high |
| spinosad | 200 | 3 | low | moderate |
| chlorantraniliprole | 150 | 14 | low | low |
| emamectin_benzoate | 80 | 14 | moderate | moderate |

### Banned Pesticides (Zero Tolerance)
- endosulfan
- monocrotophos
- phosphamidon
- methyl_parathion
- carbofuran

### Default Safety Equipment
- Mask (respiratory protection)
- Gloves (chemical-resistant)
- Goggles (eye protection)
- Long sleeves
- Boots

## Integration with Agents SDK

Guardrails are automatically attached to agents via the SDK:

```python
from agents import Agent
from guardrails import input_guardrail, output_guardrail

triage_agent = Agent(
    name="Triage Agent",
    instructions=TRIAGE_AGENT_INSTRUCTIONS,
    tools=[classify_intent],
    handoffs=[agronomy_agent, pest_doctor_agent, market_finance_agent],
    input_guardrails=[input_guardrail],
    output_guardrails=[output_guardrail],
)
```

## Testing Guardrails

```bash
# Test input guardrail
pytest tests/unit/test_guardrails/ -v

# Test specific scenarios
python -c "
from guardrails.input_guardrail import input_guardrail
# Test cases...
"
```

## Customization

To adjust safety limits, edit `config/constants.py`:
- `PESTICIDE_SAFETY_LIMITS`
- `PRE_HARVEST_INTERVALS`
- `BANNED_PESTICIDES`

To add off-topic patterns, edit `guardrails/input_guardrail.py`:
- `OFF_TOPIC_PATTERNS`
- `UNSAFE_PATTERNS`