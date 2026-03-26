import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from database import get_progress


def get_progress_charts(user_id, target_calories):
    data = get_progress(user_id)
    if not data:
        return None, None, None

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Weight chart
    fig_weight = go.Figure()
    fig_weight.add_trace(go.Scatter(
        x=df['date'], y=df['weight'],
        mode='lines+markers',
        name='Weight',
        line=dict(color='#FF6B35', width=3),
        marker=dict(size=8, color='#FF6B35')
    ))
    fig_weight.update_layout(
        title='⚖️ Weight Progress',
        plot_bgcolor='#0D1525',
        paper_bgcolor='#0D1525',
        font=dict(color='white'),
        xaxis=dict(gridcolor='#1E2761'),
        yaxis=dict(gridcolor='#1E2761', title='Weight (kg)'),
        hovermode='x unified'
    )

    # Calories chart
    colors = ['#2ECC71' if abs(c - target_calories) / target_calories <= 0.1
              else '#E74C3C' if c > target_calories else '#F39C12'
              for c in df['calories_eaten']]
    fig_cal = go.Figure()
    fig_cal.add_trace(go.Bar(
        x=df['date'], y=df['calories_eaten'],
        name='Calories', marker_color=colors
    ))
    fig_cal.add_hline(
        y=target_calories, line_dash="dash",
        line_color="#FF6B35", annotation_text="Target"
    )
    fig_cal.update_layout(
        title='🔥 Daily Calories',
        plot_bgcolor='#0D1525',
        paper_bgcolor='#0D1525',
        font=dict(color='white'),
        xaxis=dict(gridcolor='#1E2761'),
        yaxis=dict(gridcolor='#1E2761', title='Calories (kcal)'),
    )

    # Stats
    stats = {
        'total_days': len(df),
        'avg_weight': round(df['weight'].mean(), 1),
        'avg_calories': round(df['calories_eaten'].mean(), 1),
        'workouts_done': int(df['workout_done'].sum()),
        'latest_weight': round(df['weight'].iloc[-1], 1),
        'first_weight': round(df['weight'].iloc[0], 1),
        'weight_change': round(df['weight'].iloc[-1] - df['weight'].iloc[0], 1)
    }

    return fig_weight, fig_cal, stats
