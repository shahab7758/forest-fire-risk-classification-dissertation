import streamlit as st
import os
import sys
import requests
import json
from PIL import Image
import io

# Add current directory to path to import functions
sys.path.insert(0, os.path.dirname(__file__))

# Import the functions directly
from satellite_functions import satellite_cnn_predict
from camera_functions import camera_cnn_predict
from meteorological_functions import weather_data_predict

# Page configuration
st.set_page_config(
    page_title="Forest Fire Risk Classification",
    page_icon="🔥",
    layout="wide"
)

st.title("Forest Fire Risk Classification System")

# Function to get coordinates from postcode
def get_coordinates_from_postcode(postcode):
    try:
        # Using a free geocoding service
        url = f"https://nominatim.openstreetmap.org/search?postalcode={postcode}&country=US&format=json&limit=1"
        response = requests.get(url, headers={'User-Agent': 'ForestFireApp/1.0'})
        
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
            else:
                return None, None
        else:
            return None, None
    except Exception as e:
        st.error(f"Error getting coordinates from postcode: {str(e)}")
        return None, None

# Initialize database function
def init_db():
    try:
        import sqlite3
        conn = sqlite3.connect("alerts.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL
            )
        """
        )
        conn.commit()
        conn.close()
    except Exception as e:
        st.warning(f"Database initialization warning: {str(e)}")

# Initialize database
init_db()

# Display the app interface
st.markdown("""
## 🔥 Forest Fire Risk Classification

This system combines satellite imagery, camera feeds, and weather data to predict the risk of wildfires.

