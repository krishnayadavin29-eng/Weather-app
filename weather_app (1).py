import streamlit as st
import requests

st.set_page_config(page_title="Weather App", page_icon="🌤️", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    .weather-card {
        background: rgba(255,255,255,0.08); backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.15); border-radius: 24px;
        padding: 2rem; margin: 1rem 0; text-align: center;
    }
    .temp-display { font-size: 5rem; font-weight: 700; color: #fff; line-height: 1; }
    .city-name { font-size: 1.8rem; font-weight: 600; color: #a78bfa; margin-bottom: 0.5rem; }
    .description { font-size: 1.1rem; color: rgba(255,255,255,0.7); margin-bottom: 1.5rem; }
    .stat-box {
        background: rgba(255,255,255,0.06); border-radius: 16px; padding: 1rem;
        text-align: center; border: 1px solid rgba(255,255,255,0.1);
    }
    .stat-label { font-size: 0.75rem; color: rgba(255,255,255,0.5); text-transform: uppercase; letter-spacing: 0.1em; }
    .stat-value { font-size: 1.4rem; font-weight: 600; color: #c4b5fd; }
    .error-box {
        background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.4);
        border-radius: 12px; padding: 1rem; color: #fca5a5;
    }
    .badge {
        display: inline-block; background: rgba(167,139,250,0.2);
        border: 1px solid rgba(167,139,250,0.4); border-radius: 20px;
        padding: 0.2rem 0.8rem; font-size: 0.75rem; color: #c4b5fd; margin-bottom: 1rem;
    }
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px !important; color: white !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
        color: white !important; border: none !important;
        border-radius: 12px !important; font-weight: 600 !important; width: 100% !important;
    }
    label { color: rgba(255,255,255,0.7) !important; }
</style>
""", unsafe_allow_html=True)

WMO_CODES = {
    0: ("Clear Sky", "☀️"),
    1: ("Mainly Clear", "🌤️"), 2: ("Partly Cloudy", "⛅"), 3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"), 48: ("Icy Fog", "🌫️"),
    51: ("Light Drizzle", "🌦️"), 53: ("Drizzle", "🌦️"), 55: ("Heavy Drizzle", "🌧️"),
    61: ("Slight Rain", "🌧️"), 63: ("Rain", "🌧️"), 65: ("Heavy Rain", "🌧️"),
    71: ("Slight Snow", "❄️"), 73: ("Snow", "❄️"), 75: ("Heavy Snow", "❄️"),
    77: ("Snow Grains", "🌨️"),
    80: ("Slight Showers", "🌦️"), 81: ("Showers", "🌧️"), 82: ("Violent Showers", "⛈️"),
    85: ("Snow Showers", "🌨️"), 86: ("Heavy Snow Showers", "🌨️"),
    95: ("Thunderstorm", "⛈️"), 96: ("Thunderstorm w/ Hail", "⛈️"), 99: ("Severe Thunderstorm", "⛈️"),
}

def geocode(city):
    try:
        resp = requests.get(f"https://geocode.xyz/{city}?json=1", timeout=10)
        data = resp.json()
        lat = float(data.get("latt", 0))
        lon = float(data.get("longt", 0))
        name = data.get("city") or data.get("region") or city.title()
        country = data.get("country", "")
        if lat == 0 and lon == 0:
            return None, None, None, None, "City not found. Try a different spelling."
        return lat, lon, name, country, None
    except Exception as e:
        return None, None, None, None, f"Geocoding error: {e}"

def get_weather(lat, lon, unit):
    temp_unit = "celsius" if unit == "°C" else "fahrenheit"
    wind_unit = "ms" if unit == "°C" else "mph"
    params = {
        "latitude": lat, "longitude": lon,
        "current": ["temperature_2m","apparent_temperature","relative_humidity_2m",
                    "wind_speed_10m","weathercode","visibility"],
        "daily": ["temperature_2m_max","temperature_2m_min"],
        "temperature_unit": temp_unit, "wind_speed_unit": wind_unit,
        "timezone": "auto", "forecast_days": 1,
    }
    try:
        resp = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=10)
        return resp.json(), None
    except Exception as e:
        return None, str(e)

st.markdown("<h1 style='text-align:center;color:white;font-size:2.5rem;margin-bottom:0;'>🌤️ Weather App</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;margin-bottom:1.5rem;'><span class='badge'>✅ No API Key Required</span></div>", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    city = st.text_input("City", placeholder="e.g. Delhi, Tokyo, Paris…", label_visibility="collapsed")
with col2:
    unit = st.selectbox("Unit", ["°C", "°F"], label_visibility="collapsed")

search = st.button("Get Weather", use_container_width=True)

if search and city.strip():
    with st.spinner("Finding city…"):
        lat, lon, name, country, geo_err = geocode(city.strip())

    if geo_err:
        st.markdown(f'<div class="error-box">❌ {geo_err}</div>', unsafe_allow_html=True)
    else:
        with st.spinner("Fetching weather…"):
            data, err = get_weather(lat, lon, unit)

        if err:
            st.markdown(f'<div class="error-box">❌ {err}</div>', unsafe_allow_html=True)
        elif data:
            cur = data["current"]
            daily = data.get("daily", {})
            temp = round(cur["temperature_2m"])
            feels = round(cur["apparent_temperature"])
            humidity = cur["relative_humidity_2m"]
            wind = round(cur["wind_speed_10m"])
            wind_lbl = "m/s" if unit == "°C" else "mph"
            vis_m = cur.get("visibility", 0)
            vis_km = round(vis_m / 1000, 1) if vis_m else "N/A"
            wcode = cur.get("weathercode", 0)
            desc, emoji = WMO_CODES.get(wcode, ("Unknown", "🌡️"))
            temp_max = round(daily["temperature_2m_max"][0]) if daily.get("temperature_2m_max") else "—"
            temp_min = round(daily["temperature_2m_min"][0]) if daily.get("temperature_2m_min") else "—"
            location_str = f"{name}, {country}" if country else name

            st.markdown(f"""
            <div class="weather-card">
                <div class="city-name">📍 {location_str}</div>
                <div style="font-size:4rem;margin:0.5rem 0;">{emoji}</div>
                <div class="temp-display">{temp}{unit}</div>
                <div class="description">{desc}</div>
                <div style="color:rgba(255,255,255,0.5);font-size:0.9rem;">Feels like {feels}{unit}</div>
            </div>""", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="stat-box"><div class="stat-label">💧 Humidity</div><div class="stat-value">{humidity}%</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="stat-box"><div class="stat-label">💨 Wind</div><div class="stat-value">{wind} {wind_lbl}</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="stat-box"><div class="stat-label">👁️ Visibility</div><div class="stat-value">{vis_km} km</div></div>', unsafe_allow_html=True)

            st.markdown(f"""
            <div style="text-align:center;color:rgba(255,255,255,0.5);font-size:0.9rem;margin-top:1rem;">
                🌡️ Low: {temp_min}{unit} &nbsp;|&nbsp; High: {temp_max}{unit}
            </div>""", unsafe_allow_html=True)

elif search and not city.strip():
    st.markdown('<div class="error-box">⚠️ Please enter a city name.</div>', unsafe_allow_html=True)
