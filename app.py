"""
app.py — Main Flask application for the Weather Web App
=========================================================
Fetches real-time weather data from OpenWeatherMap API and
renders it on a responsive Bootstrap-powered web page.

Author  : Weather App Project
Date    : 2026
Version : 1.0
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, session # type: ignore
import requests # type: ignore
from dotenv import load_dotenv # type: ignore

# Anchor .env to this script's directory so it works regardless
# of which folder the Flask server is launched from.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(_BASE_DIR, ".env"), override=True)

# ──────────────────────────────────────────────
# Flask app initialisation
# ──────────────────────────────────────────────
app = Flask(__name__)

# Secret key is required for Flask sessions (stores last searched city).
# Loaded from .env — set FLASK_SECRET_KEY to a strong random string in production.
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret_key")

# ──────────────────────────────────────────────
# OpenWeatherMap API configuration
# ──────────────────────────────────────────────
# API key is read from the environment on every startup.
# Set OPENWEATHER_API_KEY in your .env file.
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


# ──────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

def get_weather(city: str, units: str = "metric") -> dict:
    """
    Fetch weather data for a given city from the OpenWeatherMap API.

    Parameters
    ----------
    city  : str  — City name entered by the user
    units : str  — 'metric' (Celsius) or 'imperial' (Fahrenheit)

    Returns
    -------
    dict with keys:
        'success' (bool), 'data' (dict | None), 'error' (str | None)
    """
    params = {
        "q": city,
        "appid": os.getenv("OPENWEATHER_API_KEY", ""),
        "units": units,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)

        # 404 → city not found
        if response.status_code == 404:
            return {"success": False, "data": None, "error": f"City '{city}' not found. Please check the spelling and try again."}

        # 401 → bad API key
        if response.status_code == 401:
            return {"success": False, "data": None, "error": "Invalid API key. Please update your API key in app.py."}

        # Any other non-200 status
        if response.status_code != 200:
            return {"success": False, "data": None, "error": f"API error (status {response.status_code}). Please try again later."}

        raw = response.json()

        # ── Parse and structure the response ──
        unit_symbol = "°C" if units == "metric" else "°F"
        speed_unit  = "m/s" if units == "metric" else "mph"

        # Visibility is in metres → convert to km (metric) or miles (imperial)
        visibility_raw = raw.get("visibility", 0)
        if units == "metric":
            visibility = f"{round(visibility_raw / 1000, 1)} km"
        else:
            visibility = f"{round(visibility_raw / 1609.34, 1)} mi"

        icon = raw["weather"][0]["icon"]
        if icon in ["50d", "50n"]:
            icon = "03d"
        elif icon in ["04d", "04n"]:
            icon = icon.replace("04", "03")
        if icon == "01n":
            icon = "03n"
            
        data = {
            "city":           raw["name"],
            "country":        raw["sys"]["country"],
            "temperature":    round(raw["main"]["temp"]),
            "feels_like":     round(raw["main"]["feels_like"]),
            "humidity":       raw["main"]["humidity"],
            "pressure":       raw["main"]["pressure"],
            "condition":      raw["weather"][0]["main"],          # e.g. "Rain"
            "description":    raw["weather"][0]["description"].capitalize(),
            "wind_speed":     raw["wind"]["speed"],
            "visibility":     visibility,
            "icon":           icon,                               # replaced if 50d/50n
            "unit_symbol":    unit_symbol,
            "speed_unit":     speed_unit,
            "units":          units,
        }

        return {"success": True, "data": data, "error": None}

    except requests.exceptions.ConnectionError:
        return {"success": False, "data": None, "error": "Network error. Please check your internet connection."}
    except requests.exceptions.Timeout:
        return {"success": False, "data": None, "error": "Request timed out. The API server is taking too long to respond."}
    except requests.exceptions.RequestException as exc:
        return {"success": False, "data": None, "error": f"Unexpected error: {str(exc)}"}


def get_forecast(city: str, units: str = "metric") -> dict:
    """
    Fetch 5-day / 3-hour forecast data for a given city from OpenWeatherMap API
    and restructure it into intraday (next 12h) and daily (next 5 days) views.
    """
    params = {
        "q": city,
        "appid": os.getenv("OPENWEATHER_API_KEY", ""),
        "units": units,
    }

    try:
        response = requests.get(FORECAST_URL, params=params, timeout=10)
        if response.status_code != 200:
            return {"success": False, "data": None, "error": "Could not fetch forecast."}
        
        raw = response.json()
        list_data = raw.get("list", [])
        
        if not list_data:
            return {"success": False, "data": None, "error": "No forecast data."}

        # 1. Intraday (Next 4 blocks representing ~12 hours)
        # Using labels Night, Morning, Day, Evening purely illustratively 
        intraday = []
        labels = ["Night", "Morning", "Day", "Evening"]
        for i in range(min(4, len(list_data))):
            item = list_data[i]
            dt_txt = item["dt_txt"]
            time_str = dt_txt.split(" ")[1][:5] # e.g. "15:00"
            icon = item["weather"][0]["icon"]
            if icon in ["04d", "04n"]: icon = icon.replace("04", "03")
            if icon == "01n": icon = "03n"
            intraday.append({
                "label": labels[i] if i < 4 else "Later",
                "time": time_str,
                "temp": round(item["main"]["temp"]),
                "icon": icon
            })

        # 2. Daily grouping (5 days)
        from collections import defaultdict
        daily_groups = defaultdict(list)
        for item in list_data:
            # item["dt_txt"] format: "2026-03-21 15:00:00"
            date_str = item["dt_txt"].split(" ")[0]
            daily_groups[date_str].append(item)
        
        # Build 5-day summary
        daily_forecast = []
        for date_str, items in daily_groups.items():
            temps = [x["main"]["temp"] for x in items]
            min_temp = round(min(temps))
            max_temp = round(max(temps))
            
            # Use the condition of the middle-of-the-day item (approx index 4 in an 8-item day)
            mid_item = items[len(items)//2]
            condition_desc = mid_item["weather"][0]["description"].capitalize()
            icon = mid_item["weather"][0]["icon"]
            if icon in ["04d", "04n"]: icon = icon.replace("04", "03")
            if icon == "01n": icon = "03n"
            
            # Parse date for display
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            day_name = date_obj.strftime("%A").upper() # "FRIDAY"
            day_date = date_obj.strftime("%d %B")      # "24 July"
            
            daily_forecast.append({
                "day_name": day_name,
                "day_date": day_date,
                "min": min_temp,
                "max": max_temp,
                "desc": condition_desc,
                "icon": icon
            })
            
            # Limit to 6 days total (today + 5)
            if len(daily_forecast) >= 6:
                break

        data = {
            "intraday": intraday,
            "daily": daily_forecast
        }

        return {"success": True, "data": data, "error": None}

    except Exception as exc:
        return {"success": False, "data": None, "error": str(exc)}



def get_bg_class(condition: str) -> str:
    """
    Map a weather condition string to a CSS background class.

    Parameters
    ----------
    condition : str — The 'main' weather condition from OWM (e.g. 'Rain')

    Returns
    -------
    str — CSS class name defined in style.css
    """
    mapping = {
        "Clear":         "bg-clear",
        "Rain":          "bg-rain",
        "Drizzle":       "bg-rain",
        "Thunderstorm":  "bg-thunderstorm",
        "Clouds":        "bg-clouds",
        "Snow":          "bg-snow",
        "Mist":          "bg-mist",
        "Fog":           "bg-mist",
        "Haze":          "bg-mist",
        "Smoke":         "bg-mist",
        "Dust":          "bg-mist",
        "Sand":          "bg-mist",
        "Ash":           "bg-mist",
        "Squall":        "bg-thunderstorm",
        "Tornado":       "bg-thunderstorm",
    }
    return mapping.get(condition, "bg-default")


def get_current_datetime() -> str:
    """Return the current date and time formatted for display."""
    return datetime.now().strftime("%A, %d %B %Y  •  %I:%M %p")


# ──────────────────────────────────────────────
# Flask Routes
# ──────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    """
    Home page — renders the search form.
    Pre-fills the city field with the last searched city (from session) or default IP location.
    """
    last_city = session.get("last_city", "")
    units = request.args.get("units", "metric")
    
    # If no city searched yet, try to auto-detect based on IP
    if not last_city:
        try:
            res = requests.get("http://ip-api.com/json/", timeout=3)
            if res.status_code == 200:
                loc_data = res.json()
                if loc_data.get("status") == "success":
                    last_city = loc_data.get("city", "")
                    session["last_city"] = last_city
        except Exception:
            pass

    # If we have a city (either from session or IP), show its weather automatically
    if last_city:
        result = get_weather(last_city, units)
        forecast_result = get_forecast(last_city, units)
        
        if result["success"]:
            weather_data = result["data"]
            forecast_data = forecast_result["data"] if forecast_result["success"] else None
            bg_class = get_bg_class(weather_data["condition"])
            
            return render_template(
                "index.html",
                weather=weather_data,
                forecast=forecast_data,
                bg_class=bg_class,
                last_city=last_city,
                datetime=get_current_datetime(),
            )
            
    return render_template("index.html", last_city=last_city, datetime=get_current_datetime())


@app.route("/weather", methods=["POST"])
def weather():
    """
    Weather results route — called when the search form is submitted.
    Fetches weather data and passes it to the template.
    """
    city  = request.form.get("city", "").strip()
    units = request.form.get("units", "metric")   # 'metric' or 'imperial'

    # Basic input validation
    if not city:
        return render_template(
            "index.html",
            error="Please enter a city name.",
            last_city="",
            datetime=get_current_datetime(),
        )

    # Store the searched city in the session so we can pre-fill on next visit
    session["last_city"] = city

    # Fetch weather data
    result = get_weather(city, units)
    forecast_result = get_forecast(city, units)

    if result["success"]:
        weather_data = result["data"]
        forecast_data = forecast_result["data"] if forecast_result["success"] else None
        
        bg_class     = get_bg_class(weather_data["condition"])
        return render_template(
            "index.html",
            weather=weather_data,
            forecast=forecast_data,
            bg_class=bg_class,
            last_city=city,
            datetime=get_current_datetime(),
        )
    else:
        return render_template(
            "index.html",
            error=result["error"],
            last_city=city,
            datetime=get_current_datetime(),
        )


@app.route("/search_cities", methods=["GET"])
def search_cities():
    """Proxy route to fetch city autocomplete suggestions from OpenWeatherMap"""
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return {"cities": []}
    
    api_key = os.getenv("OPENWEATHER_API_KEY", "")
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={q}&limit=5&appid={api_key}"
    
    try:
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            data = res.json()
            cities = []
            for item in data:
                name = item.get("name", "")
                state = item.get("state", "")
                country = item.get("country", "")
                # Format: City, State, Country
                full_name = f"{name}, {state}, {country}" if state else f"{name}, {country}"
                if full_name not in cities:
                    cities.append(full_name)
            return {"cities": cities}
    except Exception:
        pass
    
    return {"cities": []}


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    # debug=True enables hot-reload during development.
    # Set debug=False and use a production WSGI server for deployment.
    app.run(debug=True)
