"""
Source File Analysis
--------------------
Performs an exploratory analysis of the four main source datasets:
    - roads.gpkg,cadastre.gpkg,gnaf_prop.parquet,transactions.parquet
Author: Silaruddin Shaik
"""

import geopandas as gpd
import pandas as pd
import os


def analyze_file(filepath):
    """Read and summarize the given spatial or tabular file."""
    print("\n" + "=" * 80)
    print(f"Analyzing file: {os.path.basename(filepath)}")
    print("=" * 80)

    try:
        # Detect file type and load appropriately
        if filepath.endswith(".gpkg"):
            df = gpd.read_file(filepath)
            filetype = "GeoPackage (spatial)"
        elif filepath.endswith(".parquet"):
            try:
                df = gpd.read_parquet(filepath)
                filetype = "Parquet (GeoDataFrame)"
            except Exception:
                df = pd.read_parquet(filepath)
                filetype = "Parquet (DataFrame)"
        else:
            print(f"Unsupported file format: {filepath}")
            return

        # Print summary information
        print(f"File type: {filetype}")
        print(f"Number of rows: {len(df):,}")
        print(f"Columns: {list(df.columns)}")

        # Geometry information, if applicable
        if isinstance(df, gpd.GeoDataFrame):
            geom_col = df.geometry.name if df.geometry is not None else "N/A"
            geom_types = df.geom_type.value_counts().to_dict()
            print(f"Geometry column: {geom_col}")
            print(f"Geometry types: {geom_types}")

        # Display sample data
        print("\nSample data (first 10 rows):")
        print(df.head(10))

    except Exception as e:
        print(f"Error reading {filepath}: {e}")


if __name__ == "__main__":
    print("Starting source file analysis...\n")

    files_to_check = [
        "roads.gpkg",
        "cadastre.gpkg",
        "gnaf_prop.parquet",
        "transactions.parquet"
    ]

    for file in files_to_check:
        if os.path.exists(file):
            analyze_file(file)
        else:
            print(f"File not found: {file}")

    print("\nSource file analysis complete.")
