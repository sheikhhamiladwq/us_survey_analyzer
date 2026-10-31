from pathlib import Path

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator

BASE_DIR = Path(__file__).resolve().parent.parent

ZCTA_PATH = BASE_DIR / "data" / "external" / "zcta" / "cb_2020_us_zcta520_500k.shp"
STATE_PATH = BASE_DIR / "data" / "external" / "states" / "cb_2020_us_state_500k.shp"
REFERENCE_PATH = BASE_DIR / "output" / "datasets" / "zcta_reference.csv"
COUNTS_PATH = BASE_DIR / "output" / "datasets" / "respondent_counts_by_zcta.csv"
OUTPUT_PATH = BASE_DIR / "output" / "maps" / "respondent_density_map.png"

GREY = "#eeeeee"
CONUS = ("AL AZ AR CA CO CT DE DC FL GA ID IL IN IA KS KY LA ME MD MA MI MN MS "
         "MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA "
         "WV WI WY").split()

# Per-region projections (CONUS Albers, Alaska Albers, Hawaii Albers)
CRS_CONUS, CRS_AK, CRS_HI = "EPSG:5070", "EPSG:3338", "ESRI:102007"
# lon/lat windows used to drop far-flung geometry (Aleutians west of 170W, NW Hawaiian islets)
BOX_AK = (-170.0, 51.0, -129.0, 72.0)
BOX_HI = (-160.7, 18.8, -154.7, 22.3)

print("Loading geographic data...")
zctas = gpd.read_file(ZCTA_PATH)
states = gpd.read_file(STATE_PATH)
reference = pd.read_csv(REFERENCE_PATH, dtype={"ZCTA5CE20": str})
counts = pd.read_csv(COUNTS_PATH, dtype={"zip_code": str})

print("Preparing map dataset...")

# CHANGED: left merge so ZCTAs absent from the reference are not silently dropped.
map_data = zctas.merge(
    reference[["ZCTA5CE20", "STUSPS"]],
    on="ZCTA5CE20", how="left", validate="one_to_one",
)

# Fallback: assign a state to unmatched ZCTAs via a point-in-polygon join.
missing = map_data["STUSPS"].isna()
print("ZCTAs missing from reference:", int(missing.sum()))
if missing.any():
    pts = map_data.loc[missing, ["geometry"]].copy()
    pts["geometry"] = pts.representative_point()
    joined = gpd.sjoin(pts, states[["STUSPS", "geometry"]], how="left", predicate="within")
    joined = joined[~joined.index.duplicated()]
    map_data.loc[missing, "STUSPS"] = joined["STUSPS"]

map_data = map_data.merge(
    counts, left_on="ZCTA5CE20", right_on="zip_code", how="left", validate="one_to_one"
)
map_data["respondent_count"] = map_data["respondent_count"].fillna(0).astype(int)

# --- Diagnostics: these should read 200 and 900, with no unmatched ZIPs ---
print("ZCTA polygons loaded:", len(zctas), "| mapped:", len(map_data))
print("ZCTAs with respondents:", (map_data["respondent_count"] > 0).sum())
print("Total respondents mapped:", map_data["respondent_count"].sum())
print("Survey ZIPs with no ZCTA polygon:",
      sorted(set(counts["zip_code"]) - set(zctas["ZCTA5CE20"]))[:20])

# Keep only the 50 states and DC (this also excludes PR and territories).
states = states[states["STUSPS"].isin(CONUS + ["AK", "HI"])].copy()

# CHANGED: one shared scale for all panels, with a truncated colormap so that
# a count of 1 is visibly different from the grey "zero" fill.
VMIN, VMAX = 1, int(map_data["respondent_count"].max())
CMAP = LinearSegmentedColormap.from_list(
    "YlOrRd_trunc", mpl.colormaps["YlOrRd"](np.linspace(0.2, 1.0, 256))
)


