import streamlit as st
import pytz
from datetime import datetime, timezone
from utils.astro import Astro
from utils.chart_utils import (
    build_chart,
    static_data,
    astro_house,
    deg_in_house,
    deg_min,
)
from utils.datetime_utils import smart_inc, time_widget

st.set_page_config(page_title="Planetary Positions", layout="wide")
st.title("Planetary Positions")


# cache Astro singleton
@st.cache_resource
def get_astro():
    return Astro()


# Sidebar init
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)
for k, v in dict(
    year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute
).items():
    st.session_state.setdefault(k, v)

st.sidebar.subheader("IST Local Date Time")

# draw each widget by delegating to our helper
time_widget("Year", "year", 1900, 2100)
time_widget("Month", "month", 1, 12)
time_widget("Day", "day", 1, 31)
time_widget("Hour", "hour", 0, 23)
time_widget("Minute", "minute", 0, 59)

# show chosen IST
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

# fetch & draw
astro = get_astro()
utc_dt = ist_dt.astimezone(timezone.utc)
with st.spinner("Calculating sky…"):
    sky = astro.get_sky_details(utc_dt)

st.plotly_chart(
    build_chart(sky),
    use_container_width=True,
    config=dict(displayModeBar=False, displaylogo=False),
)

# table
houses, _, psym, pname, _ = static_data()
rows = []
for pl, data in sky.items():
    d, m = deg_min(deg_in_house(data["lon"]))
    rows.append(
        dict(
            Planet=f"{psym[pl]} {pname[pl]}",
            House=houses[astro_house(data["lon"])],
            Position=f"{d}° {m:02d}'",
            Speed=f"{data['dlon']:.4f}",
            Retrograde="Yes" if data["dlon"] < 0 else "No",
        )
    )
st.table(rows)
