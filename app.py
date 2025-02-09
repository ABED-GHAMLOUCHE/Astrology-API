import os
import traceback
from flask import Flask, redirect, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import swisseph as swe
from geopy.geocoders import Nominatim
from config import Config

# ✅ Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

# ✅ Database Setup
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ✅ Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# ✅ Define User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(50), unique=True, nullable=True)  # For Google Login
    username = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)

# ✅ Google OAuth Setup
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = "https://astrology-api-au16.onrender.com/auth/google/callback"  # ✅ Correct Redirect URI

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    raise ValueError("Missing Google OAuth Client ID or Secret. Set them as environment variables.")

google_bp = make_google_blueprint(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    scope=["openid", "email", "profile"],
    redirect_url=GOOGLE_REDIRECT_URI  # ✅ FIXED
)
app.register_blueprint(google_bp, url_prefix="/auth")

# ✅ JWT Setup
jwt = JWTManager(app)

# ===========================
# 🚀 AUTHENTICATION SYSTEM
# ===========================

@app.route("/auth/google/callback")
def google_callback():
    if not google.authorized:
        return redirect(url_for("google.login"))

    try:
        # ✅ Fetch user info from Google API
        resp = google.get("https://www.googleapis.com/oauth2/v2/userinfo")  # ✅ FIXED
        if not resp.ok:
            return jsonify({"error": "Failed to fetch user info"}), 400

        user_info = resp.json()
        google_id = user_info["id"]
        email = user_info["email"]
        name = user_info.get("name", "")

        # ✅ Check if user exists in DB
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            user = User(google_id=google_id, email=email, username=name)
            db.session.add(user)
            db.session.commit()

        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "Login successful!",
            "username": user.username,
            "email": user.email,
            "access_token": access_token
        }), 200

    except Exception as e:
        print("🔥 ERROR:", e)
        traceback.print_exc()
        return jsonify({"error": "Something went wrong!"}), 500

# ✅ User Profile Route (Protected)
@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    try:
        user_id = int(get_jwt_identity())  # Convert from string to integer
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

ZODIAC_SIGNS = [
    "♈ Aries", "♉ Taurus", "♊ Gemini", "♋ Cancer", "♌ Leo",
    "♍ Virgo", "♎ Libra", "♏ Scorpio", "♐ Sagittarius", "♑ Capricorn",
    "♒ Aquarius", "♓ Pisces"
]

# ✅ Get Coordinates of a City
def get_coordinates(city):
    geolocator = Nominatim(user_agent="astrology_api")
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
        house_position = next((i+1 for i, cusp in enumerate(houses) if cusp > planet_longitude), 12)
        chart[planet] = {
            "position": planet_longitude,
            "sign": ZODIAC_SIGNS[int(planet_longitude // 30)],
            "house": house_position
        }

    chart["Ascendant"] = {
        "position": ascendant_degree,
        "sign": ZODIAC_SIGNS[int(ascendant_degree // 30)],  # ✅ FIXED
        "house": 1
    }
    chart["Midheaven"] = {
        "position": asc_mc[1],
        "sign": ZODIAC_SIGNS[int(asc_mc[1] // 30)],  # ✅ FIXED
        "house": 10
    }

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
    return "Welcome to the Astrology API! Go to /auth/google to log in."

# ✅ Run Flask App
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)