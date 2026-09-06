"""Pakistan-specific constants for Kisan Dost."""

# Pakistan districts by province
DISTRICTS_BY_PROVINCE = {
    "punjab": [
        "lahore", "faisalabad", "rawalpindi", "gujranwala", "multan", "sialkot",
        "bahawalpur", "sargodha", "sahiwal", "dg_khan", "sheikhupura", "jhelum",
        "gujrat", "kasur", "okara", "pakpattan", "vehari", "khanewal", "lodhran",
        "muzaffargarh", "layyah", "bhakkar", "mianwali", "khushab", "chakwal",
        "attock", "nankana_sahib", "mandi_bahauddin", "narowal", "hafizabad"
    ],
    "sindh": [
        "karachi", "hyderabad", "sukkur", "larkana", "nawabshah", "mirpur_khas",
        "jacobabad", "shikarpur", "kashmore", "gambat", "khairpur", "sanghar",
        "umatarko", "tharparkar", "badin", "thatta", "sujawal", "tando_allahyar",
        "tando_muhammad_khan", "matiari", "jamshoro", "dadu", "kamber_shahdadkot"
    ],
    "kpk": [
        "peshawar", "mardan", "abbottabad", "swat", "kohat", "bannu", "di_khan",
        "nowshera", "charsadda", "swabi", "haripur", "mansehra", "batagram",
        "kohistan", "shangla", "buner", "malakand", "dir_lower", "dir_upper",
        "chitral", "hangu", "karak", "lakki_marwat", "tank", "south_waziristan",
        "north_waziristan", "khyber", "mohmand", "bajaur", "kurram", "orakzai"
    ],
    "balochistan": [
        "quetta", "gwadar", "turbat", "khuzdar", "kalat", "mastung", "noshki",
        "chagai", "panjgur", "akeel", "washuk", "lasbela", "hub", "dalbandin",
        "sibi", "kohlu", "dzhi", "jhal_magsi", "jaffarabad", "nasirabad",
        "sohbatpur", "lehri", "musakhel", "barkhan", "loralai", "ziarat",
        "pishin", "qilla_abdullah", "qilla_saifullah", "zhob", "sherani"
    ],
    "gilgit_baltistan": [
        "gilgit", "skardu", "hunza", "nagar", "ghizer", "diamer", "astor",
        "kharmang", "shigar", "gultari", "roundu"
    ],
    "azad_kashmir": [
        "muzaffarabad", "mirpur", "kotli", "bhimber", "baghd", "haveli",
        "neelum", "jhelum_valley", "sudhanoti", "pooch"
    ]
}

ALL_DISTRICTS = [d for districts in DISTRICTS_BY_PROVINCE.values() for d in districts]

# Crop seasons in Pakistan
RABI_CROPS = [
    "wheat", "barley", "chickpea", "lentil", "mustard", "rapeseed",
    "oats", "fodder_maize", "berseem", "lucerne", "garlic", "onion"
]

KHARIF_CROPS = [
    "cotton", "rice", "maize", "sugarcane", "sorghum", "millet",
    "mungbean", "mothbean", "sesame", "groundnut", "soybean",
    "okra", "bitter_gourd", "bottle_gourd", "pumpkin", "cucumber"
]

ZAID_CROPS = [
    "watermelon", "muskmelon", "cucumber", "bitter_gourd", "bottle_gourd",
    "pumpkin", "fodder_maize", "sorghum", "pearl_millet", "moong", "moth"
]

# Fertilizer composition (nutrient %)
FERTILIZER_COMPOSITION = {
    "urea": {"N": 46.0, "P2O5": 0.0, "K2O": 0.0},
    "dap": {"N": 18.0, "P2O5": 46.0, "K2O": 0.0},
    "npk_20_20_20": {"N": 20.0, "P2O5": 20.0, "K2O": 20.0},
    "npk_12_32_16": {"N": 12.0, "P2O5": 32.0, "K2O": 16.0},
    "ssp": {"N": 0.0, "P2O5": 16.0, "K2O": 0.0},
    "mop": {"N": 0.0, "P2O5": 0.0, "K2O": 60.0},
    "zinc_sulfate": {"Zn": 33.0},
    "boron": {"B": 17.4},
}

# Default fertilizer prices (PKR per 50kg bag) - approximate 2024 rates
DEFAULT_FERTILIZER_PRICES = {
    "urea": 3000,
    "dap": 11500,
    "npk_20_20_20": 5500,
    "npk_12_32_16": 6000,
    "ssp": 2200,
    "mop": 4500,
    "zinc_sulfate": 2500,
    "boron": 3000,
}

# Crop NPK requirements (kg per acre) - typical for Pakistan
CROP_NPK_REQUIREMENTS = {
    "wheat": {"N": 90, "P2O5": 45, "K2O": 30},
    "cotton": {"N": 120, "P2O5": 60, "K2O": 60},
    "rice": {"N": 100, "P2O5": 50, "K2O": 50},
    "maize": {"N": 150, "P2O5": 75, "K2O": 75},
    "sugarcane": {"N": 200, "P2O5": 100, "K2O": 200},
    "chickpea": {"N": 20, "P2O5": 40, "K2O": 20},
    "lentil": {"N": 15, "P2O5": 30, "K2O": 15},
    "mungbean": {"N": 15, "P2O5": 30, "K2O": 15},
    "mustard": {"N": 60, "P2O5": 30, "K2O": 20},
    "rapeseed": {"N": 60, "P2O5": 30, "K2O": 20},
    "groundnut": {"N": 20, "P2O5": 40, "K2O": 30},
    "sesame": {"N": 40, "P2O5": 20, "K2O": 20},
    "sunflower": {"N": 80, "P2O5": 40, "K2O": 40},
    "potato": {"N": 150, "P2O5": 100, "K2O": 150},
    "onion": {"N": 100, "P2O5": 50, "K2O": 50},
    "tomato": {"N": 120, "P2O5": 60, "K2O": 80},
}

# Water requirements (mm per season)
CROP_WATER_REQUIREMENTS = {
    "wheat": 450,
    "cotton": 700,
    "rice": 1200,
    "maize": 500,
    "sugarcane": 1500,
    "chickpea": 300,
    "lentil": 250,
    "mungbean": 300,
    "mustard": 350,
    "groundnut": 450,
    "sesame": 350,
    "sunflower": 500,
    "potato": 500,
    "onion": 450,
    "tomato": 550,
}

# Punjab major mandis
PUNJAB_MANDIS = [
    "faisalabad_grain_market", "faisalabad_vegetable_market",
    "multan_grain_market", "multan_fruit_market",
    "lahore_grain_market", "lahore_vegetable_market",
    "gujranwala_grain_market", "gujranwala_vegetable_market",
    "sargodha_grain_market", "sargodha_citrus_market",
    "sahiwal_grain_market", "sahiwal_vegetable_market",
    "bahawalpur_grain_market", "bahawalpur_cotton_market",
    "dg_khan_grain_market", "dg_khan_cotton_market",
    "rawalpindi_grain_market", "rawalpindi_vegetable_market",
    "sialkot_grain_market", "sialkot_vegetable_market",
]

# Government schemes by province
GOVT_SCHEMES_BY_PROVINCE = {
    "punjab": [
        "kisan_card", "fertilizer_subsidy_punjab", "wheat_support_price",
        "solar_tubewell_punjab", "agri_loan_punjab", "crop_insurance_punjab",
        "mechanization_subsidy_punjab", "seed_subsidy_punjab"
    ],
    "sindh": [
        "kisan_card_sindh", "fertilizer_subsidy_sindh", "wheat_procurement_sindh",
        "tube_well_subsidy_sindh", "agri_credit_sindh"
    ],
    "kpk": [
        "kisan_card_kpk", "fertilizer_subsidy_kpk", "crop_insurance_kpk",
        "orchard_development_kpk", "livestock_insurance_kpk"
    ],
    "balochistan": [
        "kisan_card_balochistan", "water_management_balochistan",
        "date_palm_development", "livestock_vaccination_balochistan"
    ],
}

# Pesticide safety limits (ml per acre) - WHO/FAO guidelines adapted for Pakistan
PESTICIDE_SAFETY_LIMITS = {
    "imidacloprid": 200,
    "thiamethoxam": 100,
    "acetamiprid": 150,
    "chlorpyrifos": 500,
    "profenofos": 1000,
    "cypermethrin": 200,
    "lambda_cyhalothrin": 100,
    "bifenthrin": 150,
    "fipronil": 100,
    "abamectin": 50,
    "spinosad": 200,
    "emamectin_benzoate": 80,
    "chlorantraniliprole": 150,
    "flubendiamide": 120,
    "indoxacarb": 200,
    "methomyl": 500,
    "carbofuran": 0,  # Banned in many countries
    "monocrotophos": 0,  # Banned
    "endosulfan": 0,  # Banned
    "phosphamidon": 0,  # Banned
    "methyl_parathion": 0,  # Banned
}

# Pre-harvest intervals (days)
PRE_HARVEST_INTERVALS = {
    "imidacloprid": 14,
    "thiamethoxam": 14,
    "acetamiprid": 7,
    "chlorpyrifos": 21,
    "profenofos": 14,
    "cypermethrin": 7,
    "lambda_cyhalothrin": 7,
    "bifenthrin": 14,
    "fipronil": 30,
    "abamectin": 7,
    "spinosad": 3,
    "emamectin_benzoate": 14,
    "chlorantraniliprole": 14,
    "flubendiamide": 14,
    "indoxacarb": 14,
    "methomyl": 7,
}

# Urdu translations for key terms
URDU_TERMS = {
    "crop": "فصل",
    "fertilizer": "کھاد",
    "pest": "کیڑا",
    "disease": "بیماری",
    "harvest": "کٹائی",
    "sowing": "بوائی",
    "irrigation": "آبیاری",
    "market": "منڈی",
    "price": "قیمت",
    "profit": "منافعہ",
    "loss": "نقصان",
    "soil": "مٹی",
    "water": "پانی",
    "season": "موسم",
    "acre": "ایکڑ",
    "bag": "بوڑا",
    "urea": "یوریا",
    "dap": "ڈی اے پی",
    "subsidy": "سبسڈی",
    "loan": "قرضہ",
    "kisan_card": "کسان کارڈ",
    "district": "ضلع",
    "province": "صوبہ",
    "farmer": "کسان",
    "advisor": "مشیر",
    "recommendation": "تجویز",
    "treatment": "علاج",
    "dosage": "دوس",
    "safe": "محفوظ",
    "warning": "انتباہ",
    "weather": "موسم",
    "rain": "بارش",
    "temperature": "درجہ حرارت",
}