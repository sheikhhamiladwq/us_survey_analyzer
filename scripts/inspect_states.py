from pathlib import Path
import geopandas as gpd


BASE_DIR = Path(__file__).resolve().parent.parent

STATE_PATH = (
    BASE_DIR
    / "data"
    / "external"
    / "states"
    / "cb_2020_us_state_500k.shp"
)


print("Loading state boundaries...")

states = gpd.read_file(STATE_PATH)

print("\nDataset overview:")
print("-" * 40)

print("Number of records:", len(states))
print("CRS:", states.crs)

print("\nColumns:")
print(states.columns.tolist())

print("\nFirst five records:")
print(states.head())

print("\nState names:")
print(states["NAME"].tolist())