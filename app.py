import streamlit as st
from database import init_db, save_profile, get_profile, save_progress, save_chat_message, get_chat_history
from auth import register_user, login_user
from fitness_calc import get_all_calculations
from ai_engine import generate_diet_plan, generate_workout_plan, chat_with_trainer
from progress_tracker import get_progress_charts
from datetime import date

# ─── PAGE CONFIG ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Gnaneswar Fitness AI",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── INIT DB ─────────────────────────────────────────────────────
init_db()

# ─── GLOBAL CSS — Dark Orange Animated Theme ─────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');

/* ── Base ── */
* { font-family: 'Rajdhani', sans-serif !important; }
.stApp { background: #050810 !important; }

/* ── Grid background ── */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(255,107,53,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,107,53,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1525 0%, #050810 100%) !important;
    border-right: 1px solid rgba(255,107,53,0.2) !important;
}
[data-testid="stSidebar"] * { color: #E0E0E0 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #FF6B35, #E55A20) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    letter-spacing: 1px !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(255,107,53,0.3) !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(255,107,53,0.5) !important;
    background: linear-gradient(135deg, #FF8C5A, #FF6B35) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > div,
.stTextArea > div > div > textarea {
    background: #0D1525 !important;
    border: 1px solid rgba(255,107,53,0.3) !important;
    border-radius: 8px !important;
    color: white !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #FF6B35 !important;
    box-shadow: 0 0 10px rgba(255,107,53,0.3) !important;
}

/* ── Labels ── */
label, .stSelectbox label, .stTextInput label,
.stNumberInput label, p, .stMarkdown p {
    color: #E0E0E0 !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(255,107,53,0.1), rgba(255,107,53,0.05)) !important;
    border: 1px solid rgba(255,107,53,0.3) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
[data-testid="metric-container"] label { color: #888 !important; }
[data-testid="metric-container"] [data-testid="metric-value"] {
    color: #FF6B35 !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}

/* ── Success / Error ── */
.stSuccess { background: rgba(46,204,113,0.1) !important; border-left: 4px solid #2ECC71 !important; }
.stError   { background: rgba(231,76,60,0.1)  !important; border-left: 4px solid #E74C3C  !important; }
.stInfo    { background: rgba(52,152,219,0.1) !important; border-left: 4px solid #3498DB  !important; }
.stWarning { background: rgba(243,156,18,0.1) !important; border-left: 4px solid #F39C18  !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #FF6B35 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #050810; }
::-webkit-scrollbar-thumb { background: #FF6B35; border-radius: 3px; }

/* ── Animations ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.6; }
}
@keyframes glow {
    0%, 100% { text-shadow: 0 0 10px rgba(255,107,53,0.5); }
    50%       { text-shadow: 0 0 30px rgba(255,107,53,0.9), 0 0 60px rgba(255,107,53,0.5); }
}
@keyframes slideIn {
    from { opacity: 0; transform: translateX(-20px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes spin {
    0%   { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>
""", unsafe_allow_html=True)


# ─── HELPER: HTML COMPONENTS ─────────────────────────────────────

def hero_title(title, subtitle=""):
    st.markdown(f"""
    <div style="text-align:center; padding: 2rem 0 1rem 0;
                animation: fadeInUp 0.8s ease;">
        <h1 style="font-family:'Orbitron',monospace; font-size:2.8rem;
                   font-weight:900; color:#FF6B35; letter-spacing:3px;
                   text-transform:uppercase; animation: glow 3s ease infinite;
                   text-shadow: 0 0 20px rgba(255,107,53,0.5);">
            {title}
        </h1>
        {"<p style='color:#888; font-size:1.1rem; letter-spacing:2px; margin-top:0.5rem;'>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def section_header(text, icon=""):
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px;
                margin: 1.5rem 0 1rem 0; animation: slideIn 0.5s ease;">
        <div style="width:4px; height:28px; background:#FF6B35;
                    border-radius:2px; box-shadow: 0 0 10px rgba(255,107,53,0.5);"></div>
        <h2 style="color:#FF6B35; font-size:1.4rem; font-weight:700;
                   margin:0; letter-spacing:1px;">{icon} {text}</h2>
    </div>
    """, unsafe_allow_html=True)


def info_card(title, value, icon="", color="#FF6B35"):
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255,107,53,0.08), rgba(255,107,53,0.02));
                border: 1px solid rgba(255,107,53,0.25); border-radius:12px;
                padding:1.2rem; text-align:center; margin:0.3rem 0;
                animation: fadeInUp 0.5s ease;
                transition: transform 0.3s, box-shadow 0.3s;"
         onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 25px rgba(255,107,53,0.2)'"
         onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none'">
        <div style="font-size:1.8rem;">{icon}</div>
        <div style="font-size:1.6rem; font-weight:700; color:{color}; margin:0.3rem 0;">{value}</div>
        <div style="font-size:0.85rem; color:#888; letter-spacing:1px;">{title}</div>
    </div>
    """, unsafe_allow_html=True)


def chat_bubble(role, message):
    is_user = role == "user"
    align = "flex-end" if is_user else "flex-start"
    bg = "linear-gradient(135deg, #FF6B35, #E55A20)" if is_user else "linear-gradient(135deg, #1E2761, #0D1525)"
    border = "none" if is_user else "1px solid rgba(255,107,53,0.3)"
    label = "👤 You" if is_user else "🤖 AI Trainer"
    st.markdown(f"""
    <div style="display:flex; justify-content:{align}; margin:0.5rem 0;
                animation: fadeInUp 0.3s ease;">
        <div style="max-width:75%; background:{bg}; border:{border};
                    border-radius:12px; padding:0.8rem 1rem;">
            <div style="font-size:0.75rem; color:rgba(255,255,255,0.6);
                        margin-bottom:0.3rem; font-weight:600;">{label}</div>
            <div style="color:white; font-size:0.95rem; line-height:1.5;">{message}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── SESSION STATE ────────────────────────────────────────────────
if 'user_id'   not in st.session_state: st.session_state.user_id   = None
if 'user_name' not in st.session_state: st.session_state.user_name = None
if 'page'      not in st.session_state: st.session_state.page      = 'Home'


# ─── SIDEBAR ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:1rem 0;">
        <div style="font-size:3rem; animation: pulse 2s infinite;">💪</div>
        <div style="font-family:'Orbitron',monospace; font-size:1rem;
                    font-weight:900; color:#FF6B35; letter-spacing:2px;
                    margin-top:0.5rem;">GNANESWAR</div>
        <div style="font-family:'Orbitron',monospace; font-size:0.7rem;
                    color:#888; letter-spacing:3px;">FITNESS AI</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.user_id:
        st.markdown(f"""
        <div style="background:rgba(255,107,53,0.1); border:1px solid rgba(255,107,53,0.3);
                    border-radius:8px; padding:0.8rem; text-align:center; margin-bottom:1rem;">
            <div style="font-size:1.5rem;">👋</div>
            <div style="color:#FF6B35; font-weight:700; font-size:1rem;">
                {st.session_state.user_name}
            </div>
            <div style="color:#888; font-size:0.75rem;">Logged In ✅</div>
        </div>
        """, unsafe_allow_html=True)

        pages = ["🏠 Home", "👤 My Profile", "🥗 Diet Plan",
                 "🏋️ Workout", "🤖 AI Trainer", "📈 Progress"]
        page_map = {
            "🏠 Home": "Home", "👤 My Profile": "Profile",
            "🥗 Diet Plan": "Diet", "🏋️ Workout": "Workout",
            "🤖 AI Trainer": "Chat", "📈 Progress": "Progress"
        }
        selected = st.radio("Navigate", pages, label_visibility="collapsed")
        st.session_state.page = page_map[selected]

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_id   = None
            st.session_state.user_name = None
            st.session_state.page      = "Home"
            st.rerun()
    else:
        pages = ["🏠 Home", "🔐 Login", "📝 Register"]
        page_map = {"🏠 Home": "Home", "🔐 Login": "Login", "📝 Register": "Register"}
        selected = st.radio("Navigate", pages, label_visibility="collapsed")
        st.session_state.page = page_map[selected]


# ════════════════════════════════════════════════════════════════
# PAGE: HOME
# ════════════════════════════════════════════════════════════════
if st.session_state.page == "Home":
    hero_title("GNANESWAR FITNESS AI", "AI-Powered Personal Fitness Assistant")

    st.markdown("""
    <div style="text-align:center; max-width:700px; margin:0 auto 2rem auto;
                color:#888; font-size:1.05rem; line-height:1.7;
                animation: fadeInUp 1s ease;">
        Get personalized diet plans, workout programs, and real-time fitness
        coaching powered by <span style="color:#FF6B35; font-weight:700;">
        LLaMA 3.1</span> — 8 Billion parameter AI by Meta, accessed via
        <span style="color:#FF6B35; font-weight:700;">Groq API</span>.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    features = [
        ("🔐", "Secure Login", "bcrypt password hashing"),
        ("🧮", "BMI & BMR", "Mifflin-St Jeor formula"),
        ("🥗", "AI Diet Plan", "7-day Indian meal plan"),
        ("🏋️", "AI Workout", "Push Pull Legs program"),
        ("🤖", "AI Chatbot", "Personal trainer chat"),
        ("📈", "Progress", "Plotly chart tracking"),
    ]
    cols = st.columns(6)
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(f"""
            <div style="background:rgba(255,107,53,0.05); border:1px solid rgba(255,107,53,0.2);
                        border-radius:10px; padding:1rem; text-align:center;
                        animation: fadeInUp 0.8s ease;
                        transition: all 0.3s ease; cursor:pointer;"
                 onmouseover="this.style.background='rgba(255,107,53,0.12)';this.style.transform='translateY(-5px)'"
                 onmouseout="this.style.background='rgba(255,107,53,0.05)';this.style.transform='translateY(0)'">
                <div style="font-size:2rem; margin-bottom:0.5rem;">{icon}</div>
                <div style="color:#FF6B35; font-weight:700; font-size:0.9rem;">{title}</div>
                <div style="color:#666; font-size:0.75rem; margin-top:0.3rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    if not st.session_state.user_id:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2, 1, 2])
        with c2:
            if st.button("🚀 GET STARTED", use_container_width=True):
                st.session_state.page = "Register"
                st.rerun()


# ════════════════════════════════════════════════════════════════
# PAGE: LOGIN
# ════════════════════════════════════════════════════════════════
elif st.session_state.page == "Login":
    hero_title("WELCOME BACK", "Login to your account")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background:linear-gradient(135deg, rgba(255,107,53,0.08), rgba(255,107,53,0.02));
                    border:1px solid rgba(255,107,53,0.25); border-radius:16px;
                    padding:2rem; animation: fadeInUp 0.6s ease;">
        """, unsafe_allow_html=True)

        st.markdown("<div style='text-align:center; font-size:3rem;'>🔐</div>", unsafe_allow_html=True)

        with st.form("login_form"):
            email    = st.text_input("📧 Email Address", placeholder="your@email.com")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter password")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🚀 LOGIN", use_container_width=True)

        if submitted:
            if email and password:
                with st.spinner("🔄 Authenticating..."):
                    success, user, msg = login_user(email, password)
                if success:
                    st.session_state.user_id   = user['id']
                    st.session_state.user_name = user['name']
                    st.success(f"✅ Welcome back, {user['name']}!")
                    st.balloons()
                    import time; time.sleep(1)
                    st.session_state.page = "Home"
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
            else:
                st.warning("⚠️ Please fill all fields!")

        st.markdown("""
        <div style="text-align:center; color:#888; margin-top:1rem; font-size:0.9rem;">
            Don't have an account?
            <span style="color:#FF6B35; font-weight:700;">Register →</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# PAGE: REGISTER
# ════════════════════════════════════════════════════════════════
elif st.session_state.page == "Register":
    hero_title("CREATE ACCOUNT", "Join Gnaneswar Fitness AI")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background:linear-gradient(135deg, rgba(255,107,53,0.08), rgba(255,107,53,0.02));
                    border:1px solid rgba(255,107,53,0.25); border-radius:16px;
                    padding:2rem; animation: fadeInUp 0.6s ease;">
        """, unsafe_allow_html=True)

        st.markdown("<div style='text-align:center; font-size:3rem;'>📝</div>", unsafe_allow_html=True)

        with st.form("register_form"):
            name     = st.text_input("👤 Full Name",      placeholder="Your full name")
            email    = st.text_input("📧 Email Address",  placeholder="your@email.com")
            password = st.text_input("🔑 Password",       type="password", placeholder="Min 6 characters")
            confirm  = st.text_input("🔑 Confirm Password", type="password", placeholder="Repeat password")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("✨ CREATE ACCOUNT", use_container_width=True)

        if submitted:
            if name and email and password and confirm:
                if password != confirm:
                    st.error("❌ Passwords do not match!")
                else:
                    with st.spinner("⚙️ Creating your account..."):
                        success, msg = register_user(name, email, password)
                    if success:
                        st.success(f"🎉 {msg} Please login!")
                        st.balloons()
                    else:
                        st.error(f"❌ {msg}")
            else:
                st.warning("⚠️ Please fill all fields!")

        st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# CHECK LOGIN FOR PROTECTED PAGES
# ════════════════════════════════════════════════════════════════
elif not st.session_state.user_id:
    st.warning("⚠️ Please login first!")
    if st.button("🔐 Go to Login"):
        st.session_state.page = "Login"
        st.rerun()


# ════════════════════════════════════════════════════════════════
# PAGE: PROFILE
# ════════════════════════════════════════════════════════════════
elif st.session_state.page == "Profile":
    hero_title("MY PROFILE", "Your fitness details and calculations")
    section_header("Fitness Profile", "👤")

    existing = get_profile(st.session_state.user_id)

    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            age    = st.number_input("🎂 Age",    min_value=10, max_value=100, value=int(existing['age']) if existing else 22)
            weight = st.number_input("⚖️ Weight (kg)", min_value=30.0, max_value=300.0, value=float(existing['weight']) if existing else 70.0, step=0.5)
            goal   = st.selectbox("🎯 Goal", ["Bulking (Gain Muscle)", "Cutting (Lose Fat)", "Maintain Weight"],
                                  index=["Bulking (Gain Muscle)", "Cutting (Lose Fat)", "Maintain Weight"].index(existing['goal']) if existing else 0)
            activity = st.selectbox("🏃 Activity Level",
                ["Sedentary (No exercise)", "Lightly Active (1-3 days/week)",
                 "Moderately Active (3-5 days/week)", "Very Active (6-7 days/week)", "Extra Active (Physical job)"])
        with c2:
            gender = st.selectbox("⚤ Gender", ["Male", "Female"],
                                  index=0 if not existing or existing['gender'] == 'Male' else 1)
            height = st.number_input("📏 Height (cm)", min_value=100.0, max_value=250.0, value=float(existing['height']) if existing else 170.0, step=0.5)
            experience = st.selectbox("🏆 Experience", ["Beginner", "Intermediate", "Advanced"],
                                      index=["Beginner", "Intermediate", "Advanced"].index(existing['experience']) if existing else 0)

        submitted = st.form_submit_button("💾 SAVE PROFILE", use_container_width=True)

    if submitted:
        with st.spinner("⚙️ Calculating your fitness data..."):
            calcs = get_all_calculations(weight, height, age, gender, activity, goal, experience)
            save_profile(st.session_state.user_id, age, gender, height, weight,
                         goal, experience, activity,
                         calcs['bmi'], calcs['bmr'],
                         calcs['daily_calories'], calcs['protein_req'])
        st.success("✅ Profile saved successfully!")

        section_header("Your Fitness Results", "🧮")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("BMI", f"{calcs['bmi']}", calcs['bmi_category'])
        with c2: st.metric("BMR", f"{calcs['bmr']} kcal", "Daily Base Calories")
        with c3: st.metric("Daily Calories", f"{calcs['daily_calories']} kcal", goal)
        with c4: st.metric("Protein Target", f"{calcs['protein_req']}g", "Per Day")


# ════════════════════════════════════════════════════════════════
# PAGE: DIET PLAN
# ════════════════════════════════════════════════════════════════
elif st.session_state.page == "Diet":
    hero_title("AI DIET PLANNER", "Personalized 7-Day Indian Diet Plan")
    profile = get_profile(st.session_state.user_id)
    if not profile:
        st.warning("⚠️ Please create your profile first!")
    else:
        section_header("Your Diet Stats", "🧮")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Daily Calories", f"{profile['daily_calories']} kcal")
        with c2: st.metric("Protein Target", f"{profile['protein_req']}g/day")
        with c3: st.metric("Goal", profile['goal'])

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🥗 GENERATE MY DIET PLAN", use_container_width=True):
            with st.spinner("🤖 LLaMA 3.1 is creating your personalized diet plan..."):
                plan = generate_diet_plan(profile, st.session_state.user_name)
            section_header("Your 7-Day Diet Plan", "🥗")
            st.markdown(f"""
            <div style="background:rgba(255,107,53,0.05); border:1px solid rgba(255,107,53,0.2);
                        border-radius:12px; padding:1.5rem; white-space:pre-wrap;
                        color:#E0E0E0; line-height:1.8; font-size:0.95rem;
                        animation: fadeInUp 0.5s ease;">
                {plan}
            </div>
            """, unsafe_allow_html=True)
            st.download_button("📥 Download Diet Plan", plan,
                               file_name="my_diet_plan.txt", use_container_width=True)


# ════════════════════════════════════════════════════════════════
# PAGE: WORKOUT
# ════════════════════════════════════════════════════════════════
elif st.session_state.page == "Workout":
    hero_title("AI WORKOUT GENERATOR", "Push Pull Legs 6-Day Program")
    profile = get_profile(st.session_state.user_id)
    if not profile:
        st.warning("⚠️ Please create your profile first!")
    else:
        section_header("Your Training Stats", "🏋️")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Experience", profile['experience'])
        with c2: st.metric("Goal",       profile['goal'])
        with c3: st.metric("Weight",     f"{profile['weight']} kg")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏋️ GENERATE MY WORKOUT", use_container_width=True):
            with st.spinner("🤖 LLaMA 3.1 is building your workout program..."):
                workout = generate_workout_plan(profile, st.session_state.user_name)
            section_header("Your 6-Day Workout Plan", "🏋️")
            st.markdown(f"""
            <div style="background:rgba(255,107,53,0.05); border:1px solid rgba(255,107,53,0.2);
                        border-radius:12px; padding:1.5rem; white-space:pre-wrap;
                        color:#E0E0E0; line-height:1.8; font-size:0.95rem;
                        animation: fadeInUp 0.5s ease;">
                {workout}
            </div>
            """, unsafe_allow_html=True)
            st.download_button("📥 Download Workout Plan", workout,
                               file_name="my_workout_plan.txt", use_container_width=True)


# ════════════════════════════════════════════════════════════════
# PAGE: AI TRAINER CHAT
# ════════════════════════════════════════════════════════════════
elif st.session_state.page == "Chat":
    hero_title("AI TRAINER CHAT", "Your Personal Fitness Coach")
    profile = get_profile(st.session_state.user_id)
    if not profile:
        st.warning("⚠️ Please create your profile first!")
    else:
        history = get_chat_history(st.session_state.user_id, limit=20)
        section_header("Conversation", "💬")

        if not history:
            st.markdown("""
            <div style="text-align:center; padding:2rem; color:#888;">
                <div style="font-size:3rem; margin-bottom:1rem;">🤖</div>
                <div>Start chatting with your AI trainer!</div>
                <div style="font-size:0.85rem; margin-top:0.5rem;">
                    Ask about diet, workout, supplements, or anything fitness!
                </div>
            </div>
            """, unsafe_allow_html=True)

        for msg in history:
            chat_bubble(msg['role'], msg['message'])

        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("💬 Ask your AI trainer...",
                                        placeholder="e.g. What should I eat after workout?")
            submitted = st.form_submit_button("📤 SEND", use_container_width=True)

        if submitted and user_input:
            save_chat_message(st.session_state.user_id, "user", user_input)
            with st.spinner("🤖 AI Trainer is thinking..."):
                response = chat_with_trainer(
                    user_input, profile,
                    st.session_state.user_name, history
                )
            save_chat_message(st.session_state.user_id, "assistant", response)
            st.rerun()


# ════════════════════════════════════════════════════════════════
# PAGE: PROGRESS TRACKER
# ════════════════════════════════════════════════════════════════
elif st.session_state.page == "Progress":
    hero_title("PROGRESS TRACKER", "Track your fitness journey")
    profile = get_profile(st.session_state.user_id)
    if not profile:
        st.warning("⚠️ Please create your profile first!")
    else:
        section_header("Log Today", "📝")
        with st.form("progress_form"):
            c1, c2, c3 = st.columns(3)
            with c1: log_date    = st.date_input("📅 Date", value=date.today())
            with c2: log_weight  = st.number_input("⚖️ Weight (kg)", min_value=30.0, max_value=300.0,
                                                    value=float(profile['weight']), step=0.1)
            with c3: log_cal     = st.number_input("🔥 Calories Eaten", min_value=0.0,
                                                    value=float(profile['daily_calories']), step=50.0)
            workout_done = st.checkbox("✅ Completed workout today?")
            notes        = st.text_area("📝 Notes (optional)", placeholder="How did you feel today?", height=80)
            submitted    = st.form_submit_button("💾 SAVE TODAY'S LOG", use_container_width=True)

        if submitted:
            save_progress(st.session_state.user_id, log_date, log_weight,
                          log_cal, workout_done, notes)
            st.success("✅ Progress logged successfully!")
            st.rerun()

        section_header("Progress Charts", "📈")
        fig_w, fig_c, stats = get_progress_charts(
            st.session_state.user_id, profile['daily_calories']
        )

        if stats:
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Total Days Logged", stats['total_days'])
            with c2: st.metric("Current Weight",    f"{stats['latest_weight']} kg",
                               f"{stats['weight_change']:+.1f} kg")
            with c3: st.metric("Avg Calories",      f"{stats['avg_calories']} kcal")
            with c4: st.metric("Workouts Done",     stats['workouts_done'])

            st.plotly_chart(fig_w, use_container_width=True)
            st.plotly_chart(fig_c, use_container_width=True)
        else:
            st.info("📊 Log some progress entries to see your charts!")
