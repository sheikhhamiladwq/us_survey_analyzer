from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

SURVEY_PATH = (
    BASE_DIR
    / "output"
    / "datasets"
    / "enriched_survey_responses.csv"
)

OUTPUT_DIR = BASE_DIR / "output" / "datasets"


print("Loading enriched survey data...")

survey = pd.read_csv(
    SURVEY_PATH,
    dtype={"zip_code": str}
)


# 1. Respondent counts by ZIP code.
zip_summary = (
    survey.groupby("zip_code")
    .size()
    .reset_index(name="respondent_count")
    .sort_values("respondent_count", ascending=False)
)

# 2. Respondent counts by state.
state_summary = (
    survey.groupby(["state_abbr", "state"])
    .size()
    .reset_index(name="respondent_count")
    .sort_values("respondent_count", ascending=False)
)

# 3. Respondent counts by Census region.
region_summary = (
    survey.groupby("census_region")
    .size()
    .reset_index(name="respondent_count")
    .sort_values("respondent_count", ascending=False)
)

# 4. Respondent counts by climate classification.
climate_summary = (
    survey.groupby(["koppen_code", "climate_description"])
    .size()
    .reset_index(name="respondent_count")
    .sort_values("respondent_count", ascending=False)
)


# Add percentages to the summary datasets.
for summary in [
    state_summary,
    region_summary,
    climate_summary,
]:
    summary["percentage"] = (
        summary["respondent_count"]
        / len(survey)
        * 100
    ).round(2)


# Save all four outputs.
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

zip_summary.to_csv(
    OUTPUT_DIR / "respondent_counts_by_zcta.csv",
    index=False
)

state_summary.to_csv(
    OUTPUT_DIR / "respondent_counts_by_state.csv",
    index=False
)

region_summary.to_csv(
    OUTPUT_DIR / "respondent_counts_by_region.csv",
    index=False
)

climate_summary.to_csv(
    OUTPUT_DIR / "respondent_counts_by_climate.csv",
    index=False
)


print("\nSurvey analysis completed!")
print("-" * 40)

print("Total respondents:", len(survey))
print("Unique ZIP codes:", survey["zip_code"].nunique())

print("\nTop 10 ZIP codes:")
print(zip_summary.head(10).to_string(index=False))

print("\nRespondents by state:")
print(state_summary.to_string(index=False))

print("\nRespondents by Census region:")
print(region_summary.to_string(index=False))

print("\nRespondents by climate:")
print(climate_summary.to_string(index=False))

print("\nFour datasets saved to:")
print(OUTPUT_DIR)
