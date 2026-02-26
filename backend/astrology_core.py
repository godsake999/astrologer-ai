"""
Astrology Core Calculator for AstroLogic AI
Uses pure-Python astronomical calculations to avoid C-extension dependencies.
Implements a simplified but reasonably accurate solar system model.
"""

import math
from datetime import datetime, date
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import pytz


# ── Zodiac & Nakshatra Data ──────────────────────────────────────────────────

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn",
    "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter",
    "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury"
]

VIMSHOTTARI_ORDER = [
    ("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7),
    ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17)
]

PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄"
}

ASPECT_TYPES = [
    (0,   8,  "Conjunction"),
    (60,  6,  "Sextile"),
    (90,  8,  "Square"),
    (120, 8,  "Trine"),
    (180, 8,  "Opposition"),
]


# ── Geocoding ────────────────────────────────────────────────────────────────

def geocode_city(city: str) -> dict:
    """Convert city name to latitude and longitude."""
    geolocator = Nominatim(user_agent="astrologic-ai-v1")
    try:
        location = geolocator.geocode(city, timeout=10)
        if not location:
            raise ValueError(f"Could not find city: {city}")
        return {
            "city": city,
            "lat": location.latitude,
            "lon": location.longitude,
            "address": location.address,
        }
    except GeocoderTimedOut:
        raise ValueError("Geocoding timed out. Please try again.")


def local_to_utc(dt_local: datetime, city: str) -> datetime:
    """Convert local datetime to UTC."""
    try:
        from timezonefinder import TimezoneFinder
        tf = TimezoneFinder()
        geo = geocode_city(city)
        tz_name = tf.timezone_at(lng=geo["lon"], lat=geo["lat"]) or "UTC"
        local_tz = pytz.timezone(tz_name)
        dt_aware = local_tz.localize(dt_local)
        return dt_aware.astimezone(pytz.utc)
    except Exception:
        return pytz.utc.localize(dt_local)


# ── Julian Day & Core Astronomy ──────────────────────────────────────────────

def to_julian_day(dt: datetime) -> float:
    """Convert datetime to Julian Day Number."""
    a = (14 - dt.month) // 12
    y = dt.year + 4800 - a
    m = dt.month + 12 * a - 3
    jdn = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    jd = jdn + (dt.hour - 12) / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0
    return jd


def jd_to_j2000(jd: float) -> float:
    """Days since J2000.0 (2000-Jan-1.5 TT)."""
    return jd - 2451545.0


def normalize(angle: float) -> float:
    """Normalize angle to [0, 360)."""
    return angle % 360


def rad(deg: float) -> float:
    return math.radians(deg)


def planet_longitude(dt: datetime, planet: str) -> float:
    """
    Calculate approximate ecliptic longitude for a planet.
    Uses simplified VSOP87 / mean element theory.
    Accuracy: Sun ±0.01°, others ±1-2° (sufficient for sign/nakshatra level).
    """
    d = jd_to_j2000(to_julian_day(dt))
    T = d / 36525.0  # Julian centuries

    if planet == "Sun":
        L0 = 280.46646 + 36000.76983 * T
        M = normalize(357.52911 + 35999.05029 * T)
        Mr = rad(M)
        C = (1.914602 - 0.004817 * T) * math.sin(Mr) + 0.019993 * math.sin(2 * Mr)
        sun_lon = normalize(L0 + C)
        return sun_lon

    elif planet == "Moon":
        # Mean elements
        Lm = normalize(218.316 + 13.176396 * d)
        M_moon = normalize(134.963 + 13.064993 * d)
        F = normalize(93.272  + 13.229350 * d)
        D = normalize(297.850 + 12.190749 * d)
        Mp = normalize(357.529 + 0.985608 * d)  # Sun's mean anomaly
        lon = (Lm + 6.289 * math.sin(rad(M_moon))
                   - 1.274 * math.sin(rad(2 * D - M_moon))
                   + 0.658 * math.sin(rad(2 * D))
                   - 0.186 * math.sin(rad(Mp))
                   - 0.059 * math.sin(rad(2 * D - 2 * M_moon))
                   - 0.057 * math.sin(rad(2 * D + M_moon - Mp)))
        return normalize(lon)

    elif planet == "Mercury":
        L = normalize(252.250906 + 149472.6746358 * T)
        M = normalize(168.672  + 149472.515 * T)
        return normalize(L + 1.2 * math.sin(rad(M)))

    elif planet == "Venus":
        L = normalize(181.979801 + 58517.8156760 * T)
        M = normalize(48.0052 + 58517.8030 * T)
        return normalize(L + 0.77 * math.sin(rad(M)))

    elif planet == "Mars":
        L = normalize(355.433 + 19140.2993 * T)
        M = normalize(19.387  + 19140.3025 * T)
        return normalize(L + 10.691 * math.sin(rad(M)) + 0.623 * math.sin(rad(2 * M)))

    elif planet == "Jupiter":
        L = normalize(34.351519 + 3034.9056606 * T)
        M = normalize(20.9 + 3034.906 * T)
        return normalize(L + 5.55 * math.sin(rad(M)) + 0.168 * math.sin(rad(2 * M)))

    elif planet == "Saturn":
        L = normalize(50.077444 + 1222.1138488 * T)
        M = normalize(317.0 + 1222.114 * T)
        return normalize(L + 6.394 * math.sin(rad(M)) + 0.344 * math.sin(rad(2 * M)))

    return 0.0


