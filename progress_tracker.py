"""
progress_tracker.py
Handles progress data visualization and analysis.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from database import get_progress


def get_progress_dataframe(user_id: int) -> pd.DataFrame:
    """Fetch progress records and return as a cleaned DataFrame."""
    rows = get_progress(user_id)
    if not rows:
        return pd.DataFrame()

    data = []
    for row in rows:
        data.append({
            "Date": row["date"],
            "Weight (kg)": row["weight"],
            "Calories Eaten": row["calories_eaten"],
            "Workout": row["workout_done"],
            "Notes": row["notes"],
        })

    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    return df


def plot_weight_progress(df: pd.DataFrame, target_weight: float = None):
    """Line chart showing weight over time."""
    if df.empty or "Weight (kg)" not in df.columns:
        return None

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Weight (kg)"],
        mode="lines+markers",
        name="Body Weight",
        line=dict(color="#FF6B35", width=3),
        marker=dict(size=8, color="#FF6B35"),
        fill="tozeroy",
        fillcolor="rgba(255, 107, 53, 0.1)"
    ))

    if target_weight:
        fig.add_hline(
            y=target_weight,
            line_dash="dash",
            line_color="#00D4FF",
            annotation_text=f"Target: {target_weight} kg",
            annotation_position="top right"
        )

    fig.update_layout(
        title="⚖️ Weight Progress Over Time",
        xaxis_title="Date",
        yaxis_title="Weight (kg)",
        template="plotly_dark",
        plot_bgcolor="#0D0D0D",
        paper_bgcolor="#1A1A2E",
        font=dict(color="#FFFFFF"),
        title_font=dict(size=18, color="#FF6B35"),
        hovermode="x unified",
        margin=dict(l=50, r=50, t=60, b=50),
    )
    return fig


def plot_calorie_tracking(df: pd.DataFrame, target_calories: float = None):
    """Bar chart for calorie intake over time."""
    if df.empty or "Calories Eaten" not in df.columns:
        return None

    colors = []
    for cal in df["Calories Eaten"]:
        if target_calories and cal > target_calories * 1.1:
            colors.append("#FF4136")
        elif target_calories and cal < target_calories * 0.9:
            colors.append("#FFDC00")
        else:
            colors.append("#2ECC40")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Date"],
        y=df["Calories Eaten"],
        marker_color=colors,
        name="Calories Eaten",
        text=df["Calories Eaten"],
        textposition="outside",
    ))

    if target_calories:
        fig.add_hline(
            y=target_calories,
            line_dash="dash",
            line_color="#00D4FF",
            annotation_text=f"Target: {target_calories:.0f} kcal",
            annotation_position="top right"
        )

    fig.update_layout(
        title="🔥 Daily Calorie Intake",
        xaxis_title="Date",
        yaxis_title="Calories (kcal)",
        template="plotly_dark",
        plot_bgcolor="#0D0D0D",
        paper_bgcolor="#1A1A2E",
        font=dict(color="#FFFFFF"),
        title_font=dict(size=18, color="#FF6B35"),
        margin=dict(l=50, r=50, t=60, b=50),
    )
    return fig


def get_weekly_summary(df: pd.DataFrame) -> dict:
    """Return summary stats from the last 7 days of data."""
    if df.empty:
        return {}

    last_7 = df.tail(7)

    summary = {
        "entries": len(last_7),
        "avg_weight": round(last_7["Weight (kg)"].mean(), 1) if "Weight (kg)" in last_7 else None,
        "weight_change": None,
        "avg_calories": round(last_7["Calories Eaten"].mean(), 0) if "Calories Eaten" in last_7 else None,
        "workouts_done": last_7["Workout"].notna().sum() if "Workout" in last_7 else 0,
    }

    if len(last_7) >= 2:
        first_w = last_7["Weight (kg)"].iloc[0]
        last_w = last_7["Weight (kg)"].iloc[-1]
        summary["weight_change"] = round(last_w - first_w, 1)

    return summary
