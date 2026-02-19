
# CUSTOM ALGORITHMS MODULE

# This module implements custom algorithms from scratch without using built-in
# sorting or statistical functions. These algorithms demonstrate fundamental
# computer science concepts and data structure & algorithms knowledge.
#
# Included Algorithms:
# 1. CustomSort - QuickSort implementation for route ranking
# 2. OutlierDetector - IQR-based anomaly detection for fare analysis
# 3. TripAggregator - Manual data aggregation by time periods
# 4. SpeedAnalyzer - Congestion pattern identification



# CLASS: CustomSort

# Implements QuickSort algorithm for efficient sorting of route data
# QuickSort is a divide-and-conquer algorithm that works by selecting a
# 'pivot' element and partitioning the array around it.


class CustomSort:
    """
    Custom sorting algorithm implementation using QuickSort.
    
    QuickSort Algorithm Overview:
    - Divide and conquer approach
    - Efficient for large datasets
    - In-place sorting (minimal extra memory)
    
    Performance Characteristics:
    - Time Complexity: O(n log n) average case, O(n²) worst case
    - Space Complexity: O(log n) for recursion stack
    - Best for: Large datasets where average performance matters
    
    Note: Worst case O(n²) occurs when pivot selection is poor
    (e.g., already sorted array with last element as pivot)
    """
    
    def partition(self, arr, low, high, key):
        """
        Partition array around pivot element.
        
        This is the core operation of QuickSort. It rearranges the array
        such that all elements greater than or equal to the pivot come
        before it, and all elements less than the pivot come after it.
        
        Args:
            arr: Array to partition
            low: Starting index of partition range
            high: Ending index of partition range (contains pivot)
            key: Dictionary key to compare (e.g., 'trip_count')
            
        Returns:
            Final position of pivot element
            
        Algorithm Steps:
        1. Choose last element as pivot
        2. Initialize partition index (i) as low - 1
        3. Iterate through array from low to high-1
        4. If current element >= pivot, swap with element at i+1
        5. Place pivot in correct position
        """
        pivot = arr[high][key]  # Select last element as pivot value
        i = low - 1             # Initialize partition index
        
        # Rearrange elements based on pivot comparison
        for j in range(low, high):
            if arr[j][key] >= pivot:  # For descending order (largest first)
                i += 1
                arr[i], arr[j] = arr[j], arr[i]  # Swap elements
        
        # Place pivot in its correct position
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1  # Return pivot's final position
    
    def quicksort(self, arr, low, high, key):
        """
        Recursive QuickSort implementation.
        
        This method recursively sorts the array by partitioning it around
        a pivot and then sorting the left and right subarrays.
        
        Args:
            arr: Array to sort (modified in-place)
            low: Starting index of subarray to sort
            high: Ending index of subarray to sort
            key: Dictionary key to sort by
            
        Recursion Process:
        1. Base case: If low >= high, array is sorted (0 or 1 element)
        2. Partition array and get pivot index
        3. Recursively sort left subarray (elements before pivot)
        4. Recursively sort right subarray (elements after pivot)
        """
        if low < high:
            # Partition array and get pivot index
            pi = self.partition(arr, low, high, key)
            
            # Recursively sort elements before and after partition
            self.quicksort(arr, low, pi - 1, key)   # Sort left subarray
            self.quicksort(arr, pi + 1, high, key)  # Sort right subarray
    
    def sort_by_trip_count(self, routes):
        """
        Sort routes by trip count in descending order (highest to lowest).
        
        This is the main public method for sorting route data. It uses
        QuickSort internally to efficiently order routes by popularity.
        
        Args:
            routes: List of dictionaries, each containing 'trip_count' key
                   Example: [{'route': 'A to B', 'trip_count': 150}, ...]
        
        Returns:
            Sorted list of routes (descending by trip_count)
            Returns new list, original is unchanged
        
        Algorithm Pseudo-code:
        1. Handle edge cases: empty array or single element
        2. Create a copy to avoid modifying original data
        3. Apply QuickSort with 'trip_count' as comparison key
        4. Return sorted copy
        
        Example:
            Input:  [{'trip_count': 100}, {'trip_count': 500}, {'trip_count': 200}]
            Output: [{'trip_count': 500}, {'trip_count': 200}, {'trip_count': 100}]
        """
        # Edge case: empty or single element array is already sorted
        if not routes or len(routes) <= 1:
            return routes
        
        # Create deep copy to preserve original data
        routes_copy = [route.copy() for route in routes]
        
        # Apply QuickSort algorithm
        self.quicksort(routes_copy, 0, len(routes_copy) - 1, 'trip_count')
        
        return routes_copy



