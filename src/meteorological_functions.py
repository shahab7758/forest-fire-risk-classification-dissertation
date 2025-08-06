import os
import pandas as pd
import numpy as np
import openmeteo_requests
import requests_cache
from retry_requests import retry
from datetime import datetime
import joblib

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
analysis_dir = os.path.join(script_dir, "..", "analysis")

# Try to load the model - handle both Keras and sklearn models
try:
    model_path = os.path.join(analysis_dir, "meteorological-detection-classification.keras")
    model = __import__("tensorflow").keras.models.load_model(model_path)
except:
    try:
        model = joblib.load(model_path)
    except:
        print("Warning: Could not load weather model. Using fallback prediction.")
        model = None

try:
    scaler_path = os.path.join(analysis_dir, "std_scaler_weather.pkl")
    std_scaler = joblib.load(scaler_path)
except:
    print("Warning: Could not load weather scaler. Using fallback prediction.")
    std_scaler = None

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


# Function to fetch weather data from Open-Meteo API
def fetch_weather_data(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "rain",
            "wind_speed_10m",
        ],
        "timezone": "auto",
    }

    responses = openmeteo.weather_api(url, params=params)
    return responses[0]


# Function to extract weather data
def preprocess_weather_data(response):
    current = response.Current()
    temperature = current.Variables(0).Value()
    relative_humidity = current.Variables(1).Value()
    precipitation = current.Variables(2).Value()
    rain = current.Variables(3).Value()
    wind_speed = current.Variables(4).Value()

    return temperature, relative_humidity, precipitation, rain, wind_speed


# Fire Weather Index (FWI) calculation functions


# Calculation of Fine Fuel Moisture Code (FFMC)
def calculate_ffmc(T, RH, W, R, previous_ffmc):
    mo = 147.2 * (101.0 - previous_ffmc) / (59.5 + previous_ffmc)
    rf = 0.0

    if R > 0.5:
        rf = R - 0.5
        mo = mo + 42.5 * rf * (np.exp(-100.0 / (251.0 - mo))) * (
            1.0 - np.exp(-6.93 / rf)
        )

    Ed = (
        0.942 * (RH**0.679)
        + (11.0 * np.exp((RH - 100.0) / 10.0))
        + 0.18 * (21.1 - T) * (1.0 - 1.0 / np.exp(0.115 * RH))
    )
    Ew = (
        0.618 * (RH**0.753)
        + (10.0 * np.exp((RH - 100.0) / 10.0))
        + 0.18 * (21.1 - T) * (1.0 - 1.0 / np.exp(0.115 * RH))
    )

    if mo < Ed:
        k1 = 0.424 * (1.0 - (RH / 100.0) ** 1.7) + 0.0694 * (W**0.5) * (
            1.0 - (RH / 100.0) ** 8
        )
        kw = k1 * (0.581 * np.exp(0.0365 * T))
        m = Ed - (Ed - mo) * (1.0 - np.exp(-kw))
    else:
        k1 = 0.424 * (1.0 - ((100.0 - RH) / 100.0) ** 1.7) + 0.0694 * (W**0.5) * (
            1.0 - ((100.0 - RH) / 100.0) ** 8
        )
        kw = k1 * (0.581 * np.exp(0.0365 * T))
        m = Ew + (mo - Ew) * (1.0 - np.exp(-kw))

    ffmc = 59.5 * (250.0 - m) / (147.2 + m)
    return ffmc


# Calculation of Duff Moisture Code (DMC)
def calculate_dmc(T, RH, R, previous_dmc, month):
    rk = 1.894 * (T + 1.1) * (100 - RH) * (1e-6)

    if R > 1.5:
        re = 0.92 * R - 1.27
        mo = 20.0 + np.exp(5.6348 - (previous_dmc / 43.43))
        if previous_dmc <= 33:
            b = 100.0 / (0.5 + 0.3 * previous_dmc)
        elif previous_dmc <= 65:
            b = 14.0 - 1.3 * np.log(previous_dmc)
        else:
            b = 6.2 * np.log(previous_dmc) - 17.2
        mr = mo + 1000.0 * re / (48.77 + b * re)
        dmc = 43.43 * (5.6348 - np.log(mr - 20.0))
    else:
        dmc = previous_dmc + rk

    return dmc


# Calculation of Drought Code (DC)
def calculate_dc(T, R, previous_dc, month):
    if T < -2.8:
        T = -2.8

    Lf = [6.5, 8.0, 9.7, 12.0, 15.3, 18.2, 20.4, 19.1, 17.2, 13.9, 10.0, 7.0]
    Pf = Lf[month - 1]
    rw = 0.83 * R - 1.27

    if rw < 0:
        rw = 0

    smi = 800 * np.exp(-previous_dc / 400)

    if R > 2.8:
        smi = smi + 3.937 * rw / (previous_dc + 104.0)

    dc = 400 * np.log(800.0 / smi)
    dc = dc + Pf * (T + 2.8) * 0.036

    return dc


