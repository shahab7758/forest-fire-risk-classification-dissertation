import os
import numpy as np
from PIL import Image
from io import BytesIO
from tensorflow.keras.models import load_model

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the model file relative to the script location
model_path = os.path.join(script_dir, "..", "analysis", "wildfire_detection_model.keras")

# Try to load the model, handle missing model gracefully
try:
    model = load_model(model_path)
    print("Camera model loaded successfully")
except Exception as e:
    print(f"Warning: Could not load camera model from {model_path}")
    print(f"Error: {e}")
    print("Camera detection will not be available. Please ensure the model file is present.")
    model = None


# Function to preprocess the image before prediction
def preprocess_image(img):
    img_resized = img.resize((224, 224))
    img_array = np.array(img_resized)
    img_array = img_array / 255.0

    return np.expand_dims(img_array, axis=0)



# Function to predict wildfire probability using camera image
def camera_cnn_predict(image_file):
    # Check if model is available
    if model is None:
        return {
            "error": "Camera model not available. Please ensure the model file is present.",
            "probability": None
        }
    
    image = Image.open(BytesIO(image_file.read())).convert("RGB")
    preprocessed_image = preprocess_image(image)
    prediction = model.predict(preprocessed_image)[0][0]

    return prediction