# CLASS: OutlierDetector

# Implements statistical outlier detection using the IQR method
# (Interquartile Range). This method identifies data points that fall
# outside the typical range of values, useful for detecting anomalies
# like fraudulent transactions or data entry errors.


class OutlierDetector:
    """
    Custom outlier detection using IQR (Interquartile Range) method.
    
    IQR Method Overview:
    - Statistical technique for identifying outliers
    - Based on quartiles (Q1, Q2, Q3) of the data distribution
    - Outliers are values that fall outside 1.5 * IQR from Q1 or Q3
    - Robust to extreme values (unlike methods based on mean/std)
    
    Implementation Details:
    - No statistical libraries used (NumPy, SciPy)
    - Manual calculation of quartiles using bubble sort
    - Identifies anomalous fare amounts in trip data
    
    Performance Characteristics:
    - Time Complexity: O(n²) due to bubble sort
    - Space Complexity: O(n) for storing sorted values
    - Best for: Small to medium datasets where simplicity matters
    
    Note: For large datasets (>10,000 elements), consider optimized sorting
    """
    
    def calculate_median(self, sorted_arr):
        """
        Calculate median of a sorted array.
        
        The median is the middle value in a sorted dataset. If the dataset
        has an even number of elements, the median is the average of the
        two middle values.
        
        Args:
            sorted_arr: Array sorted in ascending order
            
        Returns:
            Median value (float)
            
        Algorithm:
        1. If array is empty, return 0
        2. Find middle index (n // 2)
        3. If odd number of elements: return middle element
        4. If even number of elements: return average of two middle elements
        """
        n = len(sorted_arr)
        if n == 0:
            return 0
        
        mid = n // 2  # Integer division for middle index
        
        # Even number of elements: average the two middle values
        if n % 2 == 0:
            return (sorted_arr[mid - 1] + sorted_arr[mid]) / 2
        # Odd number of elements: return the middle value
        else:
            return sorted_arr[mid]
    
    def bubble_sort(self, arr):
        """
        Manual bubble sort implementation for sorting numeric arrays.
        
        Bubble sort is a simple sorting algorithm that repeatedly steps
        through the list, compares adjacent elements, and swaps them if
        they are in the wrong order.
        
        Args:
            arr: Array of numeric values to sort
            
        Returns:
            New sorted array (ascending order)
            
        Algorithm:
        1. Create a copy of the array
        2. For each element in the array:
           a. Compare with next element
           b. If current > next, swap them
           c. Repeat until no more swaps needed
        3. After n passes, largest n elements are in correct position
        
        Time Complexity: O(n²) - not efficient for large datasets
        Space Complexity: O(n) for the copy
        
        Note: Used here for educational purposes and small datasets
        """
        sorted_arr = arr.copy()  # Create copy to avoid modifying original
        n = len(sorted_arr)
        
        # Outer loop: n passes through the array
        for i in range(n):
            # Inner loop: compare adjacent elements
            # After each pass, the largest element "bubbles up" to the end
            for j in range(0, n - i - 1):  # -i because last i elements are sorted
                # Swap if current element is greater than next
                if sorted_arr[j] > sorted_arr[j + 1]:
                    sorted_arr[j], sorted_arr[j + 1] = sorted_arr[j + 1], sorted_arr[j]
        
        return sorted_arr
    
    def calculate_quartiles(self, values):
        """
        Calculate Q1, Q2 (median), and Q3 manually without statistical libraries.
        
        Quartiles divide a sorted dataset into four equal parts:
        - Q1 (First Quartile): 25th percentile - median of lower half
        - Q2 (Second Quartile): 50th percentile - median of entire dataset
        - Q3 (Third Quartile): 75th percentile - median of upper half
        
        These values are essential for the IQR method of outlier detection.
        
        Args:
            values: List of numeric values (unsorted)
            
        Returns:
            Tuple (q1, q2, q3) representing the three quartiles
            
        Algorithm Pseudo-code:
        1. Sort the values using bubble sort
        2. Calculate Q2 (median of entire dataset)
        3. Split dataset into lower and upper halves
           - For odd-length data, exclude median from both halves
           - For even-length data, split evenly
        4. Calculate Q1 (median of lower half)
        5. Calculate Q3 (median of upper half)
        6. Return (Q1, Q2, Q3)
        
        Example:
            values = [1, 3, 5, 7, 9, 11, 13, 15]
            Q1 = median([1, 3, 5, 7]) = 4
            Q2 = median([1, 3, 5, 7, 9, 11, 13, 15]) = 8
            Q3 = median([9, 11, 13, 15]) = 12
        
        Time Complexity: O(n²) for bubble sort
        """
        # Handle empty array edge case
        if not values:
            return 0, 0, 0
        
        # Step 1: Sort values using bubble sort
        sorted_vals = self.bubble_sort(values)
        
        # Step 2: Calculate Q2 (median of entire dataset)
        q2 = self.calculate_median(sorted_vals)
        
        # Step 3: Split into lower and upper halves
        n = len(sorted_vals)
        mid = n // 2
        
        # For odd-length arrays, exclude the middle element from both halves
        lower_half = sorted_vals[:mid]
        upper_half = sorted_vals[mid + 1:] if n % 2 != 0 else sorted_vals[mid:]
        
        # Step 4 & 5: Calculate Q1 and Q3
        # Handle edge cases where halves might be empty
        q1 = self.calculate_median(lower_half) if lower_half else sorted_vals[0]
        q3 = self.calculate_median(upper_half) if upper_half else sorted_vals[-1]
        
        return q1, q2, q3
    
    def detect_fare_outliers(self, trips):
        """
        Detect outliers in fare amounts using the IQR (Interquartile Range) method.
        
        This method identifies trips with unusually high or low fare amounts,
        which could indicate:
        - Data entry errors
        - Fraudulent transactions
        - Special cases (e.g., long-distance trips, airport rides)
        - Pricing anomalies
        
        Args:
            trips: List of trip dictionaries with 'fare_amount' key
                  Example: [{'id': 1, 'fare_amount': 25.50, ...}, ...]
        
        Returns:
            List of outlier trips (trips with unusual fare amounts)
            Empty list if insufficient data or no outliers found
        
        Algorithm: IQR (Interquartile Range) Method
        
        Step-by-step process:
        1. Extract all fare amounts from trips
        2. Calculate Q1, Q2, Q3 using manual sorting
        3. Calculate IQR = Q3 - Q1 (spread of middle 50% of data)
        4. Define outlier bounds:
           - Lower bound = Q1 - 1.5 * IQR
           - Upper bound = Q3 + 1.5 * IQR
        5. Identify values outside these bounds as outliers
        
        Why 1.5 * IQR?
        - This is a standard threshold in statistics (Tukey's method)
        - Captures approximately 99.3% of normally distributed data
        - Values beyond this range are considered unusual
        
        Performance:
        - Time Complexity: O(n²) due to sorting in quartile calculation
        - Space Complexity: O(n) for storing fare amounts and outliers
        
        Note: Requires at least 4 data points to calculate quartiles
        """
        # Edge case: no trips to analyze
        if not trips:
            return []
        
        # Step 1: Extract fare amounts from all trips
        fare_amounts = []
        for trip in trips:
            # Validate that fare_amount exists and is not None
            if 'fare_amount' in trip and trip['fare_amount'] is not None:
                fare_amounts.append(float(trip['fare_amount']))
        
        # Need at least 4 values to calculate meaningful quartiles
        if len(fare_amounts) < 4:
            return []
        
        # Step 2: Calculate quartiles manually (no NumPy)
        q1, q2, q3 = self.calculate_quartiles(fare_amounts)
        
        # Step 3: Calculate IQR (Interquartile Range)
        # IQR represents the spread of the middle 50% of the data
        iqr = q3 - q1
        
        # Step 4: Define outlier bounds using 1.5 * IQR rule
        lower_bound = q1 - 1.5 * iqr  # Values below this are outliers
        upper_bound = q3 + 1.5 * iqr  # Values above this are outliers
        
        # Step 5: Identify trips with outlier fares
        outliers = []
        for trip in trips:
            if 'fare_amount' in trip and trip['fare_amount'] is not None:
                fare = float(trip['fare_amount'])
                # Check if fare is outside acceptable bounds
                if fare < lower_bound or fare > upper_bound:
                    outliers.append(trip)
        
        return outliers



