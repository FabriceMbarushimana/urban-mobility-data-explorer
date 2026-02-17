"""
Main Data Pipeline
Orchestrates the complete data processing workflow:
1. Load raw data
2. Clean and validate
3. Engineer features
4. Save processed data
"""
import os
import sys
from datetime import datetime
import pandas as pd

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.load_data import DataLoader
from scripts.clean_data import DataCleaner
from scripts.feature_engineering import FeatureEngineer

class DataPipeline:
    def __init__(self, raw_data_path='data/raw', processed_data_path='data/processed'):
        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path
        self.loader = DataLoader(raw_data_path)
        self.cleaner = DataCleaner()
        self.engineer = FeatureEngineer()
        
        # Ensure directories exist
        os.makedirs(raw_data_path, exist_ok=True)
        os.makedirs(processed_data_path, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
    def run_pipeline(self, trip_data_filename, zone_lookup_filename='taxi_zone_lookup.csv', 
                     zone_geojson_filename='taxi_zones.geojson'):
        """Execute the complete data pipeline"""
        
        print("\n" + "="*60)
        print("NYC TAXI DATA PROCESSING PIPELINE")
        print("="*60 + "\n")
        
        start_time = datetime.now()
        
        # Step 1: Load Data
        print("\n[STEP 1] Loading Raw Data...")
        print("-" * 60)
        trip_data = self.loader.load_trip_data(trip_data_filename)
        zone_lookup = self.loader.load_zone_lookup(zone_lookup_filename)
        
        try:
            zone_geojson = self.loader.load_zone_geojson(zone_geojson_filename)
        except:
            print("Warning: GeoJSON file not found. Continuing without spatial data.")
            zone_geojson = None
        
        # Step 2: Integrate Zone Information
        print("\n[STEP 2] Integrating Zone Lookup Data...")
        print("-" * 60)
        trip_data = self._integrate_zone_data(trip_data, zone_lookup)
        
        # Step 3: Clean Data
        print("\n[STEP 3] Cleaning Data...")
        print("-" * 60)
        trip_data_clean = self.cleaner.clean_trip_data(trip_data)
        
        # Step 4: Engineer Features
        print("\n[STEP 4] Engineering Features...")
        print("-" * 60)
        trip_data_final = self.engineer.engineer_features(trip_data_clean)
        
        # Step 5: Save Processed Data
        print("\n[STEP 5] Saving Processed Data...")
        print("-" * 60)
        self._save_processed_data(trip_data_final, zone_lookup, zone_geojson)
        
        # Step 6: Generate Reports
        print("\n[STEP 6] Generating Reports and Logs...")
        print("-" * 60)
        self._generate_reports(trip_data_final)
        
        # Save all logs
        self.loader.save_logs()
        self.cleaner.save_exclusion_log()
        self.engineer.save_feature_log()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "="*60)
        print(f"PIPELINE COMPLETE - Duration: {duration:.2f} seconds")
        print("="*60 + "\n")
        
        return trip_data_final
    
    def _integrate_zone_data(self, trip_data, zone_lookup):
        """Merge trip data with zone lookup information"""
        
        # Merge pickup location
        trip_data = trip_data.merge(
            zone_lookup,
            left_on='PULocationID',
            right_on='LocationID',
            how='left',
            suffixes=('', '_pickup')
        )
        trip_data.rename(columns={
            'Borough': 'pickup_borough',
            'Zone': 'pickup_zone',
            'service_zone': 'pickup_service_zone'
        }, inplace=True)
        trip_data.drop('LocationID', axis=1, inplace=True, errors='ignore')
        
        # Merge dropoff location
        trip_data = trip_data.merge(
            zone_lookup,
            left_on='DOLocationID',
            right_on='LocationID',
            how='left',
            suffixes=('', '_dropoff')
        )
        trip_data.rename(columns={
            'Borough': 'dropoff_borough',
            'Zone': 'dropoff_zone',
            'service_zone': 'dropoff_service_zone'
        }, inplace=True)
        trip_data.drop('LocationID', axis=1, inplace=True, errors='ignore')
        
        print(f"Integrated zone data. Added borough and zone information.")
        
        return trip_data
    
    def _save_processed_data(self, trip_data, zone_lookup, zone_geojson):
        """Save processed data to files"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save main processed trip data
        trip_output = os.path.join(self.processed_data_path, f'processed_trip_data_{timestamp}.csv')
        trip_data.to_csv(trip_output, index=False)
        print(f"Saved processed trip data: {trip_output}")
        
        # Also save as parquet for efficiency
        trip_parquet = os.path.join(self.processed_data_path, f'processed_trip_data_{timestamp}.parquet')
        trip_data.to_parquet(trip_parquet, index=False)
        print(f"Saved processed trip data (parquet): {trip_parquet}")
        
        # Save zone lookup
        zone_output = os.path.join(self.processed_data_path, 'zone_lookup.csv')
        zone_lookup.to_csv(zone_output, index=False)
        print(f"Saved zone lookup: {zone_output}")
        
        # Save GeoJSON if available
        if zone_geojson:
            import json
            geojson_output = os.path.join(self.processed_data_path, 'zone_geojson.json')
            with open(geojson_output, 'w') as f:
                json.dump(zone_geojson, f)
            print(f"Saved GeoJSON: {geojson_output}")
    
    def _generate_reports(self, trip_data):
        """Generate summary reports"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join('logs', f'pipeline_summary_{timestamp}.txt')
        
        with open(report_file, 'w') as f:
            f.write("NYC TAXI DATA PIPELINE SUMMARY REPORT\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("DATASET OVERVIEW\n")
            f.write("-"*60 + "\n")
            f.write(f"Total Records: {len(trip_data):,}\n")
            f.write(f"Total Columns: {len(trip_data.columns)}\n\n")
            
            f.write("COLUMN LIST\n")
            f.write("-"*60 + "\n")
            for col in trip_data.columns:
                f.write(f"  - {col}\n")
            f.write("\n")
            
            f.write("DATA QUALITY METRICS\n")
            f.write("-"*60 + "\n")
            f.write(f"Missing Values: {trip_data.isnull().sum().sum()}\n")
            f.write(f"Duplicate Rows: {trip_data.duplicated().sum()}\n\n")
            
            f.write("ENGINEERED FEATURES SUMMARY\n")
            f.write("-"*60 + "\n")
            feature_summary = self.engineer.get_feature_summary(trip_data)
            for feature, stats in feature_summary.items():
                f.write(f"\n{feature}:\n")
                for stat_name, stat_value in stats.items():
                    f.write(f"  {stat_name}: {stat_value:.2f}\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write("END OF REPORT\n")
        
        print(f"Generated summary report: {report_file}")

def main():
    """Main execution function"""
    
    # Check if raw data exists
    raw_data_path = 'data/raw'
    if not os.path.exists(raw_data_path):
        print(f"\nERROR: Raw data directory not found: {raw_data_path}")
        print("\nPlease create the directory and add your data files:")
        print("  1. Yellow taxi trip data (.parquet file)")
        print("  2. taxi_zone_lookup.csv")
        print("  3. taxi_zones.geojson")
        print("\nExample:")
        print(f"  {raw_data_path}/yellow_tripdata_2024-01.parquet")
        print(f"  {raw_data_path}/taxi_zone_lookup.csv")
        print(f"  {raw_data_path}/taxi_zones.geojson")
        return
    
    # List available parquet files
    parquet_files = [f for f in os.listdir(raw_data_path) if f.endswith('.parquet')]
    
    if not parquet_files:
        print(f"\nERROR: No .parquet files found in {raw_data_path}")
        print("Please add a yellow taxi trip data file (.parquet)")
        return
    
    print("\nAvailable trip data files:")
    for i, file in enumerate(parquet_files, 1):
        print(f"  {i}. {file}")
    
    # Use first file or allow selection
    if len(parquet_files) == 1:
        selected_file = parquet_files[0]
        print(f"\nUsing: {selected_file}")
    else:
        try:
            choice = int(input("\nSelect file number (or press Enter for first file): ") or "1")
            selected_file = parquet_files[choice - 1]
        except:
            selected_file = parquet_files[0]
            print(f"Using default: {selected_file}")
    
    # Run pipeline
    pipeline = DataPipeline()
    processed_data = pipeline.run_pipeline(selected_file)
    
    print("\nProcessed data shape:", processed_data.shape)
    print("\nFirst few rows:")
    print(processed_data.head())
    
    print("\n✓ Pipeline execution complete!")
    print(f"✓ Processed data saved to: data/processed/")
    print(f"✓ Logs saved to: logs/")

if __name__ == "__main__":
    main()

