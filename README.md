# US Survey Geography & Climate Analyzer

A Python-based geospatial data analysis project demonstrating how survey responses can be enriched with geographic and climate information, analyzed, and visualized across the United States.

The project combines US Census ZIP Code Tabulation Area (ZCTA) boundaries, state and regional classifications, and Köppen–Geiger climate data to build a reusable geographic reference dataset.

A synthetic survey dataset is then used to demonstrate the complete analysis workflow.

**Important:** The survey data in this repository's demonstration is synthetic. It does not represent actual survey respondents or the US population.

## Project Overview

The workflow demonstrates how to:

- Map survey respondent distribution across US geographic areas.
- Associate ZIP codes with states and Census regions.
- Assign Köppen–Geiger climate classifications to geographic areas.
- Enrich individual survey records with geographic and climate attributes.
- Calculate respondent counts and percentages by ZIP code, state, region, and climate classification.
- Generate a geographic respondent density map.

## Technologies

- **Python** – Main programming language.
- **Pandas** – Data manipulation and analysis.
- **GeoPandas** – Geospatial data processing and spatial operations.
- **Shapely** – Geometric operations.
- **Rasterio** – Climate raster data extraction.
- **Matplotlib** – Geographic visualization.
- **Requests** – Data downloading.
- **OpenPyXL** – Excel file support.

## Data Sources

### 1. US Census ZCTA Boundaries

Source: [US Census Bureau – 2020 TIGER/Line Cartographic Boundaries](https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip)

Dataset: `cb_2020_us_zcta520_500k.shp`

These geographic boundaries provide the spatial reference for ZIP-code-level analysis.

**Note:** ZCTAs are Census Bureau approximations of ZIP-code geography. They are not identical to USPS ZIP-code delivery areas.

### 2. US State Boundaries

Source: [US Census Bureau – 2020 State Boundaries](https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_state_500k.zip)

Dataset: `cb_2020_us_state_500k.shp`

Used to associate geographic areas with states and Census regions.

The analysis includes the 50 states and Washington, DC.

### 3. Köppen–Geiger Climate Classification

Source: [GloH2O – Köppen–Geiger Climate Classification](https://www.gloh2o.org/koppen/)

Dataset: 1991–2020, 1 km resolution (`koppen_geiger_0p00833333.tif`).

The climate raster is used to assign a climate classification to each ZCTA.

Reference:

Beck, H. E., et al. (2023). High-resolution (1 km) Köppen–Geiger maps for 1901–2099 based on constrained CMIP6 projections. *Scientific Data*, 10, 724.

## Project Structure

```text
us_survey_analyzer/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│       ├── zcta/
│       ├── states/
│       └── koppen_geiger/
│
├── output/
│   ├── maps/
│   └── datasets/
│
├── scripts/
│   ├── inspect_geography.py
│   ├── inspect_climate.py
│   ├── assign_climate.py
│   ├── inspect_missing_climate.py
│   ├── check_nearby_climate.py
│   ├── inspect_states.py
│   ├── assign_state_regions.py
│   ├── build_reference_dataset.py
│   ├── generate_synthetic_survey.py
│   ├── enrich_survey_data.py
│   ├── analyze_survey.py
│   └── create_density_map.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation and Setup

Clone the repository:

```bash
git https://github.com/sheikhhamiladwq/us_survey_analyzer.git
cd us_survey_analyzer
```

Create and activate a virtual environment:

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### External Data Setup

Download and extract the three external datasets into their corresponding directories:

- Census ZCTA shapefile → `data/external/zcta/`
- Census state shapefile → `data/external/states/`
- Köppen–Geiger dataset → `data/external/koppen_geiger/`

For the climate dataset, use the 1991–2020, 1 km resolution raster and its corresponding legend.

The external datasets are not included in the Git repository and must be obtained from their original sources.

## Running the Analysis

Execute the scripts from the project root directory in the following order.

**1. Assign climate classifications**

```bash
python scripts/assign_climate.py
```

Generates:

`output/datasets/zcta_climate.csv`

**2. Assign states and Census regions**

```bash
python scripts/assign_state_regions.py
```

Generates:

`output/datasets/zcta_geography.csv`

**3. Build the geographic reference dataset**

```bash
python scripts/build_reference_dataset.py
```

Generates:

`output/datasets/zcta_reference.csv`

**4. Generate synthetic survey responses**

```bash
python scripts/generate_synthetic_survey.py
```

Generates:

`data/raw/synthetic_survey_responses.csv`

The demonstration dataset contains 900 synthetic responses distributed across 200 ZCTAs.

**5. Enrich survey records**

```bash
python scripts/enrich_survey_data.py
```

Generates:

`output/datasets/enriched_survey_responses.csv`

**6. Analyze survey distribution**

```bash
python scripts/analyze_survey.py
```

Generates respondent summaries by:

- ZCTA
- State
- Census region
- Climate classification

**7. Generate the density map**

```bash
python scripts/create_density_map.py
```

Generates:

`output/maps/respondent_density_map.png`

## Methodology

### Geographic Classification

Each ZCTA is assigned a state and Census region using geographic boundaries.

ZCTAs are matched to state polygons using representative points and spatial joins.

### Climate Assignment

A representative point is calculated for each ZCTA and transformed into the climate raster's coordinate reference system.

The corresponding raster cell is sampled to obtain its Köppen–Geiger classification.

For 120 ZCTAs where the representative point falls on a NoData cell, the nearest valid raster cell within a limited search window is used as a fallback.

The assignment method and fallback distance are retained in the climate dataset.

### Survey Enrichment

Survey records are joined to the geographic reference dataset using ZIP/ZCTA codes.

Each successfully matched response receives:

- State
- State abbreviation
- Census region
- Köppen–Geiger climate code
- Climate description

### Statistical Analysis

Respondent counts and percentages are calculated at four geographic or climate levels:

- ZIP code / ZCTA
- State
- Census region
- Climate classification

## Demonstration Results

The synthetic demonstration contains:

| Metric | Result |
|---|---:|
| Survey responses | 900 |
| Unique ZIP codes | 200 |
| Geographic reference ZCTAs | 33,642 |
| Jurisdictions | 51 |
| Successfully enriched responses | 900 |
| Unmatched survey responses | 0 |

The density map highlights ZCTAs containing synthetic respondents. Areas without survey responses are shown in grey, while areas without ZCTA coverage remain unfilled.

## Limitations

- Synthetic survey responses are used for demonstration purposes only. They are not statistically representative of the US population.
- ZCTAs approximate ZIP-code geography and do not cover every USPS ZIP code.
- Climate classifications are assigned using representative points rather than the dominant climate across the entire ZCTA.
- The nearest-valid-pixel fallback may use a raster cell outside the corresponding ZCTA.
- Climate data represents the 1991–2020 classification period, not real-time climate conditions.
- The density map visualizes the synthetic sample distribution, not population density.

## Potential Applications

The workflow can be adapted to real survey datasets to support:

- Geographic respondent distribution analysis.
- Regional segmentation.
- Climate-based market segmentation.
- Geographic data enrichment.
- Survey reporting and visualization.

The synthetic dataset can be replaced with actual survey responses while retaining the geographic reference and enrichment workflow.