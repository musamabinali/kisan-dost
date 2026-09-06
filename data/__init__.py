"""Data loading utilities for CSV files."""

import pandas as pd
from pathlib import Path
from typing import Optional, Literal
from config import settings

class DataLoader:
    """Base data loader with caching."""
    
    def __init__(self):
        self.data_dir = Path(settings.data_dir)
        self._cache = {}
    
    def _load_csv(self, filename: str, use_cache: bool = True) -> pd.DataFrame:
        if use_cache and filename in self._cache:
            return self._cache[filename]
        
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")
        
        df = pd.read_csv(path)
        if use_cache:
            self._cache[filename] = df
        return df
    
    def clear_cache(self):
        self._cache.clear()


class CropDataLoader(DataLoader):
    """Load crop recommendation data."""
    
    def load_crop_recommendations(self) -> pd.DataFrame:
        return self._load_csv("crops.csv")
    
    def get_crops_by_season(self, season: str) -> pd.DataFrame:
        df = self.load_crop_recommendations()
        return df[df["season"] == season]
    
    def get_crop_requirements(self, crop: str) -> Optional[dict]:
        df = self.load_crop_recommendations()
        row = df[df["crop"] == crop.lower()]
        if row.empty:
            return None
        return row.iloc[0].to_dict()


class FertilizerDataLoader(DataLoader):
    """Load fertilizer composition and price data."""
    
    def load_fertilizers(self) -> pd.DataFrame:
        return self._load_csv("fertilizers.csv")
    
    def get_fertilizer_info(self, fertilizer_type: str) -> Optional[dict]:
        df = self.load_fertilizers()
        row = df[df["fertilizer_type"] == fertilizer_type]
        if row.empty:
            return None
        return row.iloc[0].to_dict()
    
    def get_all_fertilizers(self) -> list[dict]:
        df = self.load_fertilizers()
        return df.to_dict("records")


class MandiPriceLoader(DataLoader):
    """Load mandi price data."""
    
    def load_prices(self) -> pd.DataFrame:
        return self._load_csv("mandi_prices.csv")
    
    def get_prices_for_commodity(self, commodity: str, district: Optional[str] = None) -> pd.DataFrame:
        df = self.load_prices()
        df = df[df["commodity"] == commodity.lower()]
        if district:
            df = df[df["district"] == district.lower()]
        return df.sort_values("date", ascending=False)
    
    def get_latest_prices(self, district: Optional[str] = None) -> pd.DataFrame:
        df = self.load_prices()
        if district:
            df = df[df["district"] == district.lower()]
        # Get latest date per commodity per mandi
        return df.sort_values("date", ascending=False).drop_duplicates(subset=["commodity", "mandi_name"])


class PestDataLoader(DataLoader):
    """Load pest and disease data."""
    
    def load_pests(self) -> pd.DataFrame:
        return self._load_csv("pests_diseases.csv")
    
    def search_pests(self, symptoms: str, crop: Optional[str] = None) -> list[dict]:
        df = self.load_pests()
        
        # Simple keyword matching - in production use embeddings
        symptom_keywords = symptoms.lower().split()
        scores = []
        
        for _, row in df.iterrows():
            score = 0
            matched = []
            symptom_text = " ".join([
                str(row.get("symptoms", "")),
                str(row.get("name", "")),
                str(row.get("urdu_name", ""))
            ]).lower()
            
            for kw in symptom_keywords:
                if kw in symptom_text:
                    score += 1
                    matched.append(kw)
            
            # Boost if crop matches
            if crop and crop.lower() in str(row.get("crops", "")).lower():
                score += 2
            
            if score > 0:
                scores.append({
                    **row.to_dict(),
                    "confidence": min(score / len(symptom_keywords), 1.0),
                    "matched_symptoms": matched
                })
        
        scores.sort(key=lambda x: x["confidence"], reverse=True)
        return scores[:5]


class GovtSchemeLoader(DataLoader):
    """Load government scheme data."""
    
    def load_schemes(self) -> pd.DataFrame:
        return self._load_csv("govt_schemes.csv")
    
    def get_schemes_for_farmer(
        self, 
        province: str, 
        district: str, 
        crop: Optional[str] = None,
        land_acres: float = 0,
        farmer_category: str = "small"
    ) -> list[dict]:
        df = self.load_schemes()
        df = df[(df["province"] == province.lower()) & (df["is_active"] == True)]
        
        matches = []
        for _, row in df.iterrows():
            match_score = 0
            matched = []
            missing = []
            
            # Land size check
            min_land = row.get("min_land_acres", 0) or 0
            max_land = row.get("max_land_acres", 1000) or 1000
            if min_land <= land_acres <= max_land:
                match_score += 0.3
                matched.append("land_size")
            else:
                missing.append("land_size")
            
            # Crop check
            required_crops = str(row.get("required_crops", "")).split(",") if row.get("required_crops") else []
            if not required_crops or (crop and crop.lower() in [c.strip().lower() for c in required_crops]):
                match_score += 0.3
                matched.append("crop")
            elif required_crops:
                missing.append("crop")
            
            # Farmer category
            categories = str(row.get("farmer_categories", "")).split(",") if row.get("farmer_categories") else []
            if not categories or farmer_category in [c.strip().lower() for c in categories]:
                match_score += 0.2
                matched.append("category")
            elif categories:
                missing.append("category")
            
            # District check
            districts = str(row.get("districts", "")).split(",") if row.get("districts") else []
            if not districts or district.lower() in [d.strip().lower() for d in districts]:
                match_score += 0.2
                matched.append("district")
            elif districts:
                missing.append("district")
            
            if match_score > 0:
                matches.append({
                    "scheme": row.to_dict(),
                    "match_score": match_score,
                    "matched_criteria": matched,
                    "missing_criteria": missing
                })
        
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches


# Global loader instances
crop_loader = CropDataLoader()
fertilizer_loader = FertilizerDataLoader()
mandi_loader = MandiPriceLoader()
pest_loader = PestDataLoader()
govt_loader = GovtSchemeLoader()