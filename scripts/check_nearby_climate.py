from pathlib import Path

import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.windows import Window


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
    / "nearby_climate_diagnostic.csv"
)

RADIUS = 5  # Search up to 5 raster pixels in each direction.


zctas = gpd.read_file(ZCTA_PATH)

points = gpd.GeoSeries(
    zctas.geometry.representative_point(),
    crs=zctas.crs
).to_crs("EPSG:4326")

results = []

with rasterio.open(CLIMATE_PATH) as src:

    for zcta, point in zip(zctas["ZCTA5CE20"], points):

        row, col = src.index(point.x, point.y)

        window = Window(
            col - RADIUS,
            row - RADIUS,
            RADIUS * 2 + 1,
            RADIUS * 2 + 1
        )

        values = src.read(
            1,
            window=window,
            boundless=True,
            fill_value=0
        )

        # Skip points that already have a valid climate value.
        if values[RADIUS, RADIUS] != 0:
            continue

        valid_rows, valid_cols = (values > 0).nonzero()

        if len(valid_rows) == 0:
            nearest_distance = None
            nearest_value = None
        else:
            distances = [
                ((r - RADIUS) ** 2 + (c - RADIUS) ** 2) ** 0.5
                for r, c in zip(valid_rows, valid_cols)
            ]

            nearest_index = distances.index(min(distances))

            nearest_distance = distances[nearest_index]
            nearest_value = int(
                values[
                    valid_rows[nearest_index],
                    valid_cols[nearest_index]
                ]
            )

        results.append({
            "zcta": zcta,
            "longitude": point.x,
            "latitude": point.y,
            "nearest_pixel_distance": nearest_distance,
            "nearest_climate_value": nearest_value,
        })


diagnostics = pd.DataFrame(results)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
diagnostics.to_csv(OUTPUT_PATH, index=False)

print("Missing ZCTAs checked:", len(diagnostics))
print("\nNearest valid pixel distance:")
print(
    diagnostics["nearest_pixel_distance"]
    .value_counts(dropna=False)
    .sort_index()
)

print("\nDistance summary:")
print(diagnostics["nearest_pixel_distance"].describe())

print("\nFirst 30 records:")
print(diagnostics.head(30).to_string(index=False))

print("\nSaved to:", OUTPUT_PATH)
