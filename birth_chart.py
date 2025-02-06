import swisseph as swe
import datetime
from geopy.geocoders import Nominatim

# Set Swiss Ephemeris Path (Adjust if needed)
swe.set_ephe_path("C:/swisseph-master/sweph/")  # Change this to match your setup

# List of planets to calculate
PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
    "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO, "North Node": swe.MEAN_NODE
}

# List of zodiac signs
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Function to format degrees into D° M'
def format_degrees(deg):
    d = int(deg)
    m = int((deg - d) * 60)
    return f"{d}°{m:02d}'"

# Function to determine zodiac sign based on longitude
def get_zodiac(degrees):
    sign_index = int(degrees // 30)
    return ZODIAC_SIGNS[sign_index]

# Function to calculate Whole Sign Houses
def get_whole_sign_houses(ascendant_degree):
    ascendant_sign_index = int(ascendant_degree // 30)
    return [ZODIAC_SIGNS[(ascendant_sign_index + i) % 12] for i in range(12)]

# Function to determine house placement (Whole Sign Houses)
def determine_house(planet_degree, houses):
    planet_sign = get_zodiac(planet_degree)
    return houses.index(planet_sign) + 1  # Houses are 1-based index

# Function to get latitude & longitude for a given city
def get_coordinates(city):
    geolocator = Nominatim(user_agent="astro_chart")
    location = geolocator.geocode(city)
    if location:
        return location.latitude, location.longitude
    else:
        print("❌ City not found! Defaulting to 0,0.")
        return 0.0, 0.0  # Default if city not found

# Function to generate a full birth chart
def get_birth_chart(year, month, day, hour, minute, city, tz_offset):
    # Get latitude & longitude from city
    lat, lon = get_coordinates(city)

    # Convert date to Julian Day
    jd = swe.julday(year, month, day, hour + minute / 60.0 - tz_offset)

    # Calculate Ascendant (for Whole Sign Houses)
    houses, asc_mc = swe.houses(jd, lat, lon, b'P')  # 'P' is Placidus (only for ASC & MC)
    ascendant_degree = asc_mc[0]
    ascendant_sign = get_zodiac(ascendant_degree)
    whole_sign_houses = get_whole_sign_houses(ascendant_degree)

    chart = {}
    for planet_name, planet_code in PLANETS.items():
        planet_data = swe.calc_ut(jd, planet_code)
        planet_longitude = planet_data[0][0]  # Extract longitude
        sign = get_zodiac(planet_longitude)
        house = determine_house(planet_longitude, whole_sign_houses)
        chart[planet_name] = {
            "position": format_degrees(planet_longitude),
            "sign": sign,
            "house": house
        }

    # Add Ascendant (1st House) and Midheaven (MC)
    chart["Ascendant"] = {
        "position": format_degrees(ascendant_degree),
        "sign": ascendant_sign,
        "house": 1
    }
    chart["Midheaven"] = {
        "position": format_degrees(asc_mc[1]),
        "sign": get_zodiac(asc_mc[1]),
        "house": 10
    }

    return chart, whole_sign_houses

# Ask for User Input
print("\n🌟 Enter Birth Details 🌟")
year = int(input("Enter Birth Year (YYYY): "))
month = int(input("Enter Birth Month (MM): "))
day = int(input("Enter Birth Day (DD): "))
hour = int(input("Enter Birth Hour (24h format): "))
minute = int(input("Enter Birth Minute: "))
city = input("Enter Birth City: ")
tz_offset = float(input("Enter Time Zone Offset (e.g., -5 for New York, 1 for Berlin): "))

# Generate Birth Chart
birth_chart, houses = get_birth_chart(year, month, day, hour, minute, city, tz_offset)

# Print Nicely Formatted Birth Chart
print("\n🌟 Birth Chart (Whole Sign Houses) 🌟")
print("=" * 55)
print(f"{'Planet':<12}{'Position':<10}{'Sign':<12}{'House'}")
print("=" * 55)
for planet, data in birth_chart.items():
    print(f"{planet:<12}{data['position']:<10}{data['sign']:<12}{data['house']}")
print("=" * 55)

# Print Whole Sign Houses
print("\n🏠 House System (Whole Signs) 🏠")
print("=" * 55)
for i, house_sign in enumerate(houses, start=1):
    print(f"House {i}: {house_sign}")
print("=" * 55)
