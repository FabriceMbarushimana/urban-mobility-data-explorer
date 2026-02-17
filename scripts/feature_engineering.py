"""
Feature Engineering Module
Creates derived features from cleaned NYC taxi data
"""
import pandas as pd
import numpy as np
from datetime import datetime

class FeatureEngineer:
    def __init__(self):
        self.feature_log = []
        
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.feature_log.append(log_entry)
        print(log_entry)
    
    def engineer_features(self, df):
        """Create all derived features"""
        self.log(f"Starting feature engineering on {len(df)} records")
        
        df_features = df.copy()
        
        # Feature 1: Trip Duration (minutes)
        df_features = self._add_trip_duration(df_features)
        
        # Feature 2: Fare per Mile
        df_features = self._add_fare_per_mile(df_features)
        
        # Feature 3: Pickup Hour Bucket
        df_features = self._add_pickup_hour_bucket(df_features)
        
        # Feature 4: Trip Speed (mph)
        df_features = self._add_trip_speed(df_features)
        
        # Feature 5: Time of Day Category
        df_features = self._add_time_of_day(df_features)
        
        # Feature 6: Day of Week
        df_features = self._add_day_of_week(df_features)
        
        self.log(f"Feature engineering complete. Added {len(df_features.columns) - len(df.columns)} new features")
        
        return df_features
    
    def _add_trip_duration(self, df):
        """
        Feature 1: Trip Duration in Minutes
        Justification: Essential metric for understanding trip efficiency and traffic patterns
        """
        if 'tpep_pickup_datetime' in df.columns and 'tpep_dropoff_datetime' in df.columns:
            df['trip_duration_minutes'] = (
                df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']
            ).dt.total_seconds() / 60
            
            # Remove unrealistic durations (negative or > 3 hours)
            df = df[(df['trip_duration_minutes'] > 0) & (df['trip_duration_minutes'] <= 180)]
            
            self.log(f"Added feature: trip_duration_minutes (mean: {df['trip_duration_minutes'].mean():.2f} min)")
        
        return df
    
    def _add_fare_per_mile(self, df):
        """
        Feature 2: Fare per Mile
        Justification: Reveals pricing efficiency and helps identify premium routes or surge pricing
        """
        if 'fare_amount' in df.columns and 'trip_distance' in df.columns:
            # Avoid division by zero
            df['fare_per_mile'] = np.where(
                df['trip_distance'] > 0,
                df['fare_amount'] / df['trip_distance'],
                0
            )
            
            # Cap unrealistic values
            df['fare_per_mile'] = df['fare_per_mile'].clip(upper=100)
            
            self.log(f"Added feature: fare_per_mile (mean: ${df['fare_per_mile'].mean():.2f}/mile)")
        
        return df
    
    def _add_pickup_hour_bucket(self, df):
        """
        Feature 3: Pickup Hour Bucket
        Justification: Enables time-based analysis and peak hour identification
        """
        if 'tpep_pickup_datetime' in df.columns:
            df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
            
            # Create hour buckets
            def categorize_hour(hour):
                if 6 <= hour < 12:
                    return 'Morning (6-12)'
                elif 12 <= hour < 18:
                    return 'Afternoon (12-18)'
                elif 18 <= hour < 24:
                    return 'Evening (18-24)'
                else:
                    return 'Night (0-6)'
            
            df['pickup_hour_bucket'] = df['pickup_hour'].apply(categorize_hour)
            
            self.log(f"Added feature: pickup_hour and pickup_hour_bucket")
        
        return df
    
    def _add_trip_speed(self, df):
        """
        Feature 4: Average Trip Speed (mph)
        Justification: Indicates traffic conditions and route efficiency
        """
        if 'trip_distance' in df.columns and 'trip_duration_minutes' in df.columns:
            # Convert minutes to hours
            df['trip_speed_mph'] = np.where(
                df['trip_duration_minutes'] > 0,
                (df['trip_distance'] / (df['trip_duration_minutes'] / 60)),
                0
            )
            
            # Cap unrealistic speeds (0-80 mph for NYC)
            df['trip_speed_mph'] = df['trip_speed_mph'].clip(lower=0, upper=80)
            
            self.log(f"Added feature: trip_speed_mph (mean: {df['trip_speed_mph'].mean():.2f} mph)")
        
        return df
    
    def _add_time_of_day(self, df):
        """
        Feature 5: Time of Day Category
        Justification: Broader temporal categorization for pattern analysis
        """
        if 'pickup_hour' in df.columns:
            def categorize_time_of_day(hour):
                if 5 <= hour < 9:
                    return 'Morning Rush'
                elif 9 <= hour < 17:
                    return 'Midday'
                elif 17 <= hour < 20:
                    return 'Evening Rush'
                else:
                    return 'Off-Peak'
            
            df['time_of_day'] = df['pickup_hour'].apply(categorize_time_of_day)
            
            self.log(f"Added feature: time_of_day")
        
        return df
    
    def _add_day_of_week(self, df):
        """
        Feature 6: Day of Week
        Justification: Enables weekday vs weekend pattern analysis
        """
        if 'tpep_pickup_datetime' in df.columns:
            df['day_of_week'] = df['tpep_pickup_datetime'].dt.day_name()
            df['is_weekend'] = df['tpep_pickup_datetime'].dt.dayofweek >= 5
            
            self.log(f"Added feature: day_of_week and is_weekend")
        
        return df
    
    def get_feature_summary(self, df):
        """Generate summary statistics for engineered features"""
        summary = {}
        
        numeric_features = ['trip_duration_minutes', 'fare_per_mile', 
                           'trip_speed_mph', 'pickup_hour']
        
        for feature in numeric_features:
            if feature in df.columns:
                summary[feature] = {
                    'mean': df[feature].mean(),
                    'median': df[feature].median(),
                    'std': df[feature].std(),
                    'min': df[feature].min(),
                    'max': df[feature].max()
                }
        
        return summary
    
    def save_feature_log(self, log_path='logs'):
        """Save feature engineering log"""
        import os
        os.makedirs(log_path, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_path, f'feature_engineering_{timestamp}.log')
        
        with open(log_file, 'w') as f:
            f.write("FEATURE ENGINEERING LOG\n")
            f.write("=" * 50 + "\n\n")
            f.write('\n'.join(self.feature_log))
            f.write("\n\n")
            f.write("DERIVED FEATURES:\n")
            f.write("-" * 50 + "\n")
            f.write("1. trip_duration_minutes: Time between pickup and dropoff\n")
            f.write("2. fare_per_mile: Fare amount divided by trip distance\n")
            f.write("3. pickup_hour_bucket: Categorized time periods\n")
            f.write("4. trip_speed_mph: Average speed during trip\n")
            f.write("5. time_of_day: Rush hour vs off-peak categorization\n")
            f.write("6. day_of_week: Day name and weekend indicator\n")
        
        self.log(f"Feature log saved to {log_file}")
        return log_file

if __name__ == "__main__":
    print("Feature Engineering Module - Ready for integration")

