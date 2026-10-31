from pathlib import Path

import geopandas as gpd
import pandas as pd
import rasterio


BASE_DIR = Path(__file__).resolve().parent.parent

ZCTA_PATH = (
    BASE_DIR / "data" / "external" / "zcta"
    / "cb_2020_us_zcta520_500k.shp"
)

CLIMATE_PATH = (
    BASE_DIR / "data" / "external" / "koppen_geiger"
    / "1991_2020" / "koppen_geiger_0p00833333.tif"
)

OUTPUT_PATH = (
    BASE_DIR / "output" / "datasets"
    / "missing_climate_zctas.csv"
)


print("Loading ZCTA boundaries...")
zctas = gpd.read_file(ZCTA_PATH)

# Calculate one point inside each ZCTA.
points = zctas.geometry.representative_point()

# Transform points to the raster's coordinate system.
points = gpd.GeoSeries(
    points,
    crs=zctas.crs
).to_crs("EPSG:4326")

coordinates = [
    (point.x, point.y)
    for point in points
]

print("Sampling raster values...")

with rasterio.open(CLIMATE_PATH) as src:
    values = [
        int(value[0])
        for value in src.sample(coordinates)
    ]

# Build a diagnostic table.
diagnostics = pd.DataFrame({
    "zcta": zctas["ZCTA5CE20"],
    "longitude": [point.x for point in points],
    "latitude": [point.y for point in points],
    "raster_value": values,
})

missing = diagnostics[diagnostics["raster_value"] == 0].copy()

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
missing.to_csv(OUTPUT_PATH, index=False)

print("\nDiagnostic results")
print("-" * 40)
print("Total ZCTAs:", len(diagnostics))
print("Missing classifications:", len(missing))
print("Distinct raster values among missing records:")
print(missing["raster_value"].value_counts())

print("\nGeographical extent of missing points:")
if not missing.empty:
    print("Longitude:", missing["longitude"].min(),
          "to", missing["longitude"].max())
    print("Latitude:", missing["latitude"].min(),
          "to", missing["latitude"].max())

print("\nFirst 30 missing ZCTAs:")
print(missing.head(30).to_string(index=False))

print("\nDiagnostic CSV saved to:")
print(OUTPUT_PATH)
