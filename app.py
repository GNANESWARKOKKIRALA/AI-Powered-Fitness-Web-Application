"""
app.py - Main Streamlit application entry point
Run with: streamlit run app.py
"""
import streamlit as st
from config import APP_TITLE, APP_ICON
from database import initialise_database
from auth import register_user, login_user
from workout import show_workout_page, calculate_bmi, calculate_bmr, calculate_tdee, calorie_target, protein_target
from diet import show_diet_page
from progress import show_progress_page
from ai_engine import chat_with_trainer

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── One-time DB setup ──────────────────────────────────────────────────────────
if "db_ready" not in st.session_state:
    ok, msg = initialise_database()
    st.session_state["db_ready"] = ok
    if not ok:
        st.error(f"⚠️ Database connection failed: {msg}")
        st.info("Check your .env file and make sure SQL Server Express is running.")
        st.stop()

# ── Session defaults ───────────────────────────────────────────────────────────
if "user"          not in st.session_state: st.session_state["user"]          = None
if "chat_history"  not in st.session_state: st.session_state["chat_history"]  = []
if "user_stats"    not in st.session_state: st.session_state["user_stats"]    = {}

user = st.session_state["user"]


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"## {APP_ICON} {APP_TITLE}")
    st.markdown("---")

    if user:
        st.success(f"👋 Welcome, **{user['name']}**!")
        st.markdown(f"📧 {user['email']}")
        st.markdown("---")
        page = st.radio(
            "Navigate",
            ["🏠 Home", "📊 Dashboard", "🏋️ Workout Generator",
             "🥗 Diet Planner", "🤖 Chat Trainer", "📈 Progress Tracker"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["user"]         = None
            st.session_state["chat_history"] = []
            st.session_state["user_stats"]   = {}
            st.rerun()
    else:
        page = st.radio(
            "Navigate",
            ["🏠 Home", "🔐 Login / Register"],
            label_visibility="collapsed",
        )


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE ROUTING
# ══════════════════════════════════════════════════════════════════════════════

# ── HOME ──────────────────────────────────────────────────────────────────────
if page == "🏠 Home":
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.subheader("Your AI-Powered Personal Gym Trainer & Nutrition Coach")

    col1, col2, col3 = st.columns(3)
    col1.info("### 🏋️ AI Workout Plans\nMultiple splits: PPL, Bro, Arnold, Strength & more")
    col2.info("### 🥗 Indian Diet Plans\n7-day personalised meal plans using Indian foods")
    col3.info("### 🤖 AI Chat Trainer\nAsk anything – workouts, diet, supplements & tips")

    col4, col5, col6 = st.columns(3)
    col4.success("### 📊 Progress Tracking\nLog weight daily and visualise your journey")
    col5.success("### 🧮 Body Calculations\nBMI, BMR, TDEE & protein targets")
    col6.success("### 🔐 Secure & Private\nHashed passwords & parameterised queries")

    st.markdown("---")
    st.markdown("👉 **Register or Login** from the sidebar to get started!")

    if not user:
        st.warning("You are not logged in. Please login or register first.")


# ── LOGIN / REGISTER ─────────────────────────────────────────────────────────
elif page == "🔐 Login / Register":
    st.title("🔐 Login / Register")
    tab_login, tab_reg = st.tabs(["🔑 Login", "📝 Register"])

    # Login tab
    with tab_login:
        st.subheader("Welcome Back!")
        with st.form("login_form"):
            email    = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login", use_container_width=True)

        if login_btn:
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                u, err = login_user(email, password)
                if err:
                    st.error(err)
                else:
                    st.session_state["user"] = u
                    st.success(f"Welcome back, {u['name']}! 🎉")
                    st.rerun()

    # Register tab
    with tab_reg:
        st.subheader("Create Your Account")
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                r_name   = st.text_input("Full Name")
                r_email  = st.text_input("Email Address")
                r_pass   = st.text_input("Password", type="password")
            with col2:
                r_pass2  = st.text_input("Confirm Password", type="password")
                r_age    = st.number_input("Age", 10, 90, 25)
                r_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            reg_btn = st.form_submit_button("Create Account", use_container_width=True)

        if reg_btn:
            if not all([r_name, r_email, r_pass, r_pass2]):
                st.error("Please fill in all fields.")
            elif r_pass != r_pass2:
                st.error("Passwords do not match.")
            elif len(r_pass) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                ok, msg = register_user(r_name, r_email, r_pass, r_age, r_gender)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)


# ── PROTECTED PAGES ───────────────────────────────────────────────────────────
elif not user:
    st.warning("⚠️ Please login to access this page.")
    st.stop()


# ── DASHBOARD ─────────────────────────────────────────────────────────────────
elif page == "📊 Dashboard":
    st.title(f"📊 Dashboard – Welcome, {user['name']}!")

    col1, col2, col3 = st.columns(3)
    col1.metric("Name",   user["name"])
    col2.metric("Age",    f"{user['age']} yrs")
    col3.metric("Gender", user["gender"])

    stats = st.session_state.get("user_stats", {})
    if stats:
        st.markdown("---")
        st.subheader("Your Latest Fitness Stats")
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("BMI",           f"{stats.get('bmi', '-')}")
        s2.metric("BMR",           f"{int(stats.get('bmr', 0))} kcal")
        s3.metric("Daily Calories",f"{int(stats.get('calories', 0))} kcal")
        s4.metric("Goal",          stats.get("goal", "-"))
    else:
        st.info("👆 Complete the Workout Generator to see your body stats here.")

    st.markdown("---")
    st.subheader("Quick Actions")
    qc1, qc2, qc3 = st.columns(3)
    qc1.success("🏋️ Go to **Workout Generator** in the sidebar")
    qc2.success("🥗 Go to **Diet Planner** in the sidebar")
    qc3.success("📈 Go to **Progress Tracker** in the sidebar")


# ── WORKOUT GENERATOR ─────────────────────────────────────────────────────────
elif page == "🏋️ Workout Generator":
    show_workout_page(user)


# ── DIET PLANNER ──────────────────────────────────────────────────────────────
elif page == "🥗 Diet Planner":
    show_diet_page(user)


# ── CHAT TRAINER ──────────────────────────────────────────────────────────────
elif page == "🤖 Chat Trainer":
    st.title("🤖 AI Chat Trainer")
    st.markdown("Ask me anything about **workouts, diet, supplements, recovery** and more!")

    # Display history
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # New message
    prompt = st.chat_input("Ask your fitness question…")
    if prompt:
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                # Pass history without the latest message (already added)
                reply = chat_with_trainer(
                    st.session_state["chat_history"][:-1], prompt
                )
            st.markdown(reply)

        st.session_state["chat_history"].append({"role": "assistant", "content": reply})

    if st.session_state["chat_history"]:
        if st.button("🗑️ Clear Chat"):
            st.session_state["chat_history"] = []
            st.rerun()


# ── PROGRESS TRACKER ──────────────────────────────────────────────────────────
elif page == "📈 Progress Tracker":
    show_progress_page(user)
