from pathlib import Path
import random

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

REFERENCE_PATH = (
    BASE_DIR
    / "output"
    / "datasets"
    / "zcta_reference.csv"
)

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "synthetic_survey_responses.csv"
)

RANDOM_SEED = 42
TOTAL_RESPONDENTS = 900
TOTAL_ZCTAS = 200


random.seed(RANDOM_SEED)

print("Loading geographic reference dataset...")

reference = pd.read_csv(
    REFERENCE_PATH,
    dtype={"ZCTA5CE20": str}
)

# Select one ZCTA from each state and DC.
print("Selecting ZCTAs across all jurisdictions...")

selected_zctas = []

for state in sorted(reference["STUSPS"].unique()):
    state_zctas = reference.loc[
        reference["STUSPS"] == state,
        "ZCTA5CE20"
    ].tolist()

    selected_zctas.append(random.choice(state_zctas))

# Select additional ZCTAs to reach 200.
remaining_zctas = [
    zcta
    for zcta in reference["ZCTA5CE20"].tolist()
    if zcta not in selected_zctas
]

additional_zctas = random.sample(
    remaining_zctas,
    TOTAL_ZCTAS - len(selected_zctas)
)

selected_zctas.extend(additional_zctas)

# Give each selected ZCTA a baseline of one respondent.
respondent_zctas = selected_zctas.copy()

# Assign the remaining respondents using uneven random weights.
# This creates visible variation for the demonstration map.
weights = [
    random.randint(1, 8)
    for _ in selected_zctas
]

additional_responses = random.choices(
    selected_zctas,
    weights=weights,
    k=TOTAL_RESPONDENTS - len(selected_zctas)
)

respondent_zctas.extend(additional_responses)

# Shuffle respondent locations.
random.shuffle(respondent_zctas)

# Build the synthetic survey dataset.
survey = pd.DataFrame({
    "respondent_id": [
        f"R{i:04d}"
        for i in range(1, TOTAL_RESPONDENTS + 1)
    ],
    "zip_code": respondent_zctas,
})

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

survey.to_csv(OUTPUT_PATH, index=False)

print("\nSynthetic survey dataset generated!")
print("-" * 40)

print("Total respondents:", len(survey))
print("Unique ZIP codes:", survey["zip_code"].nunique())
print("ZIP codes selected:", len(selected_zctas))

print("\nRespondents per ZIP code:")
print(
    survey["zip_code"]
    .value_counts()
    .describe()
)

print("\nFirst five records:")
print(survey.head())

print("\nOutput saved to:")
print(OUTPUT_PATH)
