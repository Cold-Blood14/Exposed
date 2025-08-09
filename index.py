from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# API keys (should use environment variables in production)
IPSTACK_KEY = os.environ.get('IPSTACK_KEY', '124568be2ee69403abf8f04f6e61d84d')
OPENWEATHER_KEY = os.environ.get('OPENWEATHER_KEY', 'cb781abd221bd259dd0df9ae29e2e83c')

def get_client_ip():
    """Get client IP address considering proxy headers"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers['X-Forwarded-For'].split(',')[0]
    return request.remote_addr

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/get_info', methods=['GET'])
def get_info():
    """API endpoint to gather and return information"""
    try:
        client_ip = get_client_ip()
        
        # Get location from IPStack
        ipstack_url = f"http://api.ipstack.com/{client_ip}?access_key={IPSTACK_KEY}"
        location_data = requests.get(ipstack_url).json()

        if "error" in location_data:
            return jsonify({"error": location_data["error"]["info"]}), 400

        lat = location_data.get("latitude")
        lon = location_data.get("longitude")
        
        if lat is None or lon is None:
            return jsonify({"error": "Latitude/Longitude not found"}), 400

        # Get ISP information
        ip_api_url = f"http://ip-api.com/json/{client_ip}"
        isp_data = requests.get(ip_api_url).json()

        isp_info = {
            "isp": isp_data.get("isp", "N/A"),
            "org": isp_data.get("org", "N/A"),
            "as": isp_data.get("as", "N/A")
        } if isp_data.get("status") == "success" else {"error": "ISP info unavailable"}

        # Get weather information
        weather_url = (f"https://api.openweathermap.org/data/2.5/weather?"
                       f"lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_KEY}")
        weather_data = requests.get(weather_url).json()

        if "main" not in weather_data:
            return jsonify({"error": weather_data.get("message", "Weather unavailable")}), 400

        weather_info = {
            "temp": weather_data['main']['temp'],
            "description": weather_data['weather'][0]['description'],
            "humidity": weather_data['main']['humidity'],
            "wind_speed": weather_data['wind']['speed']
        }

        # Prepare final response
        return jsonify({
            "ip_info": location_data,
            "isp_info": isp_info,
            "weather_info": weather_info
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)