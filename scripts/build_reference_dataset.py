from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

GEOGRAPHY_PATH = (
    BASE_DIR
    / "output"
    / "datasets"
    / "zcta_geography.csv"
)

CLIMATE_PATH = (
    BASE_DIR
    / "output"
    / "datasets"
    / "zcta_climate.csv"
)

OUTPUT_PATH = (
    BASE_DIR
    / "output"
    / "datasets"
    / "zcta_reference.csv"
)


print("Loading geographic datasets...")

geography = pd.read_csv(
    GEOGRAPHY_PATH,
    dtype={"ZCTA5CE20": str, "STATEFP": str}
)

climate = pd.read_csv(
    CLIMATE_PATH,
    dtype={"ZCTA5CE20": str}
)


print("Filtering unsupported territories...")

# Retain only ZCTAs matched to the 50 states and DC.
geography = geography.dropna(subset=["STUSPS"]).copy()


print("Merging geography and climate data...")

reference = geography.merge(
    climate,
    on="ZCTA5CE20",
    how="inner",
    validate="one_to_one"
)


# Select and organize the final columns.
reference = reference[
    [
        "ZCTA5CE20",
        "STATEFP",
        "STUSPS",
        "NAME",
        "census_region",
        "climate_value",
        "koppen_code",
        "climate_description",
    ]
].copy()


OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

reference.to_csv(
    OUTPUT_PATH,
    index=False
)


print("\nReference dataset completed!")
print("-" * 40)

print("Total ZCTAs:", len(reference))
print("Unique ZCTAs:", reference["ZCTA5CE20"].nunique())

print("\nRecords by Census region:")
print(reference["census_region"].value_counts())

print("\nRecords by state:")
print(reference["STUSPS"].value_counts().sort_index())

print("\nMissing values:")
print(reference.isna().sum())

print("\nFirst five records:")
print(reference.head())

print("\nOutput saved to:")
print(OUTPUT_PATH)
