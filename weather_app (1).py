import streamlit as st
import requests

# --- Page Config ---
st.set_page_config(
    page_title="Weather App",
    page_icon="🌤️",
    layout="centered"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url({   "standard" : {      "addresst" : {},      "statename" : {},      "city" : "City",      "prov" : "AU",      "countryname" : "Australia",      "postal" : {},      "confidence" : "0.3"   },   "longt" : "149.12911",   "alt" : {      "loc" : {         "longt" : "149.12879",         "prov" : "AU",         "city" : "City",         "countryname" : "Australia",         "postal" : "2601",         "region" : "ACT",         "latt" : "-35.28133"      }   },   "elevation" : {},   "latt" : "-35.28111"}
    '');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }

    .weather-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 24px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
    }

    .temp-display {
        font-size: 5rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1;
    }

    .city-name {
        font-size: 1.8rem;
        font-weight: 600;
        color: #a78bfa;
        margin-bottom: 0.5rem;
    }

    .description {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.7);
        text-transform: capitalize;
        margin-bottom: 1.5rem;
    }

    .stat-box {
        background: rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }

    .stat-label {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.5);
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .stat-value {
        font-size: 1.4rem;
        font-weight: 600;
        color: #c4b5fd;
    }

    .error-box {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 12px;
        padding: 1rem;
        color: #fca5a5;
    }

    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px !important;
        color: white !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        padding: 0.6rem 2rem !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.5) !important;
    }

    label {
        color: rgba(255,255,255,0.7) !important;
    }
</style>
""", unsafe_allow_html=True)


# --- Helpers ---
def get_weather(city: str, api_key: str, unit: str = "metric") -> dict | None:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": unit}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            return {"error": f"City **{city}** not found. Please check the spelling."}
        elif resp.status_code == 401:
            return {"error": "Invalid API key. Please check your OpenWeatherMap API key."}
        else:
            return {"error": f"API error: {resp.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"error": "No internet connection. Please check your network."}
    except Exception as e:
        return {"error": str(e)}


def weather_emoji(condition: str) -> str:
    mapping = {
        "clear": "☀️", "clouds": "☁️", "rain": "🌧️",
        "drizzle": "🌦️", "thunderstorm": "⛈️", "snow": "❄️",
        "mist": "🌫️", "fog": "🌫️", "haze": "🌫️",
        "smoke": "🌫️", "dust": "🌪️", "sand": "🌪️",
        "tornado": "🌪️"
    }
    key = condition.lower()
    for k, v in mapping.items():
        if k in key:
            return v
    return "🌡️"


# --- UI ---
st.markdown("<h1 style='text-align:center; color:white; font-size:2.5rem; margin-bottom:0.2rem;'>🌤️ Weather App</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:rgba(255,255,255,0.5); margin-bottom:2rem;'>Real-time weather powered by OpenWeatherMap</p>", unsafe_allow_html=True)

# API key input
with st.expander("⚙️ API Key Setup", expanded=not st.session_state.get("api_key")):
    api_key = st.text_input(
        "OpenWeatherMap API Key",
        type="password",
        placeholder="Paste your free API key here…",
        help="Get a free key at https://openweathermap.org/api"
    )
    st.markdown("[👉 Get free API key](https://openweathermap.org/api)", unsafe_allow_html=True)
    if api_key:
        st.session_state["api_key"] = api_key

api_key = st.session_state.get("api_key", "")

# City + unit
col1, col2 = st.columns([3, 1])
with col1:
    city = st.text_input("City Name", placeholder="e.g. London, Tokyo, New York…", label_visibility="collapsed")
with col2:
    unit = st.selectbox("Unit", ["°C", "°F"], label_visibility="collapsed")

unit_code = "metric" if unit == "°C" else "imperial"
unit_symbol = unit

search = st.button("Get Weather", use_container_width=True)

# Fetch & Display
if search or city:
    if not api_key:
        st.markdown('<div class="error-box">⚠️ Please enter your OpenWeatherMap API key above.</div>', unsafe_allow_html=True)
    elif not city.strip():
        st.markdown('<div class="error-box">⚠️ Please enter a city name.</div>', unsafe_allow_html=True)
    else:
        with st.spinner("Fetching weather…"):
            data = get_weather(city.strip(), api_key, unit_code)

        if data and "error" in data:
            st.markdown(f'<div class="error-box">❌ {data["error"]}</div>', unsafe_allow_html=True)
        elif data:
            name = data["name"]
            country = data["sys"]["country"]
            temp = round(data["main"]["temp"])
            feels = round(data["main"]["feels_like"])
            humidity = data["main"]["humidity"]
            wind = round(data["wind"]["speed"])
            wind_unit = "m/s" if unit_code == "metric" else "mph"
            visibility = round(data.get("visibility", 0) / 1000, 1)
            desc = data["weather"][0]["description"]
            main_cond = data["weather"][0]["main"]
            emoji = weather_emoji(main_cond)

            # Main card
            st.markdown(f"""
            <div class="weather-card">
                <div class="city-name">📍 {name}, {country}</div>
                <div style="font-size:4rem; margin: 0.5rem 0;">{emoji}</div>
                <div class="temp-display">{temp}{unit_symbol}</div>
                <div class="description">{desc}</div>
                <div style="color: rgba(255,255,255,0.5); font-size:0.9rem;">Feels like {feels}{unit_symbol}</div>
            </div>
            """, unsafe_allow_html=True)

            # Stats
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-label">💧 Humidity</div>
                    <div class="stat-value">{humidity}%</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-label">💨 Wind</div>
                    <div class="stat-value">{wind} {wind_unit}</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-label">👁️ Visibility</div>
                    <div class="stat-value">{visibility} km</div>
                </div>""", unsafe_allow_html=True)

            # Min/Max
            temp_min = round(data["main"]["temp_min"])
            temp_max = round(data["main"]["temp_max"])
            st.markdown(f"""
            <div style="text-align:center; color:rgba(255,255,255,0.5); font-size:0.9rem; margin-top:1rem;">
                🌡️ Low: {temp_min}{unit_symbol} &nbsp;|&nbsp; High: {temp_max}{unit_symbol}
            </div>""", unsafe_allow_html=True)