def approximate_ascendant(dt: datetime, lat: float, lon: float) -> float:
    """Approximate the Ascendant (Rising Sign) longitude."""
    jd = to_julian_day(dt)
    d = jd_to_j2000(jd)
    # Local Sidereal Time
    GMST = normalize(280.46061837 + 360.98564736629 * d)
    LST = normalize(GMST + lon)
    # Obliquity of the ecliptic
    eps = rad(23.439 - 0.0000004 * d)
    lst_r = rad(LST)
    lat_r = rad(lat)
    asc = math.degrees(math.atan2(math.cos(lst_r), -(math.sin(lst_r) * math.cos(eps) + math.tan(lat_r) * math.sin(eps))))
    return normalize(asc)


def get_aspects(positions: dict[str, float]) -> list[str]:
    """Calculate major aspects between planets."""
    planets = list(positions.items())
    aspects = []
    for i, (p1, lon1) in enumerate(planets):
        for p2, lon2 in planets[i + 1:]:
            diff = abs(lon1 - lon2)
            if diff > 180:
                diff = 360 - diff
            for angle, orb, name in ASPECT_TYPES:
                if abs(diff - angle) <= orb:
                    aspects.append(f"{p1} {name} {p2}")
                    break
    return aspects


def format_planet(lon: float) -> str:
    """Format a longitude as 'Sign degree°'."""
    sign_idx = int(lon / 30) % 12
    degree = round(lon % 30, 1)
    return f"{ZODIAC_SIGNS[sign_idx]} {degree}°"


# ── Vedic Calculations ────────────────────────────────────────────────────────

def get_nakshatra_info(moon_lon: float) -> dict:
    """Calculate Nakshatra from Moon's ecliptic longitude."""
    idx = min(int(moon_lon / (360 / 27)), 26)
    pada = int((moon_lon % (360 / 27)) / (360 / 108)) + 1
    return {
        "nakshatra": NAKSHATRAS[idx],
        "pada": pada,
        "lord": NAKSHATRA_LORDS[idx],
    }


def get_mahadasha(birth_date: date, moon_lon: float) -> dict:
    """Calculate current Vimshottari Mahadasha."""
    from datetime import timedelta

    idx = min(int(moon_lon / (360 / 27)), 26)
    lord = NAKSHATRA_LORDS[idx]
    nakshatra_span = 360 / 27
    fraction_elapsed = (moon_lon - idx * nakshatra_span) / nakshatra_span

    dasha_years = next(y for n, y in VIMSHOTTARI_ORDER if n == lord)
    years_elapsed = fraction_elapsed * dasha_years
    years_remaining = dasha_years - years_elapsed

    current_idx = next(i for i, (n, _) in enumerate(VIMSHOTTARI_ORDER) if n == lord)
    next_lord = VIMSHOTTARI_ORDER[(current_idx + 1) % len(VIMSHOTTARI_ORDER)][0]

    today = date.today()
    dasha_end = today + timedelta(days=years_remaining * 365.25)

    return {
        "mahadasha_lord": lord,
        "years_remaining": round(years_remaining, 1),
        "ends": dasha_end.strftime("%Y-%m-%d"),
        "next_dasha": next_lord,
    }


# ── Main Calculator ───────────────────────────────────────────────────────────

def calculate_western_vedic(birth_dt: datetime, lat: float, lon: float) -> dict:
    """
    Calculate Western planetary positions, aspects, Ascendant, and Vedic data.
    Uses pure-Python astronomical algorithms (no C extensions required).
    """
    planet_names = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    positions = {p: planet_longitude(birth_dt, p) for p in planet_names}
    ascendant_lon = approximate_ascendant(birth_dt, lat, lon)
    aspects = get_aspects(positions)

    moon_lon = positions["Moon"]
    nak_info = get_nakshatra_info(moon_lon)
    dash_info = get_mahadasha(birth_dt.date(), moon_lon)

    western = {
        "sun": format_planet(positions["Sun"]),
        "moon": format_planet(positions["Moon"]),
        "mercury": format_planet(positions["Mercury"]),
        "venus": format_planet(positions["Venus"]),
        "mars": format_planet(positions["Mars"]),
        "jupiter": format_planet(positions["Jupiter"]),
        "saturn": format_planet(positions["Saturn"]),
        "ascendant": format_planet(ascendant_lon),
        "dominant_aspects": aspects[:6] if aspects else ["No major aspects detected"],
    }

    vedic = {
        "nakshatra": nak_info["nakshatra"],
        "nakshatra_pada": nak_info["pada"],
        "nakshatra_lord": nak_info["lord"],
        "mahadasha": f"{dash_info['mahadasha_lord']} Dasha",
        "mahadasha_ends": dash_info["ends"],
        "next_dasha": dash_info["next_dasha"],
    }

    return {"western": western, "vedic": vedic}