# CLASS: TripAggregator

# Implements manual data aggregation without using pandas groupby or similar
# high-level functions. This demonstrates how to group and summarize data
# using basic data structures (dictionaries and loops).


class TripAggregator:
    """
    Custom aggregation algorithm for grouping trips by time periods.
    
    Purpose:
    Manual implementation of data aggregation without pandas groupby.
    Groups trip data by hour of day and calculates summary statistics
    (averages, counts) for each hour.
    
    Use Cases:
    - Hourly pattern analysis (rush hour identification)
    - Time-based trend visualization
    - Peak hour fare analysis
    - Traffic flow pattern recognition
    
    Performance Characteristics:
    - Time Complexity: O(n) where n is number of trips
    - Space Complexity: O(k) where k is number of unique groups (24 hours)
    - Efficient: Single pass through data with constant-time dictionary lookups
    
    Note: Much more efficient than O(n²) comparison-based approaches
    """
    
    def aggregate_by_hour(self, trips):
        """
        Aggregate trip data by pickup hour (0-23).
        
        This method groups all trips by their pickup hour and calculates
        summary statistics for each hour, providing insights into:
        - Peak travel times
        - Average fares throughout the day
        - Distance patterns by hour
        - Speed variations (traffic congestion indicators)
        
        Args:
            trips: List of trip dictionaries containing:
                  - 'pickup_hour': Hour of day (0-23)
                  - 'fare_amount': Trip fare
                  - 'trip_distance': Distance traveled
                  - 'duration_mins': Trip duration
                  - 'avg_speed_mph': Average speed
                  - 'tip_percentage': Tip percentage
        
        Returns:
            List of 24 dictionaries (one per hour) containing:
            - hour: Hour of day (0-23)
            - trip_count: Number of trips in that hour
            - avg_fare: Average fare amount
            - avg_distance: Average trip distance
            - avg_duration: Average trip duration
            - avg_speed: Average speed
            - avg_tip_pct: Average tip percentage
        
        Algorithm Pseudo-code:
        
        Phase 1 - Initialization (O(1)):
        1. Create dictionary with 24 keys (hours 0-23)
        2. Initialize counters and accumulators for each hour
        
        Phase 2 - Aggregation (O(n)):
        1. For each trip in trips:
           a. Extract pickup hour
           b. Validate hour is in range 0-23
           c. Increment trip counter for that hour
           d. Add fare amount to fare accumulator
           e. Add distance to distance accumulator
           f. Add duration, speed, tip to respective accumulators
        
        Phase 3 - Calculation (O(24) = O(1)):
        1. For each hour (0-23):
           a. If count > 0: calculate averages (total / count)
           b. If count = 0: set all metrics to 0
           c. Round results to 2 decimal places for readability
        
        Total Time Complexity: O(n) where n is number of trips
        Total Space Complexity: O(24) = O(1) constant space
        
        Example Output:
        [
            {'hour': 0, 'trip_count': 150, 'avg_fare': 15.25, ...},
            {'hour': 1, 'trip_count': 95, 'avg_fare': 18.50, ...},
            ...
            {'hour': 23, 'trip_count': 200, 'avg_fare': 22.75, ...}
        ]
        """
        # Phase 1: Initialize aggregation structure for all 24 hours
        hourly_data = {}
        for hour in range(24):
            hourly_data[hour] = {
                'hour': hour,
                'count': 0,              # Number of trips
                'total_fare': 0,         # Sum of all fares
                'total_distance': 0,     # Sum of all distances
                'total_duration': 0,     # Sum of all durations
                'total_speed': 0,        # Sum of all speeds
                'total_tip_pct': 0       # Sum of all tip percentages
            }
        
        # Phase 2: Aggregate trip data into hourly buckets
        for trip in trips:
            # Skip trips without pickup hour information
            if 'pickup_hour' not in trip or trip['pickup_hour'] is None:
                continue
            
            # Validate hour is in valid range (0-23)
            hour = int(trip['pickup_hour'])
            if hour < 0 or hour > 23:
                continue  # Skip invalid hours
            
            # Increment trip counter for this hour
            hourly_data[hour]['count'] += 1
            
            # Accumulate fare amount (with validation)
            if 'fare_amount' in trip and trip['fare_amount'] is not None:
                hourly_data[hour]['total_fare'] += float(trip['fare_amount'])
            
            # Accumulate trip distance (with validation)
            if 'trip_distance' in trip and trip['trip_distance'] is not None:
                hourly_data[hour]['total_distance'] += float(trip['trip_distance'])
            
            # Accumulate trip duration (with validation)
            if 'duration_mins' in trip and trip['duration_mins'] is not None:
                hourly_data[hour]['total_duration'] += float(trip['duration_mins'])
            
            # Accumulate average speed (with validation)
            if 'avg_speed_mph' in trip and trip['avg_speed_mph'] is not None:
                hourly_data[hour]['total_speed'] += float(trip['avg_speed_mph'])
            
            # Accumulate tip percentage (with validation)
            if 'tip_percentage' in trip and trip['tip_percentage'] is not None:
                hourly_data[hour]['total_tip_pct'] += float(trip['tip_percentage'])
        
        # Phase 3: Calculate averages for each hour
        result = []
        for hour in range(24):
            data = hourly_data[hour]
            count = data['count']
            
            # If there are trips in this hour, calculate averages
            if count > 0:
                result.append({
                    'hour': hour,
                    'trip_count': count,
                    'avg_fare': round(data['total_fare'] / count, 2),
                    'avg_distance': round(data['total_distance'] / count, 2),
                    'avg_duration': round(data['total_duration'] / count, 2),
                    'avg_speed': round(data['total_speed'] / count, 2),
                    'avg_tip_pct': round(data['total_tip_pct'] / count, 2)
                })
            # If no trips in this hour, return zeros
            else:
                result.append({
                    'hour': hour,
                    'trip_count': 0,
                    'avg_fare': 0,
                    'avg_distance': 0,
                    'avg_duration': 0,
                    'avg_speed': 0,
                    'avg_tip_pct': 0
                })
        
        return result



