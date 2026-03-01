"""
app.py — Gnaneswar Fitness AI
Main Streamlit application entry point.

Run with:   streamlit run app.py
"""

import streamlit as st
from datetime import date

# Internal modules
import database as db
import auth as auth_module
import fitness_calc as calc
import ai_engine as ai
import progress_tracker as pt

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Gnaneswar Fitness AI",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #0A0A0F !important;
    color: #E8E8E8 !important;
    font-family: 'Inter', sans-serif;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D0D1A 0%, #12121F 100%) !important;
    border-right: 1px solid #FF6B35 !important;
}
[data-testid="stSidebar"] * { color: #E8E8E8 !important; }

.main-header {
    background: linear-gradient(135deg, #0D0D1A 0%, #1A0D2E 50%, #0D1A0D 100%);
    border: 1px solid #FF6B35;
    border-radius: 16px;
    padding: 30px 40px;
    margin-bottom: 30px;
    text-align: center;
}
.main-title {
    font-family: 'Oswald', sans-serif;
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #FF6B35, #FF9A3C, #FFCC02);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: 3px;
}
.main-subtitle {
    color: #9090AA;
    font-size: 1rem;
    letter-spacing: 2px;
    margin-top: 8px;
    text-transform: uppercase;
}

.metric-card {
    background: linear-gradient(135deg, #12121F, #1A1A2E);
    border: 1px solid rgba(255, 107, 53, 0.3);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin-bottom: 16px;
}
.metric-value {
    font-family: 'Oswald', sans-serif;
    font-size: 2.2rem;
    color: #FF6B35;
    font-weight: 700;
    line-height: 1;
}
.metric-label {
    font-size: 0.75rem;
    color: #9090AA;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 6px;
}

.section-header {
    font-family: 'Oswald', sans-serif;
    font-size: 1.6rem;
    color: #FF6B35;
    letter-spacing: 2px;
    text-transform: uppercase;
    border-bottom: 2px solid rgba(255,107,53,0.3);
    padding-bottom: 10px;
    margin-bottom: 20px;
}

div.stButton > button {
    background: linear-gradient(135deg, #FF6B35, #FF4500) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Oswald', sans-serif !important;
    font-size: 1rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    padding: 10px 24px !important;
    width: 100% !important;
}

.chat-user {
    background: linear-gradient(135deg, #1A1A2E, #12122E);
    border-left: 3px solid #FF6B35;
    border-radius: 0 12px 12px 0;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.95rem;
}
.chat-bot {
    background: linear-gradient(135deg, #0D1A0D, #121F12);
    border-left: 3px solid #2ECC40;
    border-radius: 0 12px 12px 0;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.95rem;
}
.chat-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #9090AA;
    margin-bottom: 4px;
}

.info-box {
    background: rgba(0, 212, 255, 0.08);
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: 10px;
    padding: 16px;
    margin: 12px 0;
    color: #AAD4FF;
}
.success-box {
    background: rgba(46, 204, 64, 0.08);
    border: 1px solid rgba(46, 204, 64, 0.3);
    border-radius: 10px;
    padding: 16px;
    margin: 12px 0;
    color: #7AFF8A;
}
.warning-box {
    background: rgba(255, 220, 0, 0.08);
    border: 1px solid rgba(255, 220, 0, 0.3);
    border-radius: 10px;
    padding: 16px;
    margin: 12px 0;
    color: #FFE566;
}

.ai-output {
    background: linear-gradient(135deg, #0D1520, #0D0D1A);
    border: 1px solid rgba(255,107,53,0.25);
    border-radius: 12px;
    padding: 24px;
    margin-top: 16px;
    font-size: 0.92rem;
    line-height: 1.7;
    max-height: 600px;
    overflow-y: auto;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0A0A0F; }
::-webkit-scrollbar-thumb { background: #FF6B35; border-radius: 3px; }
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Database init
# ---------------------------------------------------------------------------
db.init_db()

# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------
def init_session():
    defaults = {
        "logged_in": False,
        "user_id": None,
        "user_name": "",
        "current_page": "🏠 Home",
        "diet_plan": "",
        "workout_plan": "",
        "chat_messages": [],
        "chat_loaded": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session()


def get_profile_dict():
    if not st.session_state.logged_in:
        return {}
    profile = db.get_profile(st.session_state.user_id)
    user = db.get_user_by_id(st.session_state.user_id)
    if not profile:
        return {}
    return {
        "name": user["name"] if user else "User",
        "age": profile["age"],
        "gender": profile["gender"],
        "height": profile["height"],
        "weight": profile["weight"],
        "goal": profile["goal"],
        "experience": profile["experience"],
        "bmi": profile["bmi"],
        "bmr": profile["bmr"],
        "daily_calories": profile["daily_calories"],
        "protein_req": profile["protein_req"],
    }


# ---------------------------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding: 10px 0 20px 0;'>
            <div style='font-family:Oswald,sans-serif; font-size:1.6rem;
                        color:#FF6B35; letter-spacing:2px; font-weight:700;'>
                💪 FITNESS AI
            </div>
            <div style='font-size:0.7rem; color:#9090AA; letter-spacing:2px;
                        text-transform:uppercase; margin-top:4px;'>
                GNANESWAR EDITION
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border-color:rgba(255,107,53,0.2);'>", unsafe_allow_html=True)

        if st.session_state.logged_in:
            st.markdown(f"""
            <div style='background:rgba(255,107,53,0.1); border:1px solid rgba(255,107,53,0.3);
                        border-radius:8px; padding:12px; margin-bottom:16px; text-align:center;'>
                <div style='font-size:0.7rem; color:#9090AA; text-transform:uppercase;'>Logged in as</div>
                <div style='font-family:Oswald,sans-serif; font-size:1.1rem; color:#FF6B35; margin-top:4px;'>
                    {st.session_state.user_name}
                </div>
            </div>
            """, unsafe_allow_html=True)

            pages = [
                "🏠 Home",
                "👤 My Profile",
                "🥗 AI Diet Planner",
                "🏋️ AI Workout Generator",
                "🤖 AI Trainer Chat",
                "📊 Progress Tracker",
            ]
        else:
            pages = ["🏠 Home", "🔐 Login / Register"]

        selected = st.radio("Navigate", pages, label_visibility="collapsed", key="nav_radio")
        st.session_state.current_page = selected

        if st.session_state.logged_in:
            st.markdown("<hr style='border-color:rgba(255,107,53,0.2);'>", unsafe_allow_html=True)
            if st.button("🚪 Logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                init_session()
                st.rerun()


# ---------------------------------------------------------------------------
# Page: Home
# ---------------------------------------------------------------------------
def page_home():
    st.markdown("""
    <div class='main-header'>
        <div class='main-title'>⚡ GNANESWAR FITNESS AI</div>
        <div class='main-subtitle'>Your AI-Powered Personal Gym Trainer & Nutritionist</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    features = [
        ("🥗", "AI Diet Planner", "7-day personalized Indian diet plans tailored to your goal"),
        ("🏋️", "AI Workout Generator", "Push-Pull-Legs splits customized for your experience level"),
        ("🤖", "AI Trainer Chat", "Ask anything to your 24/7 personal AI gym trainer"),
        ("📊", "Progress Tracker", "Log daily weight & calories, visualize your transformation"),
        ("🔥", "BMR & Calorie Calc", "Scientifically calculated daily calorie and protein targets"),
        ("🔐", "Secure Accounts", "Your data is safely stored in a private local database"),
    ]
    cols = [col1, col2, col3, col1, col2, col3]
    for (icon, title, desc), col in zip(features, cols):
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size:2rem;'>{icon}</div>
                <div style='font-family:Oswald,sans-serif; font-size:1.1rem;
                            color:#FF6B35; margin:8px 0 6px 0; letter-spacing:1px;'>
                    {title}
                </div>
                <div style='font-size:0.82rem; color:#9090AA; line-height:1.5;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        st.markdown("""<div class='info-box'>
            👋 <strong>Welcome!</strong> Please <strong>Register or Login</strong> from the sidebar to get started.
        </div>""", unsafe_allow_html=True)
    else:
        profile = get_profile_dict()
        if not profile:
            st.markdown("""<div class='warning-box'>
                ⚠️ Your profile is incomplete. Go to <strong>My Profile</strong> to set up your details.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class='success-box'>
                ✅ Welcome back, <strong>{profile['name']}</strong>! Goal: <strong>{profile['goal']}</strong> |
                Daily Target: <strong>{profile['daily_calories']:.0f} kcal</strong> |
                Protein: <strong>{profile['protein_req']:.0f}g</strong>
            </div>""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page: Login / Register
# ---------------------------------------------------------------------------
def page_auth():
    st.markdown("<div class='section-header'>🔐 Account Access</div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("🔑 Login")
        if submitted:
            user, msg = auth_module.login_user(email, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user["id"]
                st.session_state.user_name = user["name"]
                st.session_state.current_page = "🏠 Home"
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("register_form"):
            name = st.text_input("Full Name", placeholder="Gnaneswar")
            email = st.text_input("Email Address", placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="Min. 6 characters")
            confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
            submitted = st.form_submit_button("🚀 Create Account")
        if submitted:
            success, msg = auth_module.register_user(name, email, password, confirm)
            if success:
                st.success(f"✅ {msg} Please login.")
            else:
                st.error(msg)


# ---------------------------------------------------------------------------
# Page: Profile
# ---------------------------------------------------------------------------
def page_profile():
    st.markdown("<div class='section-header'>👤 My Fitness Profile</div>", unsafe_allow_html=True)
    existing = db.get_profile(st.session_state.user_id)

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age (years)", min_value=10, max_value=90,
                                  value=int(existing["age"]) if existing and existing["age"] else 25)
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0,
                                     value=float(existing["height"]) if existing and existing["height"] else 170.0,
                                     step=0.5)
            goal = st.selectbox("Fitness Goal", ["Bulking", "Cutting", "Maintain"],
                                index=["Bulking", "Cutting", "Maintain"].index(existing["goal"])
                                if existing and existing["goal"] else 0)
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female"],
                                  index=["Male", "Female"].index(existing["gender"])
                                  if existing and existing["gender"] else 0)
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0,
                                     value=float(existing["weight"]) if existing and existing["weight"] else 70.0,
                                     step=0.5)
            experience = st.selectbox("Experience Level", ["Beginner", "Intermediate", "Advanced"],
                                      index=["Beginner", "Intermediate", "Advanced"].index(existing["experience"])
                                      if existing and existing["experience"] else 0)
        activity = st.selectbox("Activity Level", [
            "Sedentary (little/no exercise)",
            "Light (1-3 days/week)",
            "Moderate (3-5 days/week)",
            "Active (6-7 days/week)",
            "Very Active (2x/day)",
        ], index=2)
        submitted = st.form_submit_button("💾 Save Profile & Calculate")

    if submitted:
        results = calc.full_calculation(weight, height, age, gender, goal, experience, activity)
        db.save_profile(
            user_id=st.session_state.user_id,
            age=age, gender=gender, height=height, weight=weight,
            goal=goal, experience=experience,
            bmi=results["bmi"], bmr=results["bmr"],
            daily_calories=results["daily_calories"],
            protein_req=results["protein_req"],
        )
        st.success("✅ Profile saved successfully!")
        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>{results['bmi']}</div>
                <div class='metric-label'>BMI — {results['bmi_category']}</div></div>""",
                unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>{int(results['bmr'])}</div>
                <div class='metric-label'>BMR (kcal/day)</div></div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>{int(results['daily_calories'])}</div>
                <div class='metric-label'>Target Calories ({goal})</div></div>""", unsafe_allow_html=True)
        with m4:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>{int(results['protein_req'])}g</div>
                <div class='metric-label'>Daily Protein</div></div>""", unsafe_allow_html=True)

    elif existing:
        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>{existing['bmi']}</div>
                <div class='metric-label'>BMI</div></div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>{int(existing['bmr'])}</div>
                <div class='metric-label'>BMR (kcal)</div></div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>{int(existing['daily_calories'])}</div>
                <div class='metric-label'>Daily Target (kcal)</div></div>""", unsafe_allow_html=True)
        with m4:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>{int(existing['protein_req'])}g</div>
                <div class='metric-label'>Daily Protein</div></div>""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page: AI Diet Planner
# ---------------------------------------------------------------------------
def page_diet():
    st.markdown("<div class='section-header'>🥗 AI Diet Planner</div>", unsafe_allow_html=True)
    profile = get_profile_dict()
    if not profile:
        st.markdown("""<div class='warning-box'>
            ⚠️ Please complete your <strong>Profile</strong> first to generate a personalized diet plan.
        </div>""", unsafe_allow_html=True)
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"""<div class='info-box'>
            ✅ Goal: <strong>{profile['goal']}</strong> |
            Target: <strong>{int(profile['daily_calories'])} kcal</strong> |
            Protein: <strong>{int(profile['protein_req'])}g</strong>
        </div>""", unsafe_allow_html=True)
    with col2:
        generate = st.button("🥗 Generate 7-Day Diet Plan", key="gen_diet")

    if generate:
        with st.spinner("🧠 AI is crafting your personalized Indian diet plan..."):
            plan = ai.generate_diet_plan(profile)
            st.session_state.diet_plan = plan

    if st.session_state.diet_plan:
        st.markdown("<div class='ai-output'>", unsafe_allow_html=True)
        st.markdown(st.session_state.diet_plan)
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button(
            label="⬇️ Download Diet Plan (TXT)",
            data=st.session_state.diet_plan,
            file_name="diet_plan_gnaneswar.txt",
            mime="text/plain"
        )


# ---------------------------------------------------------------------------
# Page: AI Workout Generator
# ---------------------------------------------------------------------------
def page_workout():
    st.markdown("<div class='section-header'>🏋️ AI Workout Generator</div>", unsafe_allow_html=True)
    profile = get_profile_dict()
    if not profile:
        st.markdown("""<div class='warning-box'>
            ⚠️ Please complete your <strong>Profile</strong> first.
        </div>""", unsafe_allow_html=True)
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"""<div class='info-box'>
            ✅ Goal: <strong>{profile['goal']}</strong> |
            Experience: <strong>{profile['experience']}</strong> |
            Gender: <strong>{profile['gender']}</strong>
        </div>""", unsafe_allow_html=True)
    with col2:
        generate = st.button("🏋️ Generate Workout Plan", key="gen_workout")

    if generate:
        with st.spinner("💪 AI is building your Push-Pull-Legs program..."):
            plan = ai.generate_workout_plan(profile)
            st.session_state.workout_plan = plan

    if st.session_state.workout_plan:
        st.markdown("<div class='ai-output'>", unsafe_allow_html=True)
        st.markdown(st.session_state.workout_plan)
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button(
            label="⬇️ Download Workout Plan (TXT)",
            data=st.session_state.workout_plan,
            file_name="workout_plan_gnaneswar.txt",
            mime="text/plain"
        )


# ---------------------------------------------------------------------------
# Page: AI Trainer Chat
# ---------------------------------------------------------------------------
def page_chat():
    st.markdown("<div class='section-header'>🤖 AI Trainer Chat</div>", unsafe_allow_html=True)
    profile = get_profile_dict()

    if not st.session_state.chat_loaded:
        db_history = db.get_chat_history(st.session_state.user_id, limit=20)
        st.session_state.chat_messages = [
            {"role": r["role"], "message": r["message"]} for r in db_history
        ]
        st.session_state.chat_loaded = True

    st.markdown("""<div class='info-box'>
        💬 Ask your AI trainer anything about fitness, nutrition, supplements, or training.
    </div>""", unsafe_allow_html=True)

    # Display history
    if not st.session_state.chat_messages:
        st.markdown("""
        <div style='text-align:center; padding:40px; color:#444;'>
            <div style='font-size:3rem;'>🤖</div>
            <div style='margin-top:12px;'>Start a conversation! Examples:</div>
            <div style='margin-top:8px; font-size:0.8rem; color:#555;'>
                "How to build chest?" • "Best foods for bulking?" • "Should I do cardio?"
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                st.markdown(f"""<div class='chat-user'>
                    <div class='chat-label'>👤 You</div>{msg['message']}</div>""",
                    unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class='chat-bot'>
                    <div class='chat-label'>🤖 AI Trainer</div>{msg['message']}</div>""",
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("Message", placeholder="Ask your trainer anything...",
                                   label_visibility="collapsed", key="chat_input")
    with col2:
        send = st.button("Send 💬", key="send_chat")

    col3, col4 = st.columns([3, 1])
    with col4:
        if st.button("🗑️ Clear Chat"):
            db.clear_chat_history(st.session_state.user_id)
            st.session_state.chat_messages = []
            st.rerun()

    if send and user_input.strip():
        db.save_chat(st.session_state.user_id, "user", user_input.strip())
        st.session_state.chat_messages.append({"role": "user", "message": user_input.strip()})
        with st.spinner("🤖 Trainer is thinking..."):
            response = ai.chat_with_trainer(
                user_input.strip(),
                st.session_state.chat_messages[-10:],
                profile
            )
        db.save_chat(st.session_state.user_id, "assistant", response)
        st.session_state.chat_messages.append({"role": "assistant", "message": response})
        st.rerun()


# ---------------------------------------------------------------------------
# Page: Progress Tracker
# ---------------------------------------------------------------------------
def page_progress():
    st.markdown("<div class='section-header'>📊 Progress Tracker</div>", unsafe_allow_html=True)
    profile = get_profile_dict()
    target_calories = profile.get("daily_calories") if profile else None

    st.markdown("#### 📝 Log Today's Progress")
    with st.form("progress_form"):
        col1, col2 = st.columns(2)
        with col1:
            log_date = st.date_input("Date", value=date.today())
            log_weight = st.number_input("Body Weight (kg)", min_value=20.0,
                                         max_value=300.0, step=0.1,
                                         value=profile.get("weight", 70.0) if profile else 70.0)
        with col2:
            log_calories = st.number_input("Calories Eaten (kcal)", min_value=0,
                                            max_value=10000, step=50,
                                            value=int(target_calories) if target_calories else 2000)
            workout_done = st.text_input("Workout Done", placeholder="e.g. Push Day — Chest & Triceps")
        notes = st.text_area("Notes (optional)", placeholder="How did you feel?", height=80)
        submitted = st.form_submit_button("💾 Log Progress")

    if submitted:
        db.log_progress(st.session_state.user_id, str(log_date),
                        log_weight, log_calories, workout_done, notes)
        st.success("✅ Progress logged successfully!")
        st.rerun()

    st.markdown("<hr style='border-color:rgba(255,107,53,0.2);margin:24px 0;'>", unsafe_allow_html=True)

    df = pt.get_progress_dataframe(st.session_state.user_id)
    if df.empty:
        st.markdown("""<div class='info-box'>
            📋 No progress data yet. Log your first entry above!
        </div>""", unsafe_allow_html=True)
        return

    st.markdown("#### 📈 Your Progress Charts")
    summary = pt.get_weekly_summary(df)
    if summary:
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>{summary.get('entries', 0)}</div>
                <div class='metric-label'>Entries (7 days)</div></div>""", unsafe_allow_html=True)
        with s2:
            w_change = summary.get("weight_change", 0) or 0
            color = "#2ECC40" if w_change < 0 else "#FF6B35" if w_change > 0 else "#9090AA"
            arrow = "↓" if w_change < 0 else "↑" if w_change > 0 else "→"
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value' style='color:{color};'>{arrow} {abs(w_change)} kg</div>
                <div class='metric-label'>Weight Change (7d)</div></div>""", unsafe_allow_html=True)
        with s3:
            avg_cal = summary.get("avg_calories", 0) or 0
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>{avg_cal:.0f}</div>
                <div class='metric-label'>Avg Calories/Day</div></div>""", unsafe_allow_html=True)
        with s4:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>{summary.get('workouts_done', 0)}</div>
                <div class='metric-label'>Workouts Logged</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    weight_fig = pt.plot_weight_progress(df)
    if weight_fig:
        st.plotly_chart(weight_fig, use_container_width=True)

    cal_fig = pt.plot_calorie_tracking(df, target_calories)
    if cal_fig:
        st.plotly_chart(cal_fig, use_container_width=True)

    with st.expander("📋 View Raw Progress Data"):
        st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True)


# ---------------------------------------------------------------------------
# Main router
# ---------------------------------------------------------------------------
def main():
    render_sidebar()
    page = st.session_state.current_page

    protected = ["👤 My Profile", "🥗 AI Diet Planner", "🏋️ AI Workout Generator",
                 "🤖 AI Trainer Chat", "📊 Progress Tracker"]

    if page in protected and not st.session_state.logged_in:
        st.warning("⚠️ Please login to access this page.")
        page_auth()
        return

    if page == "🏠 Home":
        page_home()
    elif page == "🔐 Login / Register":
        page_auth()
    elif page == "👤 My Profile":
        page_profile()
    elif page == "🥗 AI Diet Planner":
        page_diet()
    elif page == "🏋️ AI Workout Generator":
        page_workout()
    elif page == "🤖 AI Trainer Chat":
        page_chat()
    elif page == "📊 Progress Tracker":
        page_progress()


if __name__ == "__main__":
    main()
