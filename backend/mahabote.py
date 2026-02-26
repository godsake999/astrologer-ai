"""
Burmese Mahabote (မဟာဘုတ်) Calculator
Correct algorithm using Kyin (ကြင်း) calculation:
  1. Calculate BE year (accounting for Burmese New Year in mid-April)
  2. Kyin = BE_year mod 7
  3. House = (day_value - Kyin) mod 7
"""

from datetime import date

# Burmese New Year (Thingyan) is typically around April 13-16.
# If born before mid-April, the Burmese year hasn't changed yet.
THINGYAN_MONTH = 4
THINGYAN_DAY = 14   # approximate

# The 7 Mahabote houses indexed 0-6
MAHABOTE_HOUSES = {
    0: {"name": "Binga (ဘင်္ဂ)",    "burmese": "ဘင်္ဂ",   "planet": "Saturn",  "natural_day": "Saturday"},
    1: {"name": "Yaza (ရာဇ)",        "burmese": "ရာဇ",      "planet": "Sun",     "natural_day": "Sunday"},
    2: {"name": "Athit (ဓာတ်)",      "burmese": "ဓာတ်",     "planet": "Moon",    "natural_day": "Monday"},
    3: {"name": "Mahat (မဟာ)",        "burmese": "မဟာ",      "planet": "Mars",    "natural_day": "Tuesday"},
    4: {"name": "Atwan (အာတ်ဝမ်)",   "burmese": "အာတ်ဝမ်", "planet": "Mercury", "natural_day": "Wednesday"},
    5: {"name": "Thinga (သင်္ဃ)",    "burmese": "သင်္ဃ",   "planet": "Jupiter", "natural_day": "Thursday"},
    6: {"name": "Yat (ရာဟု)",         "burmese": "ရာဟု",     "planet": "Venus",   "natural_day": "Friday"},
}

# Day of birth value used in Mahabote (Sat=0, Sun=1, Mon=2, ..., Fri=6)
# Python weekday(): Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
PYTHON_WEEKDAY_TO_MAHABOTE_VALUE = {
    5: 0,  # Saturday  → 0
    6: 1,  # Sunday    → 1
    0: 2,  # Monday    → 2
    1: 3,  # Tuesday   → 3
    2: 4,  # Wednesday → 4
    3: 5,  # Thursday  → 5
    4: 6,  # Friday    → 6
}

# English day names
DAY_NAMES = {
    0: "Monday", 1: "Tuesday", 2: "Wednesday",
    3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"
}

DAY_TO_BURMESE = {
    "Sunday":    "တနင်္ဂနွေ",
    "Monday":    "တနင်္လာ",
    "Tuesday":   "အင်္ဂါ",
    "Wednesday": "ဗုဒ္ဓဟူး",
    "Thursday":  "ကြာသပတေး",
    "Friday":    "သောကြာ",
    "Saturday":  "စနေ",
}

NAKSHATRA_BURMESE_BY_DAY = {
    "Sunday":    "ကြောင်း (Kyaung)",
    "Monday":    "ကြတ်ဖတ် (Kyat Phat)",
    "Tuesday":   "နတ်တော် (Nat Taw)",
    "Wednesday": "သနာ် (Tha Nar)",
    "Thursday":  "ကြာ (Kyar)",
    "Friday":    "သမာ (Tha Ma)",
    "Saturday":  "ဆာဘာ (Sa Ba)",
}

HOUSE_CHARACTERISTICS = {
    "Binga (ဘင်္ဂ)":       "စိတ်ရှည်သည်းခံ၍ ပြင်းထန်သောကံတရားနှင့် တရားမျှတမှုတို့နှင့် ဆက်နွှယ်သည်။ အဆုံးတွင် အောင်မြင်မည့်သူ။ (Disciplined, patient; associated with karma and justice. Ultimately victorious.)",
    "Yaza (ရာဇ)":           "ခေါင်းဆောင်မှု၊ အာဏာ၊ မင်းသားဂုဏ်ရည်ရှိသော သဘာဝ။ မွေးဖွားလာသောနေ့မှ ခေါင်းဆောင်ဖြစ်ရန် ကြိုးသားသူ။ (Leadership, authority, noble nature. Born to lead and inspire.)",
    "Athit (ဓာတ်)":         "ဉာဏ်တုံ၊ ကရုဏာ၊ ခံစားချက်ကြွယ်ဝသော ဝိညာဉ်ဖြစ်သည်။ ဖန်တီးမှု၊ ပြုစုစောင့်ရှောက်မှုနှင့် ကြွယ်ဝ။ (Intuitive, compassionate, emotionally intelligent, creative and nurturing.)",
    "Mahat (မဟာ)":          "ရဲစွမ်းသတ္တိ၊ ဇောင်ချောင်ချောင်၊ ခိုင်မာသောဇွဲနှင့် ပြင်းပြသောစိတ်ဓာတ်ရှိသည်။ (Courageous, energetic, determined, passionate but can be impulsive.)",
    "Atwan (အာတ်ဝမ်)":     "ဉာဏ်ပညာ၊ ဆက်ဆံရေးကောင်းမွန်မှု၊ ကုန်သည်ပညာနှင့် ညှိနိှုင်းဆွေးနွေးမှုတွင် ကျွမ်းကျင်သည်။ (Intellectual, communicative, skilled in trade and negotiation.)",
    "Thinga (သင်္ဃ)":      "ပညာဗဟုသုတ၊ ကြင်နာမှု၊ ကောင်းစားချမ်းသာမှုနှင့် ကံကောင်းမှုများ ကြုံတွေ့မည်။ (Wisdom, generosity, spiritual inclination, good fortune and prosperity.)",
    "Yat (ရာဟု)":           "အနုပညာ၊ အဆွေမိတ်ကောင်းစိတ်၊ လူမှုဆက်ဆံရေးကောင်းမွန်ပြီး သံတမန်တတ်သော ပုဂ္ဂိုလ်။ (Artistic, charming, strong social bonds and diplomacy.)",
}


def calculate_burmese_era(birth_date: date) -> int:
    """
    Calculate the correct Burmese Era (BE) year.
    The Burmese New Year (Thingyan) falls around April 13-16.
    Births before mid-April belong to the previous Burmese year.
    """
    gregorian_year = birth_date.year
    # Before Thingyan: BE year = Gregorian - 639
    # After Thingyan:  BE year = Gregorian - 638
    if birth_date.month < THINGYAN_MONTH or (
        birth_date.month == THINGYAN_MONTH and birth_date.day < THINGYAN_DAY
    ):
        return gregorian_year - 639
    else:
        return gregorian_year - 638


def calculate_kyin(be_year: int) -> int:
    """Calculate Kyin (ကြင်း) — the remainder of BE year divided by 7."""
    return be_year % 7


def calculate_mahabote(birth_date: date) -> dict:
    """
    Calculate the full Mahabote profile for a given birth date.

    Algorithm:
      1. BE year (adjusted for Thingyan)
      2. Kyin = BE_year mod 7
      3. Day value (Sat=0, Sun=1, ..., Fri=6)
      4. House index = (day_value - Kyin) mod 7
    """
    be_year = calculate_burmese_era(birth_date)
    kyin = calculate_kyin(be_year)

    python_weekday = birth_date.weekday()
    day_name = DAY_NAMES[python_weekday]

    day_value = PYTHON_WEEKDAY_TO_MAHABOTE_VALUE[python_weekday]

    # Core Mahabote house calculation
    house_index = (day_value - kyin) % 7
    house_info = MAHABOTE_HOUSES[house_index]

    return {
        "birth_day": day_name,
        "birth_day_burmese": DAY_TO_BURMESE[day_name],
        "house_name": house_info["name"],
        "house_burmese": house_info["burmese"],
        "ruling_planet": house_info["planet"],
        "be_year": be_year,
        "kyin": kyin,
        "day_value": day_value,
        "house_index": house_index,
        "nakshatra_burmese": NAKSHATRA_BURMESE_BY_DAY[day_name],
        "grid_number": house_index + 1,  # 1-indexed for display
        "characteristics": HOUSE_CHARACTERISTICS[house_info["name"]],
    }
