from flask import Flask, request, jsonify, render_template, send_file
import matplotlib.pyplot as plt
import numpy as np
import swisseph as swe
import os
from io import BytesIO
from geopy.geocoders import Nominatim
from flask_cors import CORS  # Import CORS

app = Flask(__name__)

# ✅ Enable CORS for the entire app
CORS(app, resources={r"/birth_chart": {"origins": "*"}})

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# Set Ephemeris Path
EPHE_PATH = "C:/swisseph-master/sweph/"
swe.set_ephe_path(EPHE_PATH)

# Planets and Additional Points
PLANETS = {
    "☉ Sun": swe.SUN, "☽ Moon": swe.MOON, "☿ Mercury": swe.MERCURY,
    "♀ Venus": swe.VENUS, "♂ Mars": swe.MARS, "♃ Jupiter": swe.JUPITER,
    "♄ Saturn": swe.SATURN, "♅ Uranus": swe.URANUS, "♆ Neptune": swe.NEPTUNE,
    "♇ Pluto": swe.PLUTO, "☊ North Node": swe.MEAN_NODE
}

# Zodiac Signs
ZODIAC_SIGNS = [
    "♈ Aries", "♉ Taurus", "♊ Gemini", "♋ Cancer", "♌ Leo", "♍ Virgo",
    "♎ Libra", "♏ Scorpio", "♐ Sagittarius", "♑ Capricorn", "♒ Aquarius", "♓ Pisces"
]

# Major Aspects & Orbs
ASPECTS = {
    "Conjunction": 0, "Opposition": 180, "Trine": 120,
    "Square": 90, "Sextile": 60
}
ORB_ALLOWANCE = {"Conjunction": 8, "Opposition": 6, "Trine": 6, "Square": 6, "Sextile": 4}

# Function to Get Coordinates of City
def get_coordinates(city):
    geolocator = Nominatim(user_agent="astro_chart")
    location = geolocator.geocode(city)
    return (location.latitude, location.longitude) if location else (None, None)

# Function to Get Birth Chart
def get_birth_chart(year, month, day, hour, minute, city, tz_offset):
    lat, lon = get_coordinates(city)
    if lat is None or lon is None:
        return {"error": "City not found"}

    jd = swe.julday(year, month, day, hour + minute / 60.0 - tz_offset)
    houses, asc_mc = swe.houses(jd, lat, lon, b'P')
    ascendant_degree = asc_mc[0]

    chart = {}
    for planet, planet_code in PLANETS.items():
        planet_data = swe.calc_ut(jd, planet_code)
        planet_longitude = planet_data[0][0]
        chart[planet] = {
            "position": planet_longitude,
            "sign": ZODIAC_SIGNS[int(planet_longitude // 30)],
            "house": int(planet_longitude // 30) + 1
        }

    chart["Ascendant"] = {"position": ascendant_degree, "sign": ZODIAC_SIGNS[int(ascendant_degree // 30)], "house": 1}
    chart["Midheaven"] = {"position": asc_mc[1], "sign": ZODIAC_SIGNS[int(asc_mc[1] // 30)], "house": 10}

    return chart

# Function to Calculate Aspects
def calculate_aspects(chart):
    aspects = []
    planet_list = list(chart.keys())

    for i in range(len(planet_list)):
        for j in range(i + 1, len(planet_list)):
            planet1, planet2 = planet_list[i], planet_list[j]
            pos1, pos2 = chart[planet1]["position"], chart[planet2]["position"]
            for aspect, angle in ASPECTS.items():
                diff = abs(pos1 - pos2)
                diff = min(diff, 360 - diff)
                if abs(diff - angle) <= ORB_ALLOWANCE[aspect]:
                    aspects.append({"aspect": aspect, "planet1": planet1, "planet2": planet2, "orb": round(abs(diff - angle), 2)})
    return aspects

# Function to Draw Birth Chart Wheel
def draw_birth_chart(chart, aspects):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

    wheel = plt.Circle((0, 0), 1, color="black", fill=False, linewidth=2)
    ax.add_patch(wheel)

    for i, sign in enumerate(ZODIAC_SIGNS):
        angle = (i * 30 + 15)
        radian = np.radians(angle)
        x, y = np.cos(radian) * 0.85, np.sin(radian) * 0.85
        ax.text(x, y, sign, fontsize=9, ha="center", va="center", color="black")

    for planet, data in chart.items():
        radian = np.radians(data["position"])
        x, y = np.cos(radian) * 0.75, np.sin(radian) * 0.75
        ax.scatter(x, y, color="black", s=30)
        ax.text(x, y + 0.05, planet, fontsize=8, ha="center", va="center", color="black")

    # Draw Aspects
    for aspect in aspects:
        p1, p2 = aspect["planet1"], aspect["planet2"]
        x1, y1 = np.cos(np.radians(chart[p1]["position"])) * 0.75, np.sin(np.radians(chart[p1]["position"])) * 0.75
        x2, y2 = np.cos(np.radians(chart[p2]["position"])) * 0.75, np.sin(np.radians(chart[p2]["position"])) * 0.75
        ax.plot([x1, x2], [y1, y2], color="red", linestyle="--", linewidth=0.5)

    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return buf

@app.route("/chart_image")
def chart_image():
    year = int(request.args.get("year"))
    month = int(request.args.get("month"))
    day = int(request.args.get("day"))
    hour = int(request.args.get("hour"))
    minute = int(request.args.get("minute"))
    city = request.args.get("city")
    tz_offset = float(request.args.get("tz_offset"))

    chart = get_birth_chart(year, month, day, hour, minute, city, tz_offset)
    aspects = calculate_aspects(chart)

    image = draw_birth_chart(chart, aspects)
    return send_file(image, mimetype="image/png")

@app.route("/birth_chart", methods=["GET"])
def birth_chart():
    year = int(request.args.get("year"))
    month = int(request.args.get("month"))
    day = int(request.args.get("day"))
    hour = int(request.args.get("hour"))
    minute = int(request.args.get("minute"))
    city = request.args.get("city")
    tz_offset = float(request.args.get("tz_offset"))

    chart = get_birth_chart(year, month, day, hour, minute, city, tz_offset)
    aspects = calculate_aspects(chart)

    return jsonify({
        "birth_chart": chart,
        "aspects": aspects
    })

# Route to Display Web Page
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)