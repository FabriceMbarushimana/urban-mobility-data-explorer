"""
Data Cleaning Module
Handles missing values, duplicates, and outliers in NYC taxi data
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os

class DataCleaner:
    def __init__(self):
        self.cleaning_log = []
        self.excluded_records = []
        
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.cleaning_log.append(log_entry)
        print(log_entry)
    
    def clean_trip_data(self, df):
        """Main cleaning pipeline for trip data"""
        self.log(f"Starting cleaning process. Initial records: {len(df)}")
        initial_count = len(df)
        
        # Create copy to avoid modifying original
        df_clean = df.copy()
        
        # 1. Remove duplicates
        df_clean = self._remove_duplicates(df_clean)
        
        # 2. Handle missing values
        df_clean = self._handle_missing_values(df_clean)
        
        # 3. Remove outliers
        df_clean = self._remove_outliers(df_clean)
        
        # 4. Normalize data types
        df_clean = self._normalize_data_types(df_clean)
        
        final_count = len(df_clean)
        removed_count = initial_count - final_count
        removal_rate = (removed_count / initial_count) * 100
        
        self.log(f"Cleaning complete. Final records: {final_count}")
        self.log(f"Removed {removed_count} records ({removal_rate:.2f}%)")
        
        return df_clean
    
    def _remove_duplicates(self, df):
        """Remove duplicate trip records"""
        initial = len(df)
        df_clean = df.drop_duplicates()
        removed = initial - len(df_clean)
        
        if removed > 0:
            self.log(f"Removed {removed} duplicate records")
            self.excluded_records.append({
                'reason': 'Duplicate records',
                'count': removed
            })
        
        return df_clean
    
    def _handle_missing_values(self, df):
        """Handle missing values in critical columns"""
        initial = len(df)
        
        # Critical columns that cannot be missing
        critical_cols = ['tpep_pickup_datetime', 'tpep_dropoff_datetime', 
                        'PULocationID', 'DOLocationID', 'trip_distance', 
                        'fare_amount']
        
        # Check which critical columns exist
        existing_critical = [col for col in critical_cols if col in df.columns]
        
        # Remove rows with missing critical values
        df_clean = df.dropna(subset=existing_critical)
        removed = initial - len(df_clean)
        
        if removed > 0:
            self.log(f"Removed {removed} records with missing critical values")
            self.excluded_records.append({
                'reason': 'Missing critical values',
                'count': removed
            })
        
        return df_clean
    
    def _remove_outliers(self, df):
        """Remove logical outliers and anomalies"""
        initial = len(df)
        df_clean = df.copy()
        
        # Trip distance outliers (negative or unreasonably large)
        if 'trip_distance' in df_clean.columns:
            distance_mask = (df_clean['trip_distance'] > 0) & (df_clean['trip_distance'] <= 100)
            removed = len(df_clean) - distance_mask.sum()
            if removed > 0:
                self.log(f"Removed {removed} records with invalid trip distance")
                self.excluded_records.append({
                    'reason': 'Invalid trip distance (<=0 or >100 miles)',
                    'count': removed
                })
            df_clean = df_clean[distance_mask]
        
        # Fare amount outliers (negative or unreasonably large)
        if 'fare_amount' in df_clean.columns:
            fare_mask = (df_clean['fare_amount'] > 0) & (df_clean['fare_amount'] <= 500)
            removed = len(df_clean) - fare_mask.sum()
            if removed > 0:
                self.log(f"Removed {removed} records with invalid fare amount")
                self.excluded_records.append({
                    'reason': 'Invalid fare amount (<=0 or >$500)',
                    'count': removed
                })
            df_clean = df_clean[fare_mask]
        
        # Passenger count outliers
        if 'passenger_count' in df_clean.columns:
            passenger_mask = (df_clean['passenger_count'] > 0) & (df_clean['passenger_count'] <= 6)
            removed = len(df_clean) - passenger_mask.sum()
            if removed > 0:
                self.log(f"Removed {removed} records with invalid passenger count")
                self.excluded_records.append({
                    'reason': 'Invalid passenger count (<=0 or >6)',
                    'count': removed
                })
            df_clean = df_clean[passenger_mask]
        
        # Temporal outliers (dropoff before pickup)
        if 'tpep_pickup_datetime' in df_clean.columns and 'tpep_dropoff_datetime' in df_clean.columns:
            temporal_mask = df_clean['tpep_dropoff_datetime'] > df_clean['tpep_pickup_datetime']
            removed = len(df_clean) - temporal_mask.sum()
            if removed > 0:
                self.log(f"Removed {removed} records with invalid timestamps")
                self.excluded_records.append({
                    'reason': 'Dropoff time before pickup time',
                    'count': removed
                })
            df_clean = df_clean[temporal_mask]
        
        # Location ID outliers (must be valid zone IDs: 1-263)
        if 'PULocationID' in df_clean.columns:
            pu_mask = (df_clean['PULocationID'] >= 1) & (df_clean['PULocationID'] <= 263)
            removed = len(df_clean) - pu_mask.sum()
            if removed > 0:
                self.log(f"Removed {removed} records with invalid pickup location")
                self.excluded_records.append({
                    'reason': 'Invalid pickup location ID',
                    'count': removed
                })
            df_clean = df_clean[pu_mask]
        
        if 'DOLocationID' in df_clean.columns:
            do_mask = (df_clean['DOLocationID'] >= 1) & (df_clean['DOLocationID'] <= 263)
            removed = len(df_clean) - do_mask.sum()
            if removed > 0:
                self.log(f"Removed {removed} records with invalid dropoff location")
                self.excluded_records.append({
                    'reason': 'Invalid dropoff location ID',
                    'count': removed
                })
            df_clean = df_clean[do_mask]
        
        total_removed = initial - len(df_clean)
        self.log(f"Total outliers removed: {total_removed}")
        
        return df_clean
    
    def _normalize_data_types(self, df):
        """Normalize data types and formats"""
        df_clean = df.copy()
        
        # Normalize timestamps
        datetime_cols = ['tpep_pickup_datetime', 'tpep_dropoff_datetime']
        for col in datetime_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_datetime(df_clean[col])
                self.log(f"Normalized {col} to datetime")
        
        # Normalize numeric columns
        numeric_cols = ['trip_distance', 'fare_amount', 'extra', 'mta_tax', 
                       'tip_amount', 'tolls_amount', 'total_amount']
        for col in numeric_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Normalize integer columns
        int_cols = ['passenger_count', 'PULocationID', 'DOLocationID', 
                   'RatecodeID', 'payment_type']
        for col in int_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype('Int64')
        
        self.log("Data types normalized")
        
        return df_clean
    
    def save_exclusion_log(self, log_path='logs'):
        """Save exclusion log to file"""
        os.makedirs(log_path, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save detailed cleaning log
        log_file = os.path.join(log_path, f'cleaning_log_{timestamp}.log')
        with open(log_file, 'w') as f:
            f.write('\n'.join(self.cleaning_log))
        
        # Save exclusion summary
        exclusion_file = os.path.join(log_path, f'exclusion_log_{timestamp}.txt')
        with open(exclusion_file, 'w') as f:
            f.write("DATA CLEANING EXCLUSION LOG\n")
            f.write("=" * 50 + "\n\n")
            
            total_excluded = sum(record['count'] for record in self.excluded_records)
            f.write(f"Total Records Excluded: {total_excluded}\n\n")
            
            f.write("Breakdown by Reason:\n")
            f.write("-" * 50 + "\n")
            for record in self.excluded_records:
                f.write(f"{record['reason']}: {record['count']} records\n")
        
        self.log(f"Exclusion log saved to {exclusion_file}")
        return exclusion_file

if __name__ == "__main__":
    print("Data Cleaner Module - Ready for integration")

