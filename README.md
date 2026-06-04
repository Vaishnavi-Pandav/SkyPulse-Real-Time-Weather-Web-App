# 🌤️ SkyPulse — Real-Time Weather Web App

A **SkyPulse — Real-Time Weather Web App** that fetches live weather data from the [OpenWeatherMap API](https://openweathermap.org/api) and presents it in a stunning, glassmorphism-styled Bootstrap 5 UI.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔍 City Search | Search any city worldwide |
| 🌡️ Temperature | Celsius / Fahrenheit toggle |
| 💧 Humidity | Real-time humidity % |
| 💨 Wind Speed | In m/s or mph |
| 🌡️ Pressure | Atmospheric pressure (hPa) |
| 👁️ Visibility | In km or miles |
| 🖼️ Weather Icon | Official OWM icon per condition |
| 🎨 Dynamic Background | Background gradient changes with weather |
| 🕐 Search History | Last 8 cities stored in browser localStorage |
# SkyPulse — Real-Time Weather Web App (SYNOPTIC Edition)

An elegant, fully-featured, portfolio-ready Weather Web Application built with Python (Flask) and the OpenWeatherMap API, now upgraded to the breathtaking **SYNOPTIC layout**. The application provides real-time current weather details, interactive intraday (next 12 hours) temp blocks, and a robust 5-day comprehensive forecast — all elegantly overlaid on stunning cinematic landscape photography.

---

## Features

- **Cinematic Landscape UI**: Full-bleed background imagery (`sunset.jpeg`) paired with stunning dark-glass minimalistic overlays mimicking the premium SYNOPTIC style.
- **Current Data Integration**: Accurate location details, comprehensive conditions, humidity, pressure, visibility, and wind speeds.
- **Intraday Forecasting**: Detailed 3-hour blocks predicting weather conditions through the Night, Morning, Day, and Evening.
- **5-Day Extended Outlook**: Dynamic bottom-strip highlighting the week's min/max temperatures, date labels, and localized descriptive terminology.
- **Responsive Layout**: Utilizing fluid Flexbox and CSS Grid breakpoints to transition smoothly from desktop (horizontal) to mobile (vertical) layouts.
- **Robust Error Handling**: Graceful fallback UI states seamlessly handle nonexistent locations and API failures without crashing the experience.

---

## 🚀 Deployment Instructions

### 1. Prerequisites
- **Python 3.8+** installed on your system.
- An **OpenWeatherMap API Key** (Free Tier is fully compatible).

### 2. Clone / Download the project
```bash
git clone https://github.com/your-username/SkyPulse — Real-Time Weather Web App.git
cd SkyPulse — Real-Time Weather Web App
```

### 3. Create a virtual environment (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Add your API key
Open `app.py` and replace the placeholder on **line 25**:
```python
API_KEY = "YOUR_API_KEY"   # ← replace this
```

### 6. Run the app
```bash
python app.py
```

Then open your browser and navigate to **[http://127.0.0.1:5000](http://127.0.0.1:5000)** 🎉

---

## 🌐 API Reference

This app uses the **OpenWeatherMap Current Weather Data API**:

```
GET https://api.openweathermap.org/data/2.5/weather
    ?q={city}
    &appid={API_KEY}
    &units={metric|imperial}
```

- **Free tier** allows 60 calls/minute and 1 million calls/month.
- Sign up at [openweathermap.org](https://openweathermap.org/api) — API key activates within ~15 minutes.

---

## 🎨 Weather Backgrounds

The app automatically changes the page background gradient based on the current weather condition:

| Condition | Theme |
|---|---|
| ☀️ Clear | Warm amber-to-gold gradient |
| 🌧️ Rain / Drizzle | Deep blue-grey gradient |
| ⛈️ Thunderstorm | Dark purple-navy gradient |
| ☁️ Clouds | Silver-blue gradient |
| ❄️ Snow | Icy blue-white gradient |
| 🌫️ Mist / Fog / Haze | Warm grey gradient |

---

## 🛠️ Technologies Used

- **Python 3** — Backend language
- **Flask** — Web framework
- **Requests** — HTTP library for API calls
- **Jinja2** — HTML templating (built into Flask)
- **Bootstrap 5** — Responsive CSS framework
- **Bootstrap Icons** — Icon library
- **OpenWeatherMap API** — Weather data source
- **localStorage** — Browser-side search history

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

*Built with Vaishnavi Pandav*
