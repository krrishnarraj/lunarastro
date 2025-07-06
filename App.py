import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import pytz
from utils.astro import Astro
from utils.chart_utils import (
    build_chart,
    static_data,
    astro_house,
    deg_in_house,
    deg_min,
)

st.set_page_config(page_title="Planetary Positions", layout="wide")
st.title("Planetary Positions")


# Cache singleton Astro
@st.cache_resource
def get_astro():
    return Astro()


# Sidebar IST inputs
ist = pytz.timezone("Asia/Kolkata")
now_ist = datetime.now(ist)

# Initialize defaults in session_state
for key, val in {
    "year": now_ist.year,
    "month": now_ist.month,
    "day": now_ist.day,
    "hour": now_ist.hour,
    "minute": now_ist.minute,
}.items():
    st.session_state.setdefault(key, val)

st.sidebar.subheader("IST Local Date Time")

# number_inputs with built-in ± steppers
year = st.sidebar.number_input(
    "Year", min_value=1900, max_value=2100, step=1, key="year"
)
month = st.sidebar.number_input("Month", min_value=1, max_value=12, step=1, key="month")
day = st.sidebar.number_input("Day", min_value=1, max_value=31, step=1, key="day")
hour = st.sidebar.number_input("Hour", min_value=0, max_value=23, step=1, key="hour")
minute = st.sidebar.number_input(
    "Minute", min_value=0, max_value=59, step=1, key="minute"
)

# Show selected IST once
ist_dt = ist.localize(
    datetime(
        st.session_state.year,
        st.session_state.month,
        st.session_state.day,
        st.session_state.hour,
        st.session_state.minute,
    )
)
st.sidebar.success(f"Selected IST : {ist_dt:%d %b %Y  %H:%M}")

# Fetch sky details in UTC
astro = get_astro()
utc_dt = ist_dt.astimezone(timezone.utc)
with st.spinner("Calculating planetary positions…"):
    sky = astro.get_sky_details(utc_dt)

# Draw chart
st.plotly_chart(
    build_chart(sky),
    use_container_width=True,
    config=dict(displayModeBar=False, displaylogo=False),
)

# Build and show table (no index)
houses, _, psym, pname, _ = static_data()
rows = []
for pl, dat in sky.items():
    d, m = deg_min(deg_in_house(dat["lon"]))
    rows.append(
        {
            "Planet": f"{psym[pl]} {pname[pl]}",
            "House": houses[astro_house(dat["lon"])],
            "Position": f"{d}° {m:02d}'",
            "Speed": f"{dat['dlon']:.4f}",
            "Retrograde": "Yes" if dat["dlon"] < 0 else "No",
        }
    )

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True, hide_index=True)
