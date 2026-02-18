import geopandas as gpd
import os

def convert_shp_to_geojson(shp_path, geojson_path):
    """
    Converts a Shapefile to GeoJSON format.
    """
    try:
        print(f"Reading Shapefile from: {shp_path}")
        gdf = gpd.read_file(shp_path)

        # Ensure the CRS is EPSG:4326 (WGS84) for GeoJSON
        if gdf.crs != 'EPSG:4326':
            print(f"Reprojecting from {gdf.crs} to EPSG:4326...")
            gdf = gdf.to_crs('EPSG:4326')

        print(f"Writing GeoJSON to: {geojson_path}")
        gdf.to_file(geojson_path, driver='GeoJSON')
        print("Conversion successful!")

    except Exception as e:
        print(f"Error during conversion: {e}")

if __name__ == "__main__":
    # Define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shp_file = os.path.join(base_dir, 'data', 'raw', 'taxi_zones', 'taxi_zones.shp')
    geojson_file = os.path.join(base_dir, 'data', 'raw', 'taxi_zones.geojson')

    convert_shp_to_geojson(shp_file, geojson_file)

