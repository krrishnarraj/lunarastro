import streamlit as st
from datetime import datetime, timedelta
import calendar


def add_months(dt: datetime, inc: int) -> datetime:
    total = dt.month - 1 + inc
    yr = dt.year + total // 12
    mn = total % 12 + 1
    day = min(dt.day, calendar.monthrange(yr, mn)[1])
    return dt.replace(year=yr, month=mn, day=day)


def smart_inc(y: int, m: int, d: int, hh: int, mm: int, field: str, step: int):
    """Increment one part of the date/time while handling overflow."""
    dt = datetime(y, m, d, hh, mm)
    if field == "year":
        try:
            dt = dt.replace(year=dt.year + step)
        except ValueError:
            dt = dt.replace(year=dt.year + step, day=28)
    elif field == "month":
        dt = add_months(dt, step)
    elif field == "day":
        dt += timedelta(days=step)
    elif field == "hour":
        dt += timedelta(hours=step)
    elif field == "minute":
        dt += timedelta(minutes=step)
    return dt.year, dt.month, dt.day, dt.hour, dt.minute


def time_widget(label: str, field: str, low: int, high: int):
    """
    Renders a number_input and ◀ ▶ buttons in the sidebar,
    and mutates st.session_state[field] with wrap‐aware stepping.
    """
    col1, col2, col3 = st.sidebar.columns([2, 1, 1])
    # number input
    with col1:
        val = st.number_input(
            label,
            min_value=low,
            max_value=high,
            value=st.session_state[field],
            key=f"{field}_in",
        )
        st.session_state[field] = val
    # decrement
    with col2:
        if st.button("◀", key=f"{field}_dec"):
            y, mo, da, hh, mi = smart_inc(
                st.session_state.year,
                st.session_state.month,
                st.session_state.day,
                st.session_state.hour,
                st.session_state.minute,
                field if field != "year" else "year",
                -1,
            )
            st.session_state.update(dict(year=y, month=mo, day=da, hour=hh, minute=mi))
            st.rerun()
    # increment
    with col3:
        if st.button("▶", key=f"{field}_inc"):
            y, mo, da, hh, mi = smart_inc(
                st.session_state.year,
                st.session_state.month,
                st.session_state.day,
                st.session_state.hour,
                st.session_state.minute,
                field if field != "year" else "year",
                +1,
            )
            st.session_state.update(dict(year=y, month=mo, day=da, hour=hh, minute=mi))
            st.rerun()