### Available Features:
- **Camera Detection**: Upload images for fire detection
- **Satellite Detection**: Analyze satellite imagery for fire risks  
- **Weather Analysis**: Get meteorological fire risk assessment
- **Alert System**: Subscribe to location-based wildfire alerts
""")

# Create tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["Home", "Camera Detection", "Satellite Detection", "Alert System"])

with tab1:
    st.markdown("""
    ### Welcome to Forest Fire Risk Classification System
    
    This system combines satellite imagery, camera feeds, and weather data to predict the risk of wildfires.
    
    **Features:**
    - 🔥 **Camera Detection**: Upload images to detect fire risks in real-time
    - 🛰️ **Satellite Detection**: Analyze satellite imagery for fire-prone areas
    - 🌤️ **Weather Analysis**: Combine meteorological data with image analysis
    - 🚨 **Alert System**: Subscribe to location-based wildfire alerts
    """)

with tab2:
    st.markdown("### 🔥 Camera Detection")
    
    uploaded_file = st.file_uploader("Upload an image for fire detection", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        if st.button("Analyze Image"):
            with st.spinner("Analyzing image..."):
                try:
                    # Convert PIL image to bytes for processing
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    
                    # Create a file-like object for the camera_cnn_predict function
                    class FileWrapper:
                        def __init__(self, bytes_io):
                            self.bytes_io = bytes_io
                        
                        def read(self):
                            return self.bytes_io.getvalue()
                        
                        def seek(self, pos):
                            self.bytes_io.seek(pos)
                    
                    file_wrapper = FileWrapper(img_bytes)
                    file_wrapper.filename = uploaded_file.name
                    
                    prediction = camera_cnn_predict(file_wrapper)
                    
                    # Fixed logic: Make confidence percentage more intuitive
                    # High prediction value (≥0.5) means NO FIRE
                    # Low prediction value (<0.5) means FIRE DETECTED
                    if prediction >= 0.5:
                        # NO FIRE detected
                        wildfire_prediction = 0  # 0 = No Fire
                        risk_level = "Low"
                        status = "Safe"
                        action = "No immediate action needed"
                        
                        # For NO FIRE: Show confidence as "Certainty of No Fire"
                        # Convert prediction to meaningful confidence (0.5-1.0 becomes 0-100%)
                        confidence = round(((prediction - 0.5) / 0.5) * 100)
                        confidence_text = f"Certainty of No Fire: {confidence}%"
                        
                    else:
                        # FIRE DETECTED
                        wildfire_prediction = 1  # 1 = Fire Detected
                        risk_level = "High"
                        status = "Fire Detected"
                        action = "Immediate attention required"
                        
                        # For FIRE: Show confidence as "Certainty of Fire Detection"
                        # Convert prediction to meaningful confidence (0-0.5 becomes 100-0%)
                        confidence = round(((0.5 - prediction) / 0.5) * 100)
                        confidence_text = f"Certainty of Fire Detection: {confidence}%"
                    
                    # Display results with corrected logic and clear confidence
                    if wildfire_prediction == 1:
                        st.error("🚨 Fire Detected!")
                        st.info(confidence_text)
                        st.warning(f"Risk Level: {risk_level} - {action}")
                        st.error(f"Status: {status}")
                    else:
                        st.success("✅ No Fire Detected")
                        st.info(confidence_text)
                        st.success(f"Risk Level: {risk_level} - {action}")
                        st.success(f"Status: {status}")
                        
                except Exception as e:
                    st.error(f"Error analyzing image: {str(e)}")

with tab3:
    st.markdown("### 🛰️ Satellite Detection")
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["Coordinates", "Postcode"],
        help="Select whether to enter coordinates directly or use a postcode"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Location Input")
        
        if input_method == "Coordinates":
            latitude = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=37.7749, step=0.0001, help="Enter latitude coordinate (-90 to 90)")
            longitude = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=-122.4194, step=0.0001, help="Enter longitude coordinate (-180 to 180)")
        else:
            postcode = st.text_input("Postcode", placeholder="94102", help="Enter US postcode (e.g., 94102 for San Francisco)")
            
            if postcode:
                if st.button("Get Coordinates from Postcode"):
                    with st.spinner("Looking up coordinates..."):
                        lat, lon = get_coordinates_from_postcode(postcode)
                        if lat is not None and lon is not None:
                            st.success(f"Found coordinates: {lat:.4f}, {lon:.4f}")
                            st.session_state.latitude = lat
                            st.session_state.longitude = lon
                        else:
                            st.error("Could not find coordinates for this postcode. Please try a different postcode.")
            
            # Display coordinates if available
            if 'latitude' in st.session_state and 'longitude' in st.session_state:
                latitude = st.session_state.latitude
                longitude = st.session_state.longitude
                st.info(f"Coordinates: {latitude:.4f}, {longitude:.4f}")
            else:
                latitude = 37.7749  # Default
                longitude = -122.4194  # Default
        
        zoom = st.slider("Zoom Level", min_value=10, max_value=20, value=15, help="Satellite image zoom level (10-20)")
    
    with col2:
        st.markdown("#### Instructions")
        if input_method == "Coordinates":
            st.markdown("""
            1. **Enter coordinates** for the area you want to analyze
            2. **Adjust zoom level** as needed (10-20)
            3. **Click Analyze** to get fire risk assessment
            4. **Results include** satellite and weather analysis
            """)
            
            # Example coordinates
            st.markdown("**Example Coordinates:**")
            st.code("San Francisco: 37.7749, -122.4194")
            st.code("Los Angeles: 34.0522, -118.2437")
            st.code("New York: 40.7128, -74.0060")
        else:
            st.markdown("""
            1. **Enter a US postcode** (e.g., 94102 for San Francisco)
            2. **Click "Get Coordinates"** to look up the location
            3. **Adjust zoom level** as needed (10-20)
            4. **Click Analyze** to get fire risk assessment
            """)
            
            # Example postcodes
            st.markdown("**Example Postcodes:**")
            st.code("San Francisco: 94102")
            st.code("Los Angeles: 90210")
            st.code("New York: 10001")
    
    if st.button("Analyze Location", type="primary"):
        with st.spinner("Analyzing satellite data..."):
            try:
                output_size = (350, 350)
                crop_amount = 35
                save_path = "satellite_image.png"
                
                # Use the same function as Flask app
                prediction_satellite = satellite_cnn_predict(
                    latitude,
                    longitude,
                    output_size=output_size,
                    zoom_level=zoom,
                    crop_amount=crop_amount,
                    save_path=save_path,
                )
                
                satellite_confidence = round(
                    (prediction_satellite if prediction_satellite > 0.5 else 1 - prediction_satellite) * 100
                )
                satellite_status = 1 if prediction_satellite > 0.5 else 0
                
                # Use the same weather function as Flask app
                prediction_weather = weather_data_predict(latitude, longitude)
                
                weather_confidence = round(
                    (prediction_weather if prediction_weather > 0.5 else 1 - prediction_weather) * 100
                )
                weather_status = 1 if prediction_weather > 0.5 else 0
                
                prediction_average = (prediction_satellite + prediction_weather) / 2
                average_confidence = round(
                    (prediction_average if prediction_average > 0.5 else 1 - prediction_average) * 100
                )
                average_status = 1 if prediction_average > 0.5 else 0
                
                # Display satellite image if available
                if os.path.exists(save_path):
                    satellite_img = Image.open(save_path)
                    st.image(satellite_img, caption="Satellite Image", use_column_width=True)
                
                # Display results in same style as Flask app
                st.markdown("### Analysis Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if satellite_status == 1:
                        st.error("🛰️ Satellite Analysis")
                        st.error(f"Risk: High Risk")
                    else:
                        st.success("🛰️ Satellite Analysis")
                        st.success(f"Risk: Low Risk")
                    st.info(f"Confidence: {satellite_confidence}%")
                
                with col2:
                    if weather_status == 1:
                        st.error("🌤️ Weather Analysis")
                        st.error(f"Risk: High Risk")
                    else:
                        st.success("🌤️ Weather Analysis")
                        st.success(f"Risk: Low Risk")
                    st.info(f"Confidence: {weather_confidence}%")
                
                with col3:
                    if average_status == 1:
                        st.error("📊 Combined Analysis")
                        st.error(f"Risk: High Risk")
                    else:
                        st.success("📊 Combined Analysis")
                        st.success(f"Risk: Low Risk")
                    st.info(f"Confidence: {average_confidence}%")
                
                # Summary
                st.markdown("---")
                if average_status == 1:
                    st.error("🚨 **HIGH FIRE RISK DETECTED**")
                    st.warning("This area shows elevated fire risk. Please take appropriate precautions.")
                else:
                    st.success("✅ **LOW FIRE RISK**")
                    st.info("This area shows low fire risk. Continue monitoring conditions.")
                    
            except Exception as e:
                st.error(f"Error analyzing location: {str(e)}")

with tab4:
    st.markdown("### 🚨 Alert System")
    
    st.markdown("""
    Subscribe to receive wildfire alerts for your location. We'll monitor the area and send you notifications when fire risks are detected.
    """)
    
    with st.form("alert_form"):
        email = st.text_input("Email Address", placeholder="your.email@example.com")
        
        col1, col2 = st.columns(2)
        with col1:
            alert_lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=37.7749, step=0.0001, key="alert_lat")
        with col2:
            alert_lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=-122.4194, step=0.0001, key="alert_lon")
        
        submitted = st.form_submit_button("Subscribe to Alerts")
        
        if submitted:
            if not email or alert_lat == 0 or alert_lon == 0:
                st.error("Please provide a valid email address and coordinates.")
            else:
                try:
                    # Use the same database logic as Flask app
                    import sqlite3
                    conn = sqlite3.connect("alerts.db")
                    cursor = conn.cursor()
                    
                    # Check if email already exists
                    cursor.execute("SELECT * FROM alerts WHERE email=?", (email,))
                    existing_alert = cursor.fetchone()
                    
                    if existing_alert:
                        st.error("This email is already subscribed to alerts.")
                    else:
                        # Insert the new email
                        cursor.execute(
                            "INSERT INTO alerts (email, latitude, longitude) VALUES (?, ?, ?)",
                            (email, alert_lat, alert_lon),
                        )
                        conn.commit()
                        conn.close()
                        
                        st.success(f"Successfully subscribed to alerts for {email} at coordinates ({alert_lat}, {alert_lon})")
                        st.info("You will receive alerts when fire risks are detected in your area.")
                        
                except Exception as e:
                    st.error(f"Error subscribing to alerts: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Forest Fire Risk Classification System | Powered by AI and Satellite Data</p>
</div>
""", unsafe_allow_html=True) 