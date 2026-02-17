"""
Data Loading Module
Loads raw NYC taxi data files: parquet, csv, and GeoJSON
"""
import pandas as pd
import json
import os
from datetime import datetime

class DataLoader:
    def __init__(self, raw_data_path='data/raw'):
        self.raw_data_path = raw_data_path
        self.log_messages = []
        
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        print(log_entry)
    
    def load_trip_data(self, filename):
        """Load yellow taxi trip data from parquet file"""
        try:
            filepath = os.path.join(self.raw_data_path, filename)
            self.log(f"Loading trip data from {filepath}")
            df = pd.read_parquet(filepath)
            self.log(f"Loaded {len(df)} trip records with {len(df.columns)} columns")
            return df
        except Exception as e:
            self.log(f"ERROR loading trip data: {str(e)}")
            raise
    
    def load_zone_lookup(self, filename='taxi_zone_lookup.csv'):
        """Load taxi zone lookup table"""
        try:
            filepath = os.path.join(self.raw_data_path, filename)
            self.log(f"Loading zone lookup from {filepath}")
            df = pd.read_csv(filepath)
            self.log(f"Loaded {len(df)} zone records")
            return df
        except Exception as e:
            self.log(f"ERROR loading zone lookup: {str(e)}")
            raise
    
    def load_zone_geojson(self, filename='taxi_zones.geojson'):
        """Load taxi zone GeoJSON spatial data"""
        try:
            filepath = os.path.join(self.raw_data_path, filename)
            self.log(f"Loading GeoJSON from {filepath}")
            with open(filepath, 'r') as f:
                geojson_data = json.load(f)
            num_features = len(geojson_data.get('features', []))
            self.log(f"Loaded {num_features} GeoJSON features")
            return geojson_data
        except Exception as e:
            self.log(f"ERROR loading GeoJSON: {str(e)}")
            raise
    
    def save_logs(self, log_path='logs'):
        """Save loading logs to file"""
        os.makedirs(log_path, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_path, f'data_loading_{timestamp}.log')
        with open(log_file, 'w') as f:
            f.write('\n'.join(self.log_messages))
        self.log(f"Logs saved to {log_file}")
        return log_file

if __name__ == "__main__":
    loader = DataLoader()
    
    # Example usage
    print("Data Loader Module - Ready for integration")
    print("Use this module to load trip data, zone lookup, and GeoJSON files")

