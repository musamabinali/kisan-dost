"""Script to seed data from external sources."""

import pandas as pd
from pathlib import Path
from config import settings

def seed_crop_data():
    """Download and prepare crop data from Kaggle."""
    # In production, download from:
    # https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset
    # For now, our CSV is already populated with Pakistan-specific data
    print("Crop data already seeded in data/crops.csv")
    df = pd.read_csv("data/crops.csv")
    print(f"Loaded {len(df)} crop records")
    print(f"Seasons: {df['season'].unique()}")
    print(f"Categories: {df['category'].unique()}")

def seed_pest_data():
    """Pest data from PlantVillage."""
    # In production, download from:
    # https://github.com/spMohanty/PlantVillage-Dataset
    print("Pest data already seeded in data/pests_diseases.csv")
    df = pd.read_csv("data/pests_diseases.csv")
    print(f"Loaded {len(df)} pest/disease records")
    print(f"Types: {df['type'].unique()}")

def seed_mandi_data():
    """Mandi data from AMIS Punjab."""
    # In production, scrape from http://www.amis.pk/
    print("Mandi data already seeded in data/mandi_prices.csv")
    df = pd.read_csv("data/mandi_prices.csv")
    print(f"Loaded {len(df)} price records")
    print(f"Commodities: {df['commodity'].unique()}")

def seed_govt_schemes():
    """Government schemes data."""
    print("Government schemes already seeded in data/govt_schemes.csv")
    df = pd.read_csv("data/govt_schemes.csv")
    print(f"Loaded {len(df)} schemes")
    print(f"Provinces: {df['province'].unique()}")
    print(f"Types: {df['scheme_type'].unique()}")

def validate_all_data():
    """Validate all data files."""
    files = [
        "data/crops.csv",
        "data/fertilizers.csv",
        "data/mandi_prices.csv",
        "data/pests_diseases.csv",
        "data/govt_schemes.csv"
    ]
    
    for f in files:
        path = Path(f)
        if path.exists():
            df = pd.read_csv(f)
            print(f"✓ {f}: {len(df)} rows, {len(df.columns)} columns")
        else:
            print(f"✗ {f}: NOT FOUND")

if __name__ == "__main__":
    print("=== Seeding Kisan Dost Data ===\n")
    seed_crop_data()
    print()
    seed_pest_data()
    print()
    seed_mandi_data()
    print()
    seed_govt_schemes()
    print()
    validate_all_data()