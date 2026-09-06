# Tool Specifications

## 1. crop_advisor

**Purpose**: Recommend optimal crops for given farm conditions.

**Input**:
```python
farm_context: FarmContext  # district, soil_type, season, water_availability, land_size_acres
farmer_profile: FarmerProfile | None  # optional for personalization
```

**Output**: `CropPlan`
- `recommendations`: List of `CropRecommendation` (max 5)
- `primary_recommendation`: Best match
- `alternative_crops`: 2 alternatives
- `reasoning`: Human-readable explanation
- `data_source`: "kaggle" | "mock" | "faostat" | "hybrid"

**CropRecommendation fields**:
- `crop_name`: str
- `category`: CropCategory (cereal, pulse, oilseed, cash_crop, vegetable, fodder)
- `expected_yield_kg_per_acre`: float
- `expected_price_pkr_per_40kg`: float
- `water_requirement_mm`: float
- `growing_days`: int
- `fertilizer_npk_kg_per_acre`: tuple[N, P, K]
- `profit_per_acre_pkr`: float
- `suitability_score`: 0.0-1.0
- `risk_factors`: list[str]

**Scoring Algorithm**:
```
suitability = 0.30 * water_match + 0.25 * soil_match + 0.25 * profit_score + 0.20 * season_match
```

## 2. pest_disease_doctor

**Purpose**: Diagnose pest/disease from symptom description.

**Input**:
```python
symptoms: str  # e.g., "cotton leaves curling, tiny white insects"
farm_context: FarmContext
crop_name: str | None  # optional, defaults to context.current_crop
language: str  # "en" | "ur" | "roman_ur"
```

**Output**: `PestDiagnosis`
- `pest_name`: str
- `pest_type`: PestType (insect, disease, weed, nematode, rodent)
- `scientific_name`: str | None
- `confidence`: 0.0-1.0
- `symptoms_matched`: list[str]
- `affected_crops`: list[str]
- `severity`: Severity (low, moderate, high, critical)
- `treatment`: TreatmentPlan
- `preventive_measures`: list[str]
- `economic_threshold`: str | None
- `urdu_name`: str | None

**TreatmentPlan** (IPM-first):
- `treatment_type`: TreatmentType (cultural, biological, chemical, ipm)
- `pesticide_name`: str | None
- `active_ingredient`: str | None
- `dosage_ml_per_acre`: float
- `application_method`: spray | soil_drench | seed_treatment | broadcast
- `timing`: str
- `frequency`: str
- `safety`: PesticideSafety
- `cost_per_acre_pkr`: float
- `alternatives`: list[TreatmentPlan]

## 3. fertilizer_calculator

**Purpose**: Compute NPK needs → fertilizer bags with cost.

**Input**:
```python
crop: str
acres: float
soil_test_npk: tuple[N, P, K] | None  # optional soil test
target_yield_kg_per_acre: float | None  # optional yield target
```

**Output**: `FertilizerPlan`
- `crop`: str
- `acres`: float
- `npk_requirement`: NPKRequirement
- `fertilizer_bags`: list[FertilizerBag]
- `total_cost_pkr`: float
- `application_schedule`: list[dict]
- `subsidy_eligible`: bool
- `subsidy_details`: str | None
- `cost_per_acre_pkr`: computed property

**FertilizerBag**:
- `fertilizer_type`: FertilizerType (urea, dap, npk_20_20_20, npk_12_32_16, ssp, mop, zinc_sulfate, boron)
- `bags_needed`: float
- `weight_per_bag_kg`: float (default 50)
- `price_per_bag_pkr`: float
- `total_weight_kg`: computed
- `total_cost_pkr`: computed

**Calculation Strategy**:
1. DAP for phosphorus (provides N too)
2. Urea for remaining nitrogen
3. MOP for potassium
4. Zinc sulfate for major crops

## 4. mandi_price_lookup

**Purpose**: Get wholesale prices in nearby mandis.

**Input**:
```python
crop: str
district: str
province: str = "punjab"
days_back: int = 7
```

