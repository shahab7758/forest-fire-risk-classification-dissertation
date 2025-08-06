# Forest Fire Risk Classification System

A comprehensive AI-powered system for detecting and predicting forest fire risks using camera images, satellite data, and meteorological information.

## Features

- 🔥 **Camera Detection**: Upload images to detect fire risks in real-time
- 🛰️ **Satellite Analysis**: Analyze satellite imagery for fire-prone areas
- 🌤️ **Weather Integration**: Combine meteorological data with image analysis
- 🚨 **Alert System**: Subscribe to location-based wildfire alerts

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your MAPBOX_TOKEN
   ```

3. **Run the application:**
   ```bash
   cd src
   python app.py
   ```

4. **Access the app:**
   Open http://localhost:5000 in your browser

### Docker Deployment

1. **Build and run with Docker:**
   ```bash
   ./deploy.sh
   ```

2. **Or manually:**
   ```bash
   docker build -t forest-fire-app .
   docker run -p 5000:5000 --env-file .env forest-fire-app
   ```

### Heroku Deployment

1. **Install Heroku CLI and login:**
   ```bash
   heroku login
   ```

2. **Create Heroku app:**
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set MAPBOX_TOKEN=your_token_here
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

## API Endpoints

- `GET /` - Home page
- `GET /detect/camera` - Camera detection interface
- `GET /detect/satellite` - Satellite detection interface
- `GET /alert` - Alert subscription interface
- `POST /camera_predict` - Process camera images
- `POST /satellite_predict` - Process satellite data
- `POST /alert` - Subscribe to alerts

## Environment Variables

- `MAPBOX_TOKEN` - Your Mapbox API token for satellite imagery
- `PORT` - Port number (default: 5000)

## Project Structure

```
├── src/
│   ├── app.py                 # Main Flask application
│   ├── camera_functions.py    # Camera detection logic
│   ├── satellite_functions.py # Satellite analysis logic
│   ├── meteorological_functions.py # Weather analysis
│   ├── email_alert.py        # Alert system
│   ├── templates/            # HTML templates
│   └── static/              # CSS, JS, images
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── wsgi.py                  # WSGI entry point
├── Procfile                 # Heroku deployment
└── deploy.sh               # Deployment script
```

## Technologies Used

- **Backend**: Flask, Python
- **AI/ML**: TensorFlow, Keras, Scikit-learn
- **Data**: OpenMeteo API, Mapbox API
- **Deployment**: Docker, Heroku, Gunicorn

## License

This project is licensed under the MIT License.




