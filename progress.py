"""
progress.py - Weight progress tracker.
Stores daily weight in SQL Server and renders a Streamlit chart.
"""
import streamlit as st
import pandas as pd
from datetime import date
from database import get_connection


# ── DB helpers ─────────────────────────────────────────────────────────────────
def log_weight(user_id: int, weight: float, log_date: date):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO Progress (user_id, weight, date) VALUES (?, ?, ?)",
        (user_id, weight, log_date)
    )
    conn.commit()
    conn.close()


def get_progress(user_id: int) -> pd.DataFrame:
    conn = get_connection()
    df   = pd.read_sql(
        "SELECT date, weight FROM Progress WHERE user_id = ? ORDER BY date",
        conn,
        params=(user_id,)
    )
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    return df


# ── Streamlit page ─────────────────────────────────────────────────────────────
def show_progress_page(user: dict):
    st.title("📊 Progress Tracker")
    st.markdown("Log your weight daily and watch your transformation journey.")

    # ── Log new entry ──────────────────────────────────────────────────────────
    with st.form("log_form"):
        col1, col2 = st.columns(2)
        with col1:
            weight_today = st.number_input("Today's Weight (kg)", 30.0, 250.0, 70.0, step=0.1)
        with col2:
            log_date = st.date_input("Date", value=date.today())
        submitted = st.form_submit_button("➕ Log Weight", use_container_width=True)

    if submitted:
        try:
            log_weight(user["id"], weight_today, log_date)
            st.success(f"✅ Weight {weight_today} kg logged for {log_date}")
        except Exception as e:
            st.error(f"Error saving: {e}")

    # ── History & chart ────────────────────────────────────────────────────────
    st.markdown("---")
    try:
        df = get_progress(user["id"])
    except Exception as e:
        st.error(f"Could not load progress: {e}")
        return

    if df.empty:
        st.info("No weight logs yet. Start logging to see your progress chart!")
        return

    st.subheader("📈 Weight Over Time")
    st.line_chart(df.set_index("date")["weight"], use_container_width=True)

    # KPI row
    st.markdown("---")
    first_w = df["weight"].iloc[0]
    last_w  = df["weight"].iloc[-1]
    change  = round(last_w - first_w, 1)
    m1, m2, m3 = st.columns(3)
    m1.metric("Starting Weight", f"{first_w} kg")
    m2.metric("Current Weight",  f"{last_w} kg")
    m3.metric("Total Change",    f"{change:+.1f} kg")

    # Full history table
    st.markdown("---")
    st.subheader("📋 Full Log History")
    display = df.copy()
    display["date"] = display["date"].dt.strftime("%d %b %Y")
    display.columns = ["Date", "Weight (kg)"]
    st.dataframe(display.iloc[::-1].reset_index(drop=True), use_container_width=True)