**Output**: dict
- `commodity`: str
- `district`: str
- `prices`: list[MandiPrice]
- `trends`: list[PriceTrend]
- `best_sell_window`: str
- `data_source`: "amis" | "mock"
- `last_updated`: date

**MandiPrice**:
- `commodity`, `mandi_name`, `district`, `province`
- `min_price_pkr_per_40kg`, `max_price_pkr_per_40kg`, `modal_price_pkr_per_40kg`
- `date`, `arrivals_tonnes`, `source`

**PriceTrend**:
- `trend_7d`, `change_percent_7d`
- `trend_30d`, `change_percent_30d`
- `best_sell_window`: str

## 5. irrigation_weather

**Purpose**: Weather forecast + irrigation advice.

**Input**:
```python
farm_context: FarmContext
district: str
days_ahead: int = 7
```

**Output**: `WeatherForecast`
- `district`, `latitude`, `longitude`
- `current_temp_c`, `current_humidity`
- `forecast`: list[DailyForecast] (7-14 days)
- `irrigation_advice`: IrrigationAdvice
- `alerts`: list[str]
- `source`: "open_meteo" | "mock"

**DailyForecast**:
- `date`, `temp_max_c`, `temp_min_c`
- `humidity_percent`, `precipitation_mm`, `wind_speed_kmh`
- `condition`: WeatherCondition
- `uv_index`: float | None

**IrrigationAdvice**:
- `should_irrigate`: bool
- `reason`: str
- `recommended_date`: date | None
- `water_amount_mm`: float
- `method`: flood | furrow | sprinkler | drip | skip
- `urgency`: low | medium | high | critical
- `crop_stage_context`: str
- `weather_risk`: str | None

**ETc Calculation**:
```
ETc = ET0 * Kc
ET0 (Hargreaves) = 0.0023 * (T_mean + 17.8) * (T_max - T_min)^0.5 * 0.408
```

## 6. profit_estimator

**Purpose**: Full season budget with break-even analysis.

**Input**:
```python
crop: str
acres: float
farm_context: FarmContext
expected_yield_kg_per_acre: float | None
expected_price_pkr_per_40kg: float | None
```

**Output**: `ProfitEstimate`
- `crop`, `acres`
- `input_costs`: dict[str, float] (seed, fertilizer, pesticide, labor, irrigation, rent, transport)
- `total_input_cost_pkr`: float
- `expected_yield_kg`: float
- `expected_price_pkr_per_40kg`: float
- `expected_revenue_pkr`: float
- `net_profit_pkr`: float
- `profit_margin_percent`: float
- `break_even_yield_kg_per_acre`: float
- `break_even_price_pkr_per_40kg`: float
- `sensitivity_analysis`: dict[str, float] (±10% yield/price)
- `risk_factors`: list[str]
- `recommendation`: "profitable" | "marginal" | "loss_risk"

## 7. govt_support_finder

**Purpose**: Find eligible government schemes.

**Input**:
```python
farmer_profile: FarmerProfile
farm_context: FarmContext
need_type: str | None  # "fertilizer", "seed", "loan", "insurance", "machinery", "all"
```

**Output**: list[SchemeMatch]
- `scheme`: GovtScheme
- `match_score`: 0.0-1.0
- `matched_criteria`: list[str]
- `missing_criteria`: list[str]
- `next_steps`: list[str]

**GovtScheme**:
- `scheme_id`, `name`, `name_urdu`
- `scheme_type`: SchemeType (kisan_card, fertilizer_subsidy, agri_loan, crop_insurance, seed_subsidy, machinery_subsidy, solar_tubewell, training)
- `province`, `department`, `description`
- `benefits`: list[str]
- `eligibility`: EligibilityCriteria
- `application_deadline`, `application_method`, `application_url`, `contact_info`

**EligibilityCriteria**:
- `min_land_acres`, `max_land_acres`
- `required_crops`, `provinces`, `districts`
- `farmer_categories`, `documents_required`