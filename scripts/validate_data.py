"""Data validation script."""

import pandas as pd
from pathlib import Path

def validate_crops():
    df = pd.read_csv("data/crops.csv")
    print(f"Crops: {len(df)} records")
    
    # Check required columns
    required = ["crop", "category", "season", "yield_kg_per_acre", "price_pkr_per_40kg", "water_mm", "days", "n", "p", "k", "profit_pkr"]
    for col in required:
        if col not in df.columns:
            print(f"  ✗ Missing column: {col}")
        else:
            nulls = df[col].isnull().sum()
            if nulls > 0:
                print(f"  ⚠ {col}: {nulls} null values")
    
    # Check seasons
    valid_seasons = {"rabi", "kharif", "zaid"}
    invalid_seasons = set(df['season'].unique()) - valid_seasons
    if invalid_seasons:
        print(f"  ✗ Invalid seasons: {invalid_seasons}")
    
    # Check for negative values
    for col in ["yield_kg_per_acre", "price_pkr_per_40kg", "water_mm", "days", "profit_pkr"]:
        neg = (df[col] < 0).sum()
        if neg > 0:
            print(f"  ✗ {col}: {neg} negative values")
    
    print("  ✓ Crop validation complete")

def validate_fertilizers():
    df = pd.read_csv("data/fertilizers.csv")
    print(f"Fertilizers: {len(df)} records")
    
    required = ["fertilizer_type", "n_pct", "p2o5_pct", "k2o_pct", "price_per_bag_pkr", "weight_kg_per_bag"]
    for col in required:
        if col not in df.columns:
            print(f"  ✗ Missing column: {col}")
    
    # Percentages should sum to <= 100
    df['total_pct'] = df['n_pct'] + df['p2o5_pct'] + df['k2o_pct'] + df.get('zn_pct', 0) + df.get('b_pct', 0)
    over = (df['total_pct'] > 100).sum()
    if over > 0:
        print(f"  ⚠ {over} fertilizers have >100% nutrient content")
    
    print("  ✓ Fertilizer validation complete")

def validate_mandi():
    df = pd.read_csv("data/mandi_prices.csv")
    print(f"Mandi Prices: {len(df)} records")
    
    required = ["commodity", "mandi_name", "district", "province", "min_price_pkr_per_40kg", "max_price_pkr_per_40kg", "modal_price_pkr_per_40kg", "date"]
    for col in required:
        if col not in df.columns:
            print(f"  ✗ Missing column: {col}")
    
    # Price logic
    invalid = (df['min_price_pkr_per_40kg'] > df['max_price_pkr_per_40kg']).sum()
    if invalid > 0:
        print(f"  ✗ {invalid} records have min > max price")
    
    print("  ✓ Mandi validation complete")

def validate_pests():
    df = pd.read_csv("data/pests_diseases.csv")
    print(f"Pests/Diseases: {len(df)} records")
    
    required = ["name", "type", "crops", "symptoms", "severity", "treatments"]
    for col in required:
        if col not in df.columns:
            print(f"  ✗ Missing column: {col}")
    
    valid_types = {"insect", "disease", "weed", "nematode", "rodent"}
    invalid_types = set(df['type'].unique()) - valid_types
    if invalid_types:
        print(f"  ✗ Invalid types: {invalid_types}")
    
    valid_severity = {"low", "moderate", "high", "critical"}
    invalid_sev = set(df['severity'].unique()) - valid_severity
    if invalid_sev:
        print(f"  ✗ Invalid severity: {invalid_sev}")
    
    print("  ✓ Pest validation complete")

def validate_govt():
    df = pd.read_csv("data/govt_schemes.csv")
    print(f"Govt Schemes: {len(df)} records")
    
    required = ["scheme_id", "name", "scheme_type", "province", "department", "description", "benefits"]
    for col in required:
        if col not in df.columns:
            print(f"  ✗ Missing column: {col}")
    
    print("  ✓ Govt validation complete")

if __name__ == "__main__":
    print("=== Validating Kisan Dost Data ===\n")
    validate_crops()
    validate_fertilizers()
    validate_mandi()
    validate_pests()
    validate_govt()
    print("\n=== Validation Complete ===")