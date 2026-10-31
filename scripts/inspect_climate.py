from pathlib import Path
import rasterio

BASE_DIR = Path(__file__).resolve().parent.parent

raster_path = (
    BASE_DIR
    / "data"
    / "external"
    / "koppen_geiger"
    / "1991_2020"
    / "koppen_geiger_0p00833333.tif"
)

with rasterio.open(raster_path) as src:
    print("Climate dataset loaded successfully!")
    print("-" * 40)

    print("CRS:", src.crs)
    print("Dimensions:", src.width, "x", src.height)
    print("Resolution:", src.res)
    print("Number of bands:", src.count)
    print("Data type:", src.dtypes)
    print("NoData value:", src.nodata)
    print("Bounds:", src.bounds)