def draw_panel(ax, codes, crs, lonlat_box=None, title=None):
    z = map_data[map_data["STUSPS"].isin(codes)]
    s = states[states["STUSPS"].isin(codes)]
    if lonlat_box:
        x0, y0, x1, y1 = lonlat_box
        z = z.cx[x0:x1, y0:y1]          # filter in lon/lat, before projecting
    z, s = z.to_crs(crs), s.to_crs(crs)

    # White state fill underneath: anything still white has no ZCTA polygon.
    s.plot(ax=ax, color="white", edgecolor="none", zorder=0)

    # CHANGED: no white edges on the grey layer (they wash out dense areas).
    z[z["respondent_count"] == 0].plot(
        ax=ax, color=GREY, edgecolor="face", linewidth=0.1, zorder=1
    )

    surveyed = z[z["respondent_count"] > 0]
    if not surveyed.empty:
        # CHANGED: explicit vmin/vmax shared by every panel, dark edge for visibility.
        surveyed.plot(
            ax=ax, column="respondent_count", cmap=CMAP, vmin=VMIN, vmax=VMAX,
            edgecolor="#333333", linewidth=0.3, zorder=2,
        )

    s.boundary.plot(ax=ax, color="#777777", linewidth=0.45, zorder=3)

    if lonlat_box and not z.empty:      # crop axes to the filtered ZCTAs
        xa, ya, xb, yb = z.total_bounds
        padx, pady = 0.03 * (xb - xa), 0.03 * (yb - ya)
        ax.set_xlim(xa - padx, xb + padx)
        ax.set_ylim(ya - pady, yb + pady)

    ax.set_aspect("equal")
    ax.set_axis_off()
    if title:
        ax.set_title(title, fontsize=11, fontweight="bold")


print("Creating map...")

# CHANGED: manual layout. Alaska and Hawaii are insets at the lower left of the
# CONUS map, and the colorbar has its own axes. Nudge these rectangles as needed.
fig = plt.figure(figsize=(15, 9.5))
ax_main = fig.add_axes([0.03, 0.14, 0.94, 0.76])
ax_ak = fig.add_axes([0.03, 0.14, 0.20, 0.22])
ax_hi = fig.add_axes([0.24, 0.14, 0.11, 0.10])
cax = fig.add_axes([0.38, 0.075, 0.24, 0.016])

draw_panel(ax_main, CONUS, CRS_CONUS, title="Contiguous United States")
draw_panel(ax_ak, ["AK"], CRS_AK, BOX_AK, title="Alaska")
draw_panel(ax_hi, ["HI"], CRS_HI, BOX_HI, title="Hawaii")
for a in (ax_ak, ax_hi):
    a.set_anchor("SW")

sm = mpl.cm.ScalarMappable(norm=mpl.colors.Normalize(VMIN, VMAX), cmap=CMAP)
cbar = fig.colorbar(sm, cax=cax, orientation="horizontal")
cbar.set_label("Synthetic respondents per ZCTA", labelpad=6)
cbar.ax.xaxis.set_label_position("top")
cbar.locator = MaxNLocator(integer=True)
cbar.update_ticks()

fig.legend(
    handles=[
        Patch(facecolor=GREY, edgecolor="none", label="ZCTA, no respondents"),
        Patch(facecolor="white", edgecolor="#777777", label="No ZCTA polygon (unpopulated)"),
    ],
    loc="lower right", bbox_to_anchor=(0.97, 0.05), frameon=False, fontsize=9,
)

fig.suptitle("US Synthetic Survey Respondent Density",
             fontsize=19, fontweight="bold", y=0.96)
fig.text(0.5, 0.025,
         "900 synthetic responses across 200 ZCTAs | 2020 Census ZCTA boundaries",
         ha="center", fontsize=10)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight")
plt.close(fig)

print("\nMap created successfully!")
print("Output saved to:", OUTPUT_PATH)