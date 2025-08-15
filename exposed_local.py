import requests
import tkinter as tk
from tkinter import messagebox, scrolledtext
import webbrowser

# API keys
IPSTACK_KEY = "ipstack api key"
OPENWEATHER_KEY = "openweather api key"

def safe_val(value):
    """Return 'N/A' if value is None, empty string, or whitespace."""
    return value.strip() if isinstance(value, str) and value.strip() else "N/A"

def open_map(url):
    """Open the Google Maps link in the browser."""
    if url != "N/A":
        webbrowser.open(url)

def get_info():
    try:
        # Step 1: Get public IP and location info
        ip_address = requests.get("https://api.ipify.org").text
        ipstack_url = f"http://api.ipstack.com/{ip_address}?access_key={IPSTACK_KEY}"
        location_data = requests.get(ipstack_url).json()

        # Clean & extract location info
        ip = safe_val(location_data.get("ip"))
        city = safe_val(location_data.get("city"))
        region = safe_val(location_data.get("region_name"))
        country = safe_val(location_data.get("country_name"))
        timezone = safe_val(location_data.get("time_zone", {}).get("id"))
        lat = safe_val(str(location_data.get("latitude")))
        lon = safe_val(str(location_data.get("longitude")))
        map_link = f"https://www.google.com/maps?q={lat},{lon}" if lat != "N/A" and lon != "N/A" else "N/A"

        # Step 2: Get ISP info
        isp_api_url = "http://ip-api.com/json/"
        isp_data = requests.get(isp_api_url).json()
        if isp_data.get("status") == "success":
            isp = safe_val(isp_data.get("isp"))
            org = safe_val(isp_data.get("org"))
            asn = safe_val(isp_data.get("as"))
            connection_type = "Mobile" if isp_data.get("mobile") else "Wired/Broadband"
        else:
            isp = org = asn = connection_type = "N/A"

        # Step 3: Get weather info
        if lat != "N/A" and lon != "N/A":
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=metric"
            weather_data = requests.get(weather_url).json()
            temp = f"{weather_data.get('main', {}).get('temp', 'N/A')} °C"
            description = safe_val(weather_data.get("weather", [{}])[0].get("description"))
            humidity = f"{weather_data.get('main', {}).get('humidity', 'N/A')}%"
            wind_speed = f"{weather_data.get('wind', {}).get('speed', 'N/A')} m/s"
        else:
            temp = description = humidity = wind_speed = "N/A"

        # Step 4: Prepare display sections
        visitor_info = f"""=== Visitor Information ===
IP Address: {ip}
City: {city}
Region: {region}
Country: {country}
Timezone: {timezone}
Map: {map_link}
"""

        network_info = f"""\n=== Network Details ===
ISP: {isp}
Organization: {org}
AS Number: {asn}
Connection Type: {connection_type}
"""

        weather_info = f"""\n=== Weather Conditions ===
Temperature: {temp}
Description: {description}
Humidity: {humidity}
Wind Speed: {wind_speed}
"""

        # Step 5: Display in Tkinter
        result_area.config(state="normal")
        result_area.delete(1.0, tk.END)
        result_area.insert(tk.END, visitor_info + network_info + weather_info)
        result_area.config(state="disabled")

        # Optional: click to open map
        map_btn.config(state="normal")
        map_btn.config(command=lambda: open_map(map_link))

    except Exception as e:
        messagebox.showerror("Error", str(e))


# Tkinter UI setup
root = tk.Tk()
root.title("EXPOSED")
root.geometry("650x550")
root.config(bg="#1e1e1e")

title_label = tk.Label(root, text="EXPOSED", font=("Arial", 22, "bold"), fg="white", bg="#1e1e1e")
title_label.pack(pady=15)

btn = tk.Button(root, text="Get Your Information", font=("Arial", 14, "bold"),
                bg="#00b894", fg="white", relief="flat", padx=20, pady=10,
                command=get_info)
btn.pack(pady=10)

map_btn = tk.Button(root, text="Network Geolocation", font=("Arial", 12, "bold"),
                    bg="#0984e3", fg="white", relief="flat", padx=15, pady=8,
                    state="disabled")
map_btn.pack(pady=5)

result_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier New", 11),
                                        bg="#2d2d2d", fg="#f5f5f5", height=22, width=75)
result_area.pack(padx=10, pady=15)
result_area.config(state="disabled")

root.mainloop()
