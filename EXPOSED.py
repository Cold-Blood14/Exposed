import requests
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
# API keys
IPSTACK_KEY = "ipstack api key"
OPENWEATHER_KEY = "openweather api key"

def get_info():
    try:
        # Step 1: Get location info from IPStack
        ipstack_url = f"http://api.ipstack.com/check?access_key={IPSTACK_KEY}"
        location_data = requests.get(ipstack_url).json()

        if "error" in location_data:
            messagebox.showerror("Error", location_data["error"]["info"])
            return

        lat = location_data.get("latitude")
        lon = location_data.get("longitude")

        if lat is None or lon is None:
            messagebox.showerror("Error", "Latitude/Longitude not found from IPStack.")
            return

        # Step 2: Get ISP info from ip-api.com (no key needed)
        ip_api_url = "http://ip-api.com/json/"
        isp_data = requests.get(ip_api_url).json()

        if isp_data.get("status") != "success":
            isp_text = "ISP information not available."
        else:
            isp_text = (f"ISP: {isp_data.get('isp', 'N/A')}\n"
                        f"Organization: {isp_data.get('org', 'N/A')}\n"
                        f"AS: {isp_data.get('as', 'N/A')}")

        # Step 3: Get weather info from OpenWeather
        weather_url = (f"https://api.openweathermap.org/data/2.5/weather?"
                       f"lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_KEY}")
        weather_data = requests.get(weather_url).json()

        if "main" not in weather_data:
            messagebox.showerror("Error", weather_data.get("message", "Weather data unavailable"))
            return

        # Format IP & Location info
        ip_info_text = "=== IP & Location Details ===\n"
        for key, value in location_data.items():
            ip_info_text += f"{key}: {value}\n"

        # Add ISP info
        ip_info_text += "\n=== ISP Information ===\n" + isp_text + "\n"

        # Format Weather info
        weather_info_text = "\n=== Weather Details ===\n"
        weather_info_text += f"Temperature: {weather_data['main']['temp']}°C\n"
        weather_info_text += f"Description: {weather_data['weather'][0]['description']}\n"
        weather_info_text += f"Humidity: {weather_data['main']['humidity']}%\n"
        weather_info_text += f"Wind Speed: {weather_data['wind']['speed']} m/s\n"

        # Display all in text area
        result_area.config(state="normal")
        result_area.delete(1.0, tk.END)
        result_area.insert(tk.END, ip_info_text + weather_info_text)
        result_area.config(state="disabled")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# Tkinter UI setup
root = tk.Tk()
root.title("EXPOSED")
root.geometry("600x500")
root.config(bg="#1e1e1e")

title_label = tk.Label(root, text="EXPOSED", font=("Arial", 22, "bold"), fg="white", bg="#1e1e1e")
title_label.pack(pady=15)

btn = tk.Button(root, text="Get Your Information", font=("Arial", 14, "bold"),
                bg="#00b894", fg="white", relief="flat", padx=20, pady=10,
                command=get_info)
btn.pack(pady=10)

result_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier New", 11),
                                        bg="#2d2d2d", fg="#f5f5f5", height=20, width=70)
result_area.pack(padx=10, pady=15)
result_area.config(state="disabled")

root.mainloop()

