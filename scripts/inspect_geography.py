from pathlib import Path

print("Current working directory:", Path.cwd())
print("ZCTA directory exists:", Path("data/external/zcta").exists())



from pathlib import Path
import geopandas as gpd


# Locate the ZCTA shapefile
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ZCTA dataset directory
data_path = BASE_DIR / "data" / "external" / "zcta"

shapefiles = list(data_path.glob("*.shp"))

if not shapefiles:
    raise FileNotFoundError(
        f"No Shapefile found in: {data_path.resolve()}"
    )

shapefile = shapefiles[0]

# Load geographical data
zctas = gpd.read_file(shapefile)

# Inspect the dataset
print("Dataset loaded successfully!")
print("-" * 40)

print(f"Number of geographical areas: {len(zctas)}")

print("\nAvailable columns:")
print(zctas.columns.tolist())

print("\nCoordinate Reference System:")
print(zctas.crs)

print("\nFirst five records:")
print(zctas.head())

print("\nGeometry types:")
print(zctas.geometry.geom_type.value_counts())
