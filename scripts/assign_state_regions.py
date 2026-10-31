from pathlib import Path

import geopandas as gpd


BASE_DIR = Path(__file__).resolve().parent.parent

ZCTA_PATH = (
    BASE_DIR
    / "data"
    / "external"
    / "zcta"
    / "cb_2020_us_zcta520_500k.shp"
)

STATE_PATH = (
    BASE_DIR
    / "data"
    / "external"
    / "states"
    / "cb_2020_us_state_500k.shp"
)

OUTPUT_PATH = (
    BASE_DIR
    / "output"
    / "datasets"
    / "zcta_geography.csv"
)


# Census regions based on state abbreviations.
CENSUS_REGIONS = {
    "Northeast": [
        "CT", "ME", "MA", "NH", "RI", "VT",
        "NJ", "NY", "PA"
    ],
    "Midwest": [
        "IL", "IN", "MI", "OH", "WI",
        "IA", "KS", "MN", "MO", "NE", "ND", "SD"
    ],
    "South": [
        "DE", "FL", "GA", "MD", "NC", "SC", "VA",
        "DC", "WV", "AL", "KY", "MS", "TN",
        "AR", "LA", "OK", "TX"
    ],
    "West": [
        "AZ", "CO", "ID", "MT", "NV", "NM", "UT", "WY",
        "AK", "CA", "HI", "OR", "WA"
    ],
}

STATE_TO_REGION = {
    state: region
    for region, states in CENSUS_REGIONS.items()
    for state in states
}


print("Loading ZCTA boundaries...")
zctas = gpd.read_file(ZCTA_PATH)

print("Loading state boundaries...")
states = gpd.read_file(STATE_PATH)

# Keep the 50 states and Washington DC.
valid_states = list(STATE_TO_REGION.keys())
states = states[states["STUSPS"].isin(valid_states)].copy()

print("Creating ZCTA representative points...")

points = zctas[["ZCTA5CE20", "geometry"]].copy()
points["geometry"] = points.geometry.representative_point()

# Match each representative point to its containing state.
print("Matching ZCTAs to states...")

joined = gpd.sjoin(
    points,
    states[["STUSPS", "NAME", "STATEFP", "geometry"]],
    how="left",
    predicate="within"
)

# Assign Census regions.
joined["census_region"] = joined["STUSPS"].map(STATE_TO_REGION)

result = joined[
    [
        "ZCTA5CE20",
        "STATEFP",
        "STUSPS",
        "NAME",
        "census_region",
    ]
].copy()

# Save the result.
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
result.to_csv(OUTPUT_PATH, index=False)

print("\nGeographic assignment completed!")
print("-" * 40)

print("Total ZCTAs:", len(result))
print("Matched to states:", result["STUSPS"].notna().sum())
print("Unmatched ZCTAs:", result["STUSPS"].isna().sum())

print("\nZCTAs by Census region:")
print(result["census_region"].value_counts(dropna=False))

print("\nUnmatched records:")
print(result[result["STUSPS"].isna()].head(10))

print("\nFirst five records:")
print(result.head())

print("\nOutput saved to:")
print(OUTPUT_PATH)

unmatched = result[result["STUSPS"].isna()].copy()

unmatched["zip_prefix"] = (
    unmatched["ZCTA5CE20"].str[:3]
)

print("\nUnmatched ZIP prefixes:")
print(unmatched["zip_prefix"].value_counts())

print("\nUnmatched ZCTA codes:")
print(
    result.loc[
        result["STUSPS"].isna(),
        "ZCTA5CE20"
    ].tolist()
)