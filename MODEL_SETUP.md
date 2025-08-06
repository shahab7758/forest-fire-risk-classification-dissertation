# Model Setup Instructions

## Overview
This project uses machine learning models for wildfire detection. Due to GitHub's file size limitations (100MB per file), the large model files are not included in the repository.

## Required Model Files

### 1. Satellite Detection Model
- **File**: `analysis/wildfire_satellite_detection_model.keras`
- **Size**: ~131MB
- **Purpose**: CNN model for satellite image wildfire detection

### 2. Camera Detection Model  
- **File**: `analysis/wildfire_detection_model.keras`
- **Size**: ~97MB
- **Purpose**: CNN model for camera image wildfire detection

### 3. Meteorological Model
- **File**: `analysis/meteorological-detection-classification.keras`
- **Size**: ~927KB
- **Purpose**: Weather-based wildfire prediction model

### 4. Weather Scaler
- **File**: `analysis/std_scaler_weather.pkl`
- **Size**: ~1.2KB
- **Purpose**: Standard scaler for weather data preprocessing

## How to Obtain Model Files

### Option 1: Download from Original Source
If you have access to the original model files, place them in the `analysis/` directory.

### Option 2: Train New Models
You can train new models using the Jupyter notebooks in the `analysis/` directory:
- `wildfire-satellite-detection.ipynb` - for satellite model
- `wildfire-camera-detection.ipynb` - for camera model
- `meteorological-detection-classification.ipynb` - for weather model

### Option 3: Use Alternative Storage
For large model files, consider:
- Google Drive
- AWS S3
- Azure Blob Storage
- Other cloud storage services

## Application Behavior

The application is designed to handle missing model files gracefully:

- **With Models**: Full functionality available
- **Without Models**: 
  - Satellite detection: Returns error message
  - Camera detection: Returns error message  
  - Weather detection: Uses fallback prediction

## File Structure
```
analysis/
├── wildfire_satellite_detection_model.keras  # (not in repo - too large)
├── wildfire_detection_model.keras            # (not in repo - too large)
├── meteorological-detection-classification.keras
├── std_scaler_weather.pkl
└── *.ipynb files
```

## Troubleshooting

If you see warnings about missing models:
1. Ensure model files are in the `analysis/` directory
2. Check file permissions
3. Verify file integrity
4. Restart the application after adding models

## Note
The meteorological model and scaler are included in the repository as they are small enough to meet GitHub's file size limits. 