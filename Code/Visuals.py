import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.ops import nearest_points
import numpy as np

print("Loading input files...")

gnaf_df = pd.read_parquet("../Source/gnaf_prop.parquet")

gnaf_prop = gpd.GeoDataFrame(
    gnaf_df,
    geometry=gpd.points_from_xy(gnaf_df.longitude, gnaf_df.latitude),
    crs="EPSG:7856"
)

# Load road network
roads = gpd.read_file("../Source/roads.gpkg")

# Ensure both layers share the same CRS
if gnaf_prop.crs != roads.crs:
    roads = roads.to_crs(gnaf_prop.crs)

print("Files loaded successfully")

sample_gnaf = gnaf_prop.head(5).copy()

def nearest(geom, roads_gdf):
    nearest_geom = roads_gdf.geometry.iloc[roads_gdf.distance(geom).idxmin()]
    return nearest_geom

print("Performing spatial join to find nearest road")
sample_gnaf["nearest_road_geom"] = sample_gnaf.geometry.apply(lambda x: nearest(x, roads))
sample_gnaf["distance_m"] = sample_gnaf.apply(lambda row: row.geometry.distance(row.nearest_road_geom), axis=1)

def calculate_orientation(point, nearest_line):
    nearest_point_on_line = nearest_points(point, nearest_line)[1]
    dx = nearest_point_on_line.x - point.x
    dy = nearest_point_on_line.y - point.y
    angle = np.degrees(np.arctan2(dy, dx))

    directions = [
        ("North", 0), ("North-East", 45), ("East", 90),
        ("South-East", 135), ("South", 180),
        ("South-West", -135), ("West", -90),
        ("North-West", -45)
    ]
    closest_dir = min(directions, key=lambda d: abs(angle - d[1]))
    return closest_dir[0]

print("Calculating orientation angles")
sample_gnaf["orientation"] = sample_gnaf.apply(
    lambda row: calculate_orientation(row.geometry, row.nearest_road_geom), axis=1
)

output_df = sample_gnaf[["address", "orientation", "distance_m"]]
output_df.to_csv("../Output/property_orientation_output.csv", index=False)
print("Output saved to '../Output/property_orientation_output.csv'")

print("Creating base map")

fig, ax = plt.subplots(figsize=(10, 8))
roads.plot(ax=ax, color='lightgrey', linewidth=0.8, label='Roads')
sample_gnaf.plot(ax=ax, color='blue', markersize=50, label='Properties')

# Zoom around sample properties
buffer = 100  # meters around properties
xmin, ymin, xmax, ymax = sample_gnaf.total_bounds
ax.set_xlim(xmin - buffer, xmax + buffer)
ax.set_ylim(ymin - buffer, ymax + buffer)

plt.title("Property Base Map")
plt.xlabel("Easting (m)")
plt.ylabel("Northing (m)")
plt.legend()
plt.tight_layout()
plt.savefig("../Output/sample_base_map.png", dpi=300)
plt.show()

print("Creating orientation map")

fig, ax = plt.subplots(figsize=(10, 8))
roads.plot(ax=ax, color='lightgrey', linewidth=0.8, label='Roads')
sample_gnaf.plot(ax=ax, color='blue', markersize=50, label='Properties')

# Draw arrows for each property orientation
for _, row in sample_gnaf.iterrows():
    point = row.geometry
    nearest_line = row.nearest_road_geom
    nearest_point = nearest_points(point, nearest_line)[1]

    ax.arrow(point.x, point.y,
             nearest_point.x - point.x,
             nearest_point.y - point.y,
             head_width=5, head_length=8, fc='orange', ec='orange', alpha=0.7)

# Apply same zoom
ax.set_xlim(xmin - buffer, xmax + buffer)
ax.set_ylim(ymin - buffer, ymax + buffer)

plt.title("Property Orientation Map (First 5 Properties)")
plt.xlabel("Easting (m)")
plt.ylabel("Northing (m)")
plt.legend()
plt.tight_layout()
plt.savefig("../Output/sample_orientation_map.png", dpi=300)
plt.show()

print("All visuals created successfully and zoomed properly")
