"""Benchmark script for performance testing."""

import asyncio
import time
import statistics
from tools import (
    crop_advisor, pest_disease_doctor, fertilizer_calculator,
    mandi_price_lookup, irrigation_weather, profit_estimator, govt_support_finder
)
from models import FarmerProfile, FarmContext, Province, Season, SoilType, WaterAvailability
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Test fixtures
FARMER = FarmerProfile(
    farmer_id="bench_001",
    district="faisalabad",
    province=Province.PUNJAB
)

CONTEXT_RABI = FarmContext(
    land_size_acres=5.0,
    soil_type=SoilType.LOAM,
    season=Season.RABI,
    water_availability=WaterAvailability.CANAL
)

CONTEXT_KHARIF = FarmContext(
    land_size_acres=10.0,
    soil_type=SoilType.CLAY_LOAM,
    season=Season.KHARIF,
    water_availability=WaterAvailability.FULL_IRRIGATION,
    current_crop="cotton",
    crop_stage="flowering"
)

async def benchmark_tool(name: str, func, *args, iterations: int = 10):
    """Benchmark a single tool."""
    times = []
    
    # Warmup
    await func(*args)
    
    for _ in range(iterations):
        start = time.perf_counter()
        await func(*args)
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)  # ms
    
    return {
        "tool": name,
        "iterations": iterations,
        "mean_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0
    }

async def run_benchmarks():
    """Run all benchmarks."""
    print("=== Kisan Dost Tool Benchmarks ===\n")
    
    benchmarks = [
        ("crop_advisor (rabi)", crop_advisor, CONTEXT_RABI, FARMER),
        ("crop_advisor (kharif)", crop_advisor, CONTEXT_KHARIF, FARMER),
        ("fertilizer_calculator (wheat)", fertilizer_calculator, "wheat", 5.0),
        ("fertilizer_calculator (cotton)", fertilizer_calculator, "cotton", 10.0),
        ("pest_disease_doctor (whitefly)", pest_disease_doctor, "cotton leaves curling, tiny white insects", CONTEXT_KHARIF),
        ("pest_disease_doctor (aphid)", pest_disease_doctor, "okra leaves curled, sticky honeydew", CONTEXT_KHARIF, "okra"),
        ("mandi_price_lookup (wheat)", mandi_price_lookup, "wheat", "faisalabad"),
        ("mandi_price_lookup (cotton)", mandi_price_lookup, "cotton", "multan"),
        ("irrigation_weather (rabi)", irrigation_weather, CONTEXT_RABI, "faisalabad"),
        ("irrigation_weather (kharif)", irrigation_weather, CONTEXT_KHARIF, "multan"),
        ("profit_estimator (wheat)", profit_estimator, "wheat", 5.0, CONTEXT_RABI),
        ("profit_estimator (cotton)", profit_estimator, "cotton", 10.0, CONTEXT_KHARIF),
        ("govt_support_finder", govt_support_finder, FARMER, CONTEXT_RABI),
    ]
    
    results = []
    for name, func, *args in benchmarks:
        print(f"Benchmarking {name}...")
        result = await benchmark_tool(name, func, *args, iterations=10)
        results.append(result)
        print(f"  Mean: {result['mean_ms']:.1f}ms | Median: {result['median_ms']:.1f}ms | Min: {result['min_ms']:.1f}ms | Max: {result['max_ms']:.1f}ms")
    
    # Summary table
    print("\n=== Summary ===")
    print(f"{'Tool':<40} {'Mean (ms)':>10} {'Median (ms)':>12} {'Min (ms)':>10} {'Max (ms)':>10}")
    print("-" * 85)
    for r in results:
        print(f"{r['tool']:<40} {r['mean_ms']:>10.1f} {r['median_ms']:>12.1f} {r['min_ms']:>10.1f} {r['max_ms']:>10.1f}")
    
    # Overall stats
    all_means = [r['mean_ms'] for r in results]
    print(f"\nOverall average: {statistics.mean(all_means):.1f}ms")
    print(f"Total tools tested: {len(results)}")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_benchmarks())