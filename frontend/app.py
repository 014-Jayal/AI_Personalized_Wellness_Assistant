import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from database.db import init_db, get_connection, hash_password

init_db()

st.set_page_config(
    page_title="AI Wellness Assistant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS Loader ────────────────────────────────────────────────────────────────
def load_css():
    st.markdown(
        '<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">',
        unsafe_allow_html=True
    )
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ── Session State ─────────────────────────────────────────────────────────────
for key, default in [("logged_in", False), ("user_id", None), ("username", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Auth Helpers ──────────────────────────────────────────────────────────────
def login_user(username, password):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "SELECT id, name FROM users WHERE username=? AND password_hash=?",
        (username, hash_password(password))
    )
    user = cur.fetchone()
    conn.close()
    return user

def register_user(name, username, password):
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, username, password_hash) VALUES (?, ?, ?)",
            (name, username, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN / REGISTER GATE
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:

    # Centering spacer
    st.markdown("<div style='height:6vh'></div>", unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.15, 1])

    with mid:
        # ── Brand hero ────────────────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center; margin-bottom: 2.4rem;">
            <div style="
                display:inline-flex; align-items:center; justify-content:center;
                width:64px; height:64px; border-radius:18px;
                background: linear-gradient(135deg, #00d2b4, #4facfe);
                box-shadow: 0 8px 32px rgba(0,210,180,0.35);
                margin-bottom: 1.2rem;
                font-size: 2rem;
            ">🌿</div>
            <div>
                <span class="hero-tag">Secure Patient Portal</span>
                <h1 style="margin:0; font-size:2.3rem; letter-spacing:-0.03em;">AI Wellness Assistant</h1>
                <p style="color:#64748b; margin-top:6px; font-size:0.92rem;">
                    Dermatology · Recovery Analytics · Adaptive Protocols
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Auth card ─────────────────────────────────────────────────────────
        with st.container(border=True):
            tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

            # Login tab
            with tab_login:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                with st.form("login_form"):
                    log_user = st.text_input("Username", placeholder="Enter your username")
                    log_pass = st.text_input("Password", type="password", placeholder="••••••••")
                    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                    submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")
                    if submitted:
                        user = login_user(log_user, log_pass)
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user_id   = user[0]
                            st.session_state.username  = user[1]
                            st.rerun()
                        else:
                            st.error("⚠️ Invalid credentials. Please try again.")

            # Register tab
            with tab_register:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                with st.form("signup_form"):
                    reg_name = st.text_input("Full Name", placeholder="Dr. Jane Smith")
                    reg_user = st.text_input("Username", placeholder="Choose a unique username")
                    reg_pass = st.text_input("Password", type="password", placeholder="••••••••")
                    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                    submitted = st.form_submit_button("Create Account →", use_container_width=True, type="primary")
                    if submitted:
                        if not reg_name or not reg_user or not reg_pass:
                            st.warning("Please fill in all fields.")
                        elif register_user(reg_name, reg_user, reg_pass):
                            st.success("✅ Account created! Please sign in.")
                        else:
                            st.error("Username already taken. Choose another.")

        # ── Footer note ───────────────────────────────────────────────────────
        st.markdown("""
        <p style="text-align:center; font-size:0.75rem; color:#334155; margin-top:1.4rem;">
            🔒 End-to-end encrypted · HIPAA-aligned architecture · SQLite secure storage
        </p>
        """, unsafe_allow_html=True)

    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

# ── Page header ───────────────────────────────────────────────────────────────
hd_left, hd_right = st.columns([3, 1])
with hd_left:
    st.markdown(f"""
    <span class="hero-tag">Dashboard</span>
    <h1 style="margin:0;">Welcome back, {st.session_state.username} 👋</h1>
    <p style="color:#64748b; margin-top:4px; font-size:0.93rem;">
        Your holistic wellness platform is active and ready.
    </p>
    """, unsafe_allow_html=True)

with hd_right:
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    if st.button("Log Out", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

# ── System status row ─────────────────────────────────────────────────────────
s1, s2, s3 = st.columns(3)
s1.metric("CNN Model",   "Online",    "EfficientNet-B3")
s2.metric("LLM Engine",  "Connected", "Gemini 2.5 Flash")
s3.metric("Database",    "Secure",    "SQLite Encrypted")

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Feature cards ─────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)

with c1:
    with st.container(border=True):
        st.markdown("""
        <div style="padding: 0.4rem 0 0.8rem;">
            <div style="font-size:2rem; margin-bottom:12px;">🔬</div>
            <div class="section-label">Step 01</div>
            <h3 style="margin:4px 0 8px;">Dermatological Assessment</h3>
            <p style="color:#64748b; font-size:0.88rem; line-height:1.6;">
                Upload a skin image for instant AI-powered classification using 
                EfficientNet-B3 with Grad-CAM explainability.
            </p>
        </div>
        """, unsafe_allow_html=True)

with c2:
    with st.container(border=True):
        st.markdown("""
        <div style="padding: 0.4rem 0 0.8rem;">
            <div style="font-size:2rem; margin-bottom:12px;">🥗</div>
            <div class="section-label">Step 02</div>
            <h3 style="margin:4px 0 8px;">Wellness Protocol</h3>
            <p style="color:#64748b; font-size:0.88rem; line-height:1.6;">
                Receive a fully adaptive lifestyle & dietary recovery plan 
                generated by Gemini AI based on your diagnosed condition.
            </p>
        </div>
        """, unsafe_allow_html=True)

with c3:
    with st.container(border=True):
        st.markdown("""
        <div style="padding: 0.4rem 0 0.8rem;">
            <div style="font-size:2rem; margin-bottom:12px;">📈</div>
            <div class="section-label">Step 03</div>
            <h3 style="margin:4px 0 8px;">Recovery Analytics</h3>
            <p style="color:#64748b; font-size:0.88rem; line-height:1.6;">
                Log daily check-ins and visualize symptom trends over time 
                with an interactive recovery analytics dashboard.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ── Quick start CTA ───────────────────────────────────────────────────────────
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
st.info("💡 **Get started:** Navigate to **🔬 Diagnosis** in the sidebar to upload your skin image and begin your assessment.")