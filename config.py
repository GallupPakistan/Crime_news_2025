"""Central configuration: paths, column names and constants."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXCEL_PATH = DATA_DIR / "Crime_News_Analysis.xlsx"
PARQUET_PATH = DATA_DIR / "crime.parquet"
EXCEL_SHEET = "Data"

# Business rules
DATA_YEAR = 2025
CASUALTY_CAP = 50
NOT_SPECIFIED_CITY = "Not Specified"

LANGUAGES = ["Urdu", "English"]

# Source name typo fixes
SOURCE_FIXES = {
    "City42_Urdu_Crime_News_2025": "City42 News",
}

# Language typo fixes
LANGUAGE_FIXES = {
    "Ur": "Urdu",
}

# Urdu-script city names that have an English twin already present in the data.
CITY_ALIASES = {
    "حیدرآباد": "Hyderabad",
    "سبی": "Sibi",
    "پارا چنار": "Parachinar",
    "ننکانہ": "Nankana Sahib",
    "نارتھ کراچی": "North Karachi",
    "مظفرآباد": "Muzaffarabad",
    "میاں چنوں": "Mian Channu",
    "گوجرخان": "Gujar Khan",
    "وزیر آباد": "Wazirabad",
    "نوشہروفیروز": "Naushahro Feroze",
    "ہرنائی": "Harnai",
    "گڈانی": "Gadani",
    "تلہ گنگ": "Talagang",
    "بارکھان": "Barkhan",
    "ٹیکسلا": "Taxila",
    "ٹوبہ ٹیک سنگھ": "Toba Tek Singh",
    "ٹو بہ ٹیک سنگھ": "Toba Tek Singh",
    "چشتیاں": "Chishtian",
    "بولان": "Bolan",
    "بھیرہ": "Bhera",
    "عارف والا": "Arifwala",
    "شانگلہ": "Shangla",
    "خیر پور": "Khairpur",
    "کوٹ رادھا کشن": "Kot Radha Kishan",
    "چترال": "Chitral",
    "خانیوال": "Khanewal",
    "رحیم یارخان": "Rahim Yar Khan",
    "سجاول": "Sujawal",
    "ڈیرہ اسمٰعیل خان": "Dera Ismail Khan",
    "ڈی جی خان": "Dera Ghazi Khan",
    "میرپور": "Mirpur",
    "میرپور خاص": "Mirpurkhas",
    "پاراچنار": "Parachinar",
    "کیچ": "Kech",
    "سیہون": "Sehwan",
    "بٹ خیلہ": "Batkhela",
    "مری": "Murree",
    "کھاریاں": "Kharian",
    "اکوڑہ خٹک": "Akora Khattak",
    "راولاکوٹ": "Rawalakot",
    "وادی تیراہ": "Tirah Valley",
}

# Column names in the source workbook
COL_DATE = "Published_Date"
COL_CITY_RAW = "City"
COL_CRIME_TYPE_RAW = "Crime_Type"
COL_CITY = "City_Standard"
COL_CATEGORY = "Crime_Category"
COL_LANGUAGE = "Language"
COL_SOURCE = "Source_Name"

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

APP_TITLE = "Pakistan Crime News Analytics"