# CLASS: SpeedAnalyzer

# Analyzes speed patterns to identify traffic congestion hours
# Uses threshold-based analysis to find times of slowest travel


class SpeedAnalyzer:
    """
    Custom analyzer for identifying traffic congestion patterns.
    
    Purpose:
    Analyzes hourly speed data to identify congestion periods based on
    average speeds. Lower speeds typically indicate heavy traffic.
    
    Applications:
    - Traffic congestion identification
    - Route optimization recommendations
    - Peak hour traffic analysis
    - Urban planning insights
    
    Performance Characteristics:
    - Time Complexity: O(n) where n is number of hours analyzed
    - Space Complexity: O(1) constant space (excluding output)
    - Efficient: Two-pass algorithm (filter, then analyze)
    """
    
    def find_congestion_hours(self, hourly_data):
        """
        Identify hours with slowest average speeds (indicating congestion).
        
        Traffic congestion is typically characterized by slower average speeds.
        This method finds hours where speeds are significantly lower than usual,
        indicating heavy traffic conditions.
        
        Args:
            hourly_data: List of dictionaries containing:
                        - 'hour': Hour of day (0-23)
                        - 'avg_speed': Average speed in mph
                        - 'trip_count': Number of trips (for validation)
        
        Returns:
            List of hour numbers (0-23) identified as congestion hours
            Empty list if no congestion detected or insufficient data
        
        Algorithm Pseudo-code:
        
        1. Filter valid hours:
           - Only consider hours with trip_count > 10 (sufficient data)
           - This ensures statistical reliability
        
        2. Find minimum average speed:
           - Iterate through all valid hours
           - Track the lowest average speed value
        
        3. Define congestion threshold:
           - Set threshold = minimum speed * 1.1 (10% tolerance)
           - This captures hours within 10% of the slowest speed
        
        4. Identify congestion hours:
           - Any hour with avg_speed <= threshold is congestion
           - Return list of these hours
        
        Why 10% tolerance?
        - Accounts for minor variations in speed
        - Avoids flagging only the single slowest hour
        - Captures a cluster of slow-speed hours
        
        Time Complexity: O(n) where n is number of hours
        - First pass: O(n) to filter and find minimum
        - Second pass: O(n) to identify congestion hours
        - Total: O(2n) = O(n)
        
        Example:
            Input: [{'hour': 8, 'avg_speed': 12, 'trip_count': 500},
                   {'hour': 9, 'avg_speed': 11, 'trip_count': 600},  <- slowest
                   {'hour': 17, 'avg_speed': 12.5, 'trip_count': 550}]
            
            min_speed = 11
            threshold = 11 * 1.1 = 12.1
            congestion_hours = [8, 9]  (both <= 12.1)
        """
        # Edge case: no data to analyze
        if not hourly_data:
            return []
        
        # Step 1: Filter hours with sufficient data (trip_count > 10)
        # This ensures we have statistically reliable speed measurements
        valid_hours = [h for h in hourly_data if h.get('trip_count', 0) > 10]
        
        # If no valid hours, cannot identify congestion
        if not valid_hours:
            return []
        
        # Step 2: Find minimum average speed across all valid hours
        min_speed = float('inf')  # Initialize to infinity
        for hour_data in valid_hours:
            speed = hour_data.get('avg_speed', 0)
            if speed < min_speed:
                min_speed = speed
        
        # Step 3: Define congestion threshold (10% above minimum)
        # Hours with speeds within 10% of minimum are considered congested
        threshold = min_speed * 1.1
        
        # Step 4: Identify all hours meeting congestion criteria
        congestion_hours = []
        for hour_data in valid_hours:
            if hour_data.get('avg_speed', 0) <= threshold:
                congestion_hours.append(hour_data['hour'])
        
        return congestion_hours
