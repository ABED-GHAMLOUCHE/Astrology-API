from flask import Flask, request, jsonify, render_template, send_file
import matplotlib.pyplot as plt
import numpy as np
import swisseph as swe
import os
from io import BytesIO
from geopy.geocoders import Nominatim
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, bcrypt
from config import Config
import traceback  # Logs full error details

# ✅ Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

# ✅ Ensure SECRET_KEY for JWT is Set
if not app.config.get("JWT_SECRET_KEY"):
    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # Change this in production!

# ✅ Initialize Extensions
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# ✅ Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# ✅ Create Database Tables
with app.app_context():
    db.create_all()

# ===========================
# 🚀 USER AUTHENTICATION
# ===========================

# ✅ User Registration Route
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 409

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        print("🔥 ERROR:", e)
        traceback.print_exc()
        return jsonify({"error": "Something went wrong!"}), 500

# ✅ User Login Route
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid credentials"}), 401

        access_token = create_access_token(identity=str(user.id))  # Convert to string

        return jsonify({"message": "Login successful", "access_token": access_token}), 200

    except Exception as e:
        print("🔥 ERROR:", e)
        traceback.print_exc()
        return jsonify({"error": "Something went wrong!"}), 500

# ✅ Protected Profile Route
@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "username": user.username,
            "email": user.email,
            "message": "Welcome to your profile"
        }), 200

    except Exception as e:
        print("🔥 ERROR:", e)
        traceback.print_exc()
        return jsonify({"error": "Something went wrong!"}), 500

# ===========================
# 🔮 ASTROLOGY FUNCTIONS
# ===========================

# ✅ Set Ephemeris Path
EPHE_PATH = "C:/swisseph-master/sweph/"
swe.set_ephe_path(EPHE_PATH)

# ✅ Define Planets
PLANETS = {
    "☉ Sun": swe.SUN, "☽ Moon": swe.MOON, "☿ Mercury": swe.MERCURY,
    "♀ Venus": swe.VENUS, "♂ Mars": swe.MARS, "♃ Jupiter": swe.JUPITER,
    "♄ Saturn": swe.SATURN, "♅ Uranus": swe.URANUS, "♆ Neptune": swe.NEPTUNE,
    "♇ Pluto": swe.PLUTO, "☊ North Node": swe.MEAN_NODE
}

# ✅ Zodiac Signs
ZODIAC_SIGNS = [
    "♈ Aries", "♉ Taurus", "♊ Gemini", "♋ Cancer", "♌ Leo", "♍ Virgo",
    "♎ Libra", "♏ Scorpio", "♐ Sagittarius", "♑ Capricorn", "♒ Aquarius", "♓ Pisces"
]

# ✅ Major Aspects
ASPECTS = {
    "Conjunction": 0, "Opposition": 180, "Trine": 120,
    "Square": 90, "Sextile": 60
}
ORB_ALLOWANCE = {"Conjunction": 8, "Opposition": 6, "Trine": 6, "Square": 6, "Sextile": 4}

# ✅ Get Coordinates of a City
def get_coordinates(city):
    geolocator = Nominatim(user_agent="astro_chart")
    location = geolocator.geocode(city)
    return (location.latitude, location.longitude) if location else (None, None)

# ✅ Generate Birth Chart
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

# ✅ Astrology API Route
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
    return jsonify(chart)

# ✅ Homepage Route
@app.route("/")
def home():
    return render_template("index.html")

# ✅ Run Flask App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)