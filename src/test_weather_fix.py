#!/usr/bin/env python3
"""
Test script to verify weather prediction fix
This script tests the weather prediction function with different locations
to ensure it no longer always returns 100%
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from meteorological_functions import weather_data_predict

def test_weather_predictions():
    """Test weather predictions for different locations"""
    
    # Test locations with different climates
    test_locations = [
        ("New York, NY", 40.7128, -74.0060),
        ("Los Angeles, CA", 34.0522, -118.2437),
        ("Miami, FL", 25.7617, -80.1918),
        ("Seattle, WA", 47.6062, -122.3321),
        ("Phoenix, AZ", 33.4484, -112.0740),
        ("Anchorage, AK", 61.2181, -149.9003),
    ]
    
    print("Testing Weather Predictions")
    print("=" * 50)
    
    for location_name, lat, lon in test_locations:
        try:
            prediction = weather_data_predict(lat, lon)
            percentage = round(prediction * 100, 1)
            
            print(f"{location_name:15} | Lat: {lat:7.2f} | Lon: {lon:8.2f} | Risk: {percentage:5.1f}%")
            
            # Check if prediction is reasonable
            if percentage == 100:
                print(f"  ⚠️  WARNING: Still getting 100% for {location_name}")
            elif percentage < 5:
                print(f"  ℹ️   Very low risk for {location_name}")
            elif percentage > 90:
                print(f"  ⚠️  Very high risk for {location_name}")
            else:
                print(f"  ✅ Reasonable risk level for {location_name}")
                
        except Exception as e:
            print(f"{location_name:15} | Error: {e}")
        
        print()
    
    print("=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_weather_predictions() 