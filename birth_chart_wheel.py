import matplotlib.pyplot as plt
import numpy as np
import swisseph as swe

# Zodiac Signs
ZODIAC_SIGNS = [
    "♈ Aries", "♉ Taurus", "♊ Gemini", "♋ Cancer", "♌ Leo", "♍ Virgo",
    "♎ Libra", "♏ Scorpio", "♐ Sagittarius", "♑ Capricorn", "♒ Aquarius", "♓ Pisces"
]

# House System (Whole Sign Houses)
def get_whole_sign_houses(ascendant_degree):
    ascendant_sign_index = int(ascendant_degree // 30)
    return [ZODIAC_SIGNS[(ascendant_sign_index + i) % 12] for i in range(12)]

# Function to draw a circular birth chart
def draw_birth_chart(planet_positions, ascendant_degree):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)

    # Draw Circle for the Wheel
    wheel = plt.Circle((0, 0), 1, color="black", fill=False, linewidth=2)
    ax.add_patch(wheel)

    # Draw Zodiac Signs (Dividing Circle into 12 Sections)
    for i, sign in enumerate(ZODIAC_SIGNS):
        angle = (i * 30 + 15)  # Midpoint of each sign
        radian = np.radians(angle)
        x, y = np.cos(radian) * 0.85, np.sin(radian) * 0.85
        ax.text(x, y, sign, fontsize=9, ha="center", va="center", color="black")

    # Draw Houses (Whole Sign System)
    houses = get_whole_sign_houses(ascendant_degree)
    for i, house in enumerate(houses):
        angle = (i * 30 + 15)
        radian = np.radians(angle)
        x, y = np.cos(radian) * 0.6, np.sin(radian) * 0.6
        ax.text(x, y, f"H{i+1}", fontsize=8, ha="center", va="center", color="blue")

    # Draw Ascendant
    asc_radian = np.radians(ascendant_degree)
    ax.plot([0, np.cos(asc_radian)], [0, np.sin(asc_radian)], color="red", linewidth=2)
    ax.text(np.cos(asc_radian), np.sin(asc_radian), "ASC", color="red", fontsize=10, ha="center")

    # Plot Planets
    for planet, degree in planet_positions.items():
        radian = np.radians(degree)
        x, y = np.cos(radian) * 0.75, np.sin(radian) * 0.75
        ax.scatter(x, y, color="black", s=30)  # Planet marker
        ax.text(x, y + 0.05, planet, fontsize=8, ha="center", va="center", color="black")

    # Show Chart
    plt.show()

# Test Data: Planet Positions (Degrees) & Ascendant
test_planet_positions = {
    "☉ Sun": 200, "☽ Moon": 120, "☿ Mercury": 150,
    "♀ Venus": 230, "♂ Mars": 90, "♃ Jupiter": 310,
    "♄ Saturn": 45, "♅ Uranus": 275, "♆ Neptune": 350,
    "♇ Pluto": 10, "☊ North Node": 180
}
test_ascendant = 90  # Cancer Rising

# Draw the Birth Chart Wheel
draw_birth_chart(test_planet_positions, test_ascendant)
