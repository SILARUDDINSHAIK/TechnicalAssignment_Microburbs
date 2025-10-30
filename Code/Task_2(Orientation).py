import geopandas as gpd
import pandas as pd
import math
from shapely.geometry import Point, LineString, MultiLineString

# =============================================================================
# Source File Analysis and Property Orientation Calculation
# =============================================================================

# 1. Load Input Files
print("Loading source files...")

roads = gpd.read_file("../Source/roads.gpkg")
cadastre = gpd.read_file("../Source/cadastre.gpkg")
gnaf_prop = pd.read_parquet("../Source/gnaf_prop.parquet")
transactions = pd.read_parquet("../Source/transactions.parquet")

print("Files loaded successfully.")
print(f"Row counts - Roads: {len(roads)}, Cadastre: {len(cadastre)}, GNAF Properties: {len(gnaf_prop)}, Transactions: {len(transactions)}")

# 2. Prepare Property Points
print("Preparing property points...")

gnaf_prop = gpd.GeoDataFrame(
    gnaf_prop,
    geometry=gpd.points_from_xy(gnaf_prop.longitude, gnaf_prop.latitude),
    crs="EPSG:4326"
)

# Reproject to metric CRS (metres)
roads = roads.to_crs(epsg=7856)
gnaf_prop = gnaf_prop.to_crs(epsg=7856)

# 3. Find Nearest Road
print("Finding nearest road for each property...")

nearest = gpd.sjoin_nearest(
    gnaf_prop,
    roads[['geometry']],
    how="left",
    distance_col="distance_m"
)

# Rename geometry and retain both geometries
nearest = nearest.rename(columns={'geometry': 'property_geom'})
nearest['road_geom'] = nearest.apply(
    lambda row: roads.iloc[row['index_right']].geometry if pd.notnull(row['index_right']) else None,
    axis=1
)

nearest = gpd.GeoDataFrame(nearest, geometry='property_geom', crs=gnaf_prop.crs)

print("Spatial join completed successfully.")

# 4. Orientation Calculation
def calculate_orientation(point_geom, road_geom):
    """Calculate orientation angle (in degrees) of the property relative to the nearest road."""
    try:
        if road_geom is None or point_geom is None:
            return None

        if isinstance(road_geom, MultiLineString):
            line = min(road_geom.geoms, key=lambda g: point_geom.distance(g))
        elif isinstance(road_geom, LineString):
            line = road_geom
        else:
            return None

        nearest_point = line.interpolate(line.project(point_geom))
        step_distance = 1.0
        next_point = line.interpolate(line.project(point_geom) + step_distance)

        dx = next_point.x - nearest_point.x
        dy = next_point.y - nearest_point.y

        angle_rad = math.atan2(dy, dx)
        angle_deg = (math.degrees(angle_rad) + 360) % 360
        return round(angle_deg, 2)
    except Exception:
        return None


def angle_to_direction(angle):
    """Convert angle in degrees to compass direction."""
    if angle is None:
        return None
    directions = [
        "North", "North-East", "East", "South-East",
        "South", "South-West", "West", "North-West"
    ]
    index = int((angle + 22.5) // 45) % 8
    return directions[index]


print("Calculating property orientations...")

nearest['orientation_deg'] = nearest.apply(
    lambda r: calculate_orientation(r['property_geom'], r['road_geom']),
    axis=1
)
nearest['orientation'] = nearest['orientation_deg'].apply(angle_to_direction)

# 5. Build Final Output
output = nearest[['address', 'orientation', 'distance_m']].copy()
output['distance_m'] = output['distance_m'].round(2)

output.to_csv("../Output/property_orientations.csv", index=False)

print("Orientation analysis completed successfully.")
print("Output saved to 'property_orientations.csv'.")
print(output.head(10))
