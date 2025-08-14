from flask import Flask, render_template, jsonify, request
import requests
import os
from dotenv import load_dotenv

# Load .env file in local development
load_dotenv()

app = Flask(__name__)

# Use environment variables for API keys
IPSTACK_KEY = os.getenv("IPSTACK_KEY")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")

# Ensure keys exist
if not IPSTACK_KEY or not OPENWEATHER_KEY:
    raise ValueError("API keys not found in environment variables. Please set IPSTACK_KEY and OPENWEATHER_KEY.")

def safe_val(value):
    return value.strip() if isinstance(value, str) and value.strip() else "N/A"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_info')
def get_info():
    try:
        # Get client IP (with proxy support)
        client_ip = request.remote_addr
        if request.headers.get('X-Forwarded-For'):
            client_ip = request.headers['X-Forwarded-For'].split(',')[0]

        # Get location info
        ipstack_url = f"http://api.ipstack.com/{client_ip}?access_key={IPSTACK_KEY}"
        location_data = requests.get(ipstack_url).json()
        
        ip_info = {
            "IP Address": safe_val(client_ip),
            "City": safe_val(location_data.get("city")),
            "Region": safe_val(location_data.get("region_name")),
            "Country": safe_val(location_data.get("country_name")),
            "Timezone": safe_val(location_data.get("time_zone", {}).get("id")),
            "Latitude": safe_val(str(location_data.get("latitude"))),
            "Longitude": safe_val(str(location_data.get("longitude")))
        }

        # Get ISP info
        isp_api_url = f"http://ip-api.com/json/{client_ip}"
        isp_data = requests.get(isp_api_url).json()
        isp_info = {
            "ISP": safe_val(isp_data.get("isp")),
            "Organization": safe_val(isp_data.get("org")),
            "AS Number": safe_val(isp_data.get("as")),
            "Connection Type": "Mobile" if isp_data.get("mobile") else "Wired/Broadband"
        } if isp_data.get("status") == "success" else {
            "ISP": "N/A",
            "Organization": "N/A",
            "AS Number": "N/A",
            "Connection Type": "N/A"
        }

        # Get weather info
        weather_info = {}
        lat = ip_info["Latitude"]
        lon = ip_info["Longitude"]
        
        if lat != "N/A" and lon != "N/A":
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=metric"
            weather_data = requests.get(weather_url).json()
            
            if weather_data.get("cod") == 200:
                weather_info = {
                    "Temperature": f"{weather_data.get('main', {}).get('temp', 'N/A')} °C",
                    "Description": safe_val(weather_data.get("weather", [{}])[0].get("description")),
                    "Humidity": f"{weather_data.get('main', {}).get('humidity', 'N/A')}%",
                    "Wind Speed": f"{weather_data.get('wind', {}).get('speed', 'N/A')} m/s"
                }
            else:
                weather_info = {"Error": "Weather data not available"}
        else:
            weather_info = {"Error": "Location data not available for weather"}

        return jsonify({
            "ip_info": ip_info,
            "isp_info": isp_info,
            "weather_info": weather_info
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
