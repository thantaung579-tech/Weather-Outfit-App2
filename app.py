from flask import Flask, render_template, request, jsonify
import requests
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
# =========================================================
# CONFIG
# =========================================================
OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
GEO_API_KEY = os.getenv("GEO_API_KEY")
GEO_HOST = os.getenv("GEO_HOST")

# =========================================
# DATABASE
# =========================================
conn = sqlite3.connect("weather.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS weather_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT,
    temperature REAL,
    condition TEXT,
    created_at TEXT
)
""")
conn.commit()

# =========================================
# SAVE DATA
# =========================================
def save(city, temp, cond):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO weather_logs (city, temperature, condition, created_at)
        VALUES (?, ?, ?, ?)
    """, (city, temp, cond, now))

    conn.commit()

# =========================================
# OUTFIT + IMAGE AI
# =========================================
def outfit_recommendation(temp, condition):
    outfit = {
        "clothes": "",
        "shoes": "",
        "accessories": "",
        "image": ""
    }

    # 🌞 HOT
    if temp >= 30:
        outfit["clothes"] = "Light t-shirt, shorts"
        outfit["shoes"] = "Sandals or sneakers"
        outfit["accessories"] = "Sunglasses, cap"
        outfit["image"] = "https://images.unsplash.com/photo-1520975916090-3105956dac38"

    # 🌤 WARM
    elif temp >= 20:
        outfit["clothes"] = "T-shirt, jeans"
        outfit["shoes"] = "Sneakers"
        outfit["accessories"] = "Watch, cap"
        outfit["image"] = "https://images.unsplash.com/photo-1520975958225-7c2c1b0c7c7a"

    # 🌥 COOL
    elif temp >= 10:
        outfit["clothes"] = "Jacket, jeans"
        outfit["shoes"] = "Closed shoes"
        outfit["accessories"] = "Light jacket"
        outfit["image"] = "https://images.unsplash.com/photo-1520975867597-0f2d1b3d8c3f"

    # ❄ COLD
    else:
        outfit["clothes"] = "Heavy jacket"
        outfit["shoes"] = "Boots"
        outfit["accessories"] = "Scarf, gloves"
        outfit["image"] = "https://images.unsplash.com/photo-1517841905240-472988babdf9"

    # 🌧 EXTRA WEATHER CONDITIONS
    if "Rain" in condition:
        outfit["accessories"] += ", umbrella"
        outfit["image"] = "https://images.unsplash.com/photo-1501999635878-71cb5379c1d5"

    if "Snow" in condition:
        outfit["accessories"] += ", waterproof gloves"
        outfit["image"] = "https://images.unsplash.com/photo-1489515217757-5fd1be406fef"

    return outfit

# =========================================
# HOME PAGE
# =========================================
@app.route("/")
def home():
    return render_template("index.html")

# =========================================
# AUTOCOMPLETE CITY API
# =========================================
@app.route("/cities")
def cities():
    q = request.args.get("q")

    url = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities"

    headers = {
        "x-rapidapi-key": GEO_API_KEY,
        "x-rapidapi-host": GEO_HOST
    }

    params = {
        "namePrefix": q,
        "limit": 5,
        "sort": "-population"
    }

    res = requests.get(url, headers=headers, params=params)

    if res.status_code == 200:
        data = res.json()
        return jsonify([item["city"] for item in data["data"]])

    return jsonify([])

# =========================================
# WEATHER API
# =========================================
@app.route("/weather")
def weather():
    city = request.args.get("city")

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHER_KEY,
        "units": "metric"
    }

    res = requests.get(url, params=params)

    if res.status_code != 200:
        return jsonify({"error": "City not found"})

    data = res.json()

    temp = data["main"]["temp"]
    cond = data["weather"][0]["main"]

    save(city, temp, cond)

    outfit = outfit_recommendation(temp, cond)

    return jsonify({
        "city": city,
        "temp": temp,
        "condition": cond,
        "outfit": outfit
    })

# =========================================
# RUN APP
# =========================================
if __name__ == "__main__":
    app.run(debug=True)