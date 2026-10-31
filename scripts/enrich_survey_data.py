
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

SURVEY_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "synthetic_survey_responses.csv"
)

REFERENCE_PATH = (
    BASE_DIR
    / "output"
    / "datasets"
    / "zcta_reference.csv"
)

OUTPUT_PATH = (
    BASE_DIR
    / "output"
    / "datasets"
    / "enriched_survey_responses.csv"
)


print("Loading survey responses...")

survey = pd.read_csv(
    SURVEY_PATH,
    dtype={"zip_code": str}
)

print("Loading geographic reference...")

reference = pd.read_csv(
    REFERENCE_PATH,
    dtype={"ZCTA5CE20": str}
)


# Select and rename the reference columns.
reference = reference[
    [
        "ZCTA5CE20",
        "STUSPS",
        "NAME",
        "census_region",
        "koppen_code",
        "climate_description",
    ]
].rename(
    columns={
        "ZCTA5CE20": "zip_code",
        "STUSPS": "state_abbr",
        "NAME": "state",
    }
)


print("Enriching survey responses...")

enriched = survey.merge(
    reference,
    on="zip_code",
    how="left",
    validate="many_to_one",
    indicator=True
)


# Check whether every survey ZIP code was matched.
unmatched = enriched[enriched["_merge"] != "both"]

print("\nEnrichment validation:")
print("-" * 40)

print("Total responses:", len(enriched))
print("Successfully matched:", len(enriched) - len(unmatched))
print("Unmatched responses:", len(unmatched))

if not unmatched.empty:
    print("\nUnmatched ZIP codes:")
    print(unmatched["zip_code"].unique())

# Remove the temporary merge indicator.
enriched = enriched.drop(columns=["_merge"])

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

enriched.to_csv(
    OUTPUT_PATH,
    index=False
)


print("\nEnriched dataset completed!")
print("-" * 40)

print("First five records:")
print(enriched.head())

print("\nMissing values:")
print(enriched.isna().sum())

print("\nOutput saved to:")
print(OUTPUT_PATH)
