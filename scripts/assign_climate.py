from pathlib import Path
from rasterio.windows import Window

import geopandas as gpd
import rasterio


BASE_DIR = Path(__file__).resolve().parent.parent

ZCTA_PATH = (
    BASE_DIR
    / "data"
    / "external"
    / "zcta"
    / "cb_2020_us_zcta520_500k.shp"
)

CLIMATE_PATH = (
    BASE_DIR
    / "data"
    / "external"
    / "koppen_geiger"
    / "1991_2020"
    / "koppen_geiger_0p00833333.tif"
)

OUTPUT_PATH = (
    BASE_DIR
    / "output"
    / "datasets"
    / "zcta_climate.csv"
)


# Numeric raster value: (Köppen code, climate description)
CLIMATE_LEGEND = {
    1: ("Af", "Tropical, rainforest"),
    2: ("Am", "Tropical, monsoon"),
    3: ("Aw", "Tropical, savannah"),
    4: ("BWh", "Arid, desert, hot"),
    5: ("BWk", "Arid, desert, cold"),
    6: ("BSh", "Arid, steppe, hot"),
    7: ("BSk", "Arid, steppe, cold"),
    8: ("Csa", "Temperate, dry summer, hot summer"),
    9: ("Csb", "Temperate, dry summer, warm summer"),
    10: ("Csc", "Temperate, dry summer, cold summer"),
    11: ("Cwa", "Temperate, dry winter, hot summer"),
    12: ("Cwb", "Temperate, dry winter, warm summer"),
    13: ("Cwc", "Temperate, dry winter, cold summer"),
    14: ("Cfa", "Temperate, no dry season, hot summer"),
    15: ("Cfb", "Temperate, no dry season, warm summer"),
    16: ("Cfc", "Temperate, no dry season, cold summer"),
    17: ("Dsa", "Cold, dry summer, hot summer"),
    18: ("Dsb", "Cold, dry summer, warm summer"),
    19: ("Dsc", "Cold, dry summer, cold summer"),
    20: ("Dsd", "Cold, dry summer, very cold winter"),
    21: ("Dwa", "Cold, dry winter, hot summer"),
    22: ("Dwb", "Cold, dry winter, warm summer"),
    23: ("Dwc", "Cold, dry winter, cold summer"),
    24: ("Dwd", "Cold, dry winter, very cold winter"),
    25: ("Dfa", "Cold, no dry season, hot summer"),
    26: ("Dfb", "Cold, no dry season, warm summer"),
    27: ("Dfc", "Cold, no dry season, cold summer"),
    28: ("Dfd", "Cold, no dry season, very cold winter"),
    29: ("ET", "Polar, tundra"),
    30: ("EF", "Polar, frost"),
}


print("Loading ZCTA boundaries...")
zctas = gpd.read_file(ZCTA_PATH)

print("Calculating representative points...")
points = zctas.geometry.representative_point()

points = gpd.GeoDataFrame(
    geometry=points,
    crs=zctas.crs
).to_crs("EPSG:4326")

coordinates = [
    (point.x, point.y)
    for point in points.geometry
]


print("Sampling climate raster...")

with rasterio.open(CLIMATE_PATH) as src:

    sampled_values = [
        int(value[0])
        for value in src.sample(coordinates)
    ]

    assignment_methods = [
        "representative_point" if value != 0 else "nearest_valid_pixel"
        for value in sampled_values
    ]

    fallback_distances = [None] * len(sampled_values)

    radius = 5

    # Apply fallback only to points with NoData.
    for index, value in enumerate(sampled_values):

        if value != 0:
            continue

        point = points.geometry.iloc[index]
        row, col = src.index(point.x, point.y)

        window = Window(
            col - radius,
            row - radius,
            radius * 2 + 1,
            radius * 2 + 1
        )

        nearby_values = src.read(
            1,
            window=window,
            boundless=True,
            fill_value=0
        )

        valid_rows, valid_cols = (nearby_values > 0).nonzero()

        if len(valid_rows) == 0:
            assignment_methods[index] = "unclassified"
            continue

        distances = [
            ((r - radius) ** 2 + (c - radius) ** 2) ** 0.5
            for r, c in zip(valid_rows, valid_cols)
        ]

        nearest_index = distances.index(min(distances))

        sampled_values[index] = int(
            nearby_values[
                valid_rows[nearest_index],
                valid_cols[nearest_index]
            ]
        )

        fallback_distances[index] = distances[nearest_index]

zctas["climate_value"] = sampled_values

zctas["koppen_code"] = [
    CLIMATE_LEGEND.get(value, (None, None))[0]
    for value in sampled_values
]

zctas["climate_description"] = [
    CLIMATE_LEGEND.get(value, (None, None))[1]
    for value in sampled_values
]

zctas["assignment_method"] = assignment_methods
zctas["fallback_distance_pixels"] = fallback_distances

result = zctas[
    [
        "ZCTA5CE20",
        "climate_value",
        "koppen_code",
        "climate_description",
        "assignment_method",
        "fallback_distance_pixels",
    ]
].copy()

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
result.to_csv(OUTPUT_PATH, index=False)

print("\nClimate assignment completed!")
print("-" * 40)

print("Total ZCTAs:", len(result))
print("Successfully classified:", result["koppen_code"].notna().sum())
print("Missing classifications:", result["koppen_code"].isna().sum())

print("\nAssignment methods:")
print(result["assignment_method"].value_counts())

print("\nClimate classification counts:")
print(result["koppen_code"].value_counts(dropna=False))

print("\nFirst five records:")
print(result.head())

print("\nOutput saved to:")
print(OUTPUT_PATH)