# Calculation of Initial Spread Index (ISI)
def calculate_isi(ffmc, W):
    mo = 147.2 * (101.0 - ffmc) / (59.5 + ffmc)
    ff = np.exp(0.05039 * W)
    isi = 0.208 * ff * (91.9 * np.exp(-0.1386 * mo)) * \
        (1.0 + mo**5.31 / 4.93e7)
    return isi


# Calculation of Build Up Index (BUI)
def calculate_bui(dmc, dc):
    if dmc <= 0.4 * dc:
        bui = 0.8 * dmc * dc / (dmc + 0.4 * dc)
    else:
        bui = dmc - (1.0 - 0.8 * dc / (dmc + 0.4 * dc))

    if bui < 0:
        bui = 0

    return bui


# Calculation of Fire Weather Index (FWI)
def calculate_fwi(isi, bui):
    if bui <= 80:
        fwi = isi * (0.1 * bui) / (0.1 + bui)
    else:
        fwi = isi * (0.2 + 0.9 * bui) / (0.1 + bui)

    return fwi


# Function to predict wildfire probability using weather data
def weather_data_predict(latitude, longitude):
    try:
        response = fetch_weather_data(latitude, longitude)
        temperature, relative_humidity, precipitation, rain, wind_speed = (
            preprocess_weather_data(response)
        )

        # Validate input data
        if temperature is None or relative_humidity is None or wind_speed is None:
            return 0.1  # Default low risk if data is missing

        # Use more realistic previous values based on current conditions
        # These should ideally come from historical data for the specific location
        if temperature > 30 and relative_humidity < 60:
            ffmc_prev = 80.0  # Higher FFMC for hot, dry conditions
            dmc_prev = 15.0   # Higher DMC for dry conditions
            dc_prev = 25.0    # Higher DC for dry conditions
        elif temperature < 20 or relative_humidity > 80:
            ffmc_prev = 60.0  # Lower FFMC for cool, humid conditions
            dmc_prev = 5.0    # Lower DMC for humid conditions
            dc_prev = 10.0    # Lower DC for humid conditions
        else:
            ffmc_prev = 70.0  # Moderate values
            dmc_prev = 8.0
            dc_prev = 15.0

        month = datetime.now().month

        # Calculate indices
        ffmc = calculate_ffmc(temperature, relative_humidity,
                              wind_speed, rain, ffmc_prev)
        dmc = calculate_dmc(temperature, relative_humidity, rain, dmc_prev, month)
        dc = calculate_dc(temperature, rain, dc_prev, month)
        isi = calculate_isi(ffmc, wind_speed)
        bui = calculate_bui(dmc, dc)
        fwi = calculate_fwi(isi, bui)

        # Create a dataset
        data = {
            "Temperature": [temperature],
            "RH": [relative_humidity],
            "Ws": [wind_speed],
            "Rain": [rain],
            "FFMC": [ffmc],
            "DMC": [dmc],
            "DC": [dc],
            "ISI": [isi],
            "BUI": [bui],
            "FWI": [fwi],
        }

        df = pd.DataFrame(data)
        
        # Check if model and scaler are available
        if model is None or std_scaler is None:
            # Fallback to FWI-based prediction only
            print("Using fallback FWI-based prediction")
            raw_prediction = 0.5  # Neutral prediction
        else:
            df = std_scaler.transform(df)
            # Get raw prediction
            raw_prediction = model.predict(df)[0][0]
        
        # Apply additional logic to prevent unrealistic 100% predictions
        # Based on FWI thresholds and weather conditions
        fwi_risk = 0.0
        
        if fwi < 5.2:
            fwi_risk = 0.1  # Very low
        elif fwi < 11.2:
            fwi_risk = 0.3  # Low
        elif fwi < 21.3:
            fwi_risk = 0.5  # Moderate
        elif fwi < 38.0:
            fwi_risk = 0.7  # High
        elif fwi < 50.0:
            fwi_risk = 0.85 # Very high
        else:
            fwi_risk = 0.95 # Extreme
        
        # Combine model prediction with FWI-based risk
        # Give more weight to FWI for more realistic results
        final_prediction = 0.3 * raw_prediction + 0.7 * fwi_risk
        
        # Ensure prediction is within reasonable bounds
        final_prediction = max(0.05, min(0.95, final_prediction))
        
        return final_prediction
        
    except Exception as e:
        print(f"Error in weather prediction: {e}")
        return 0.1  # Default low risk on error
