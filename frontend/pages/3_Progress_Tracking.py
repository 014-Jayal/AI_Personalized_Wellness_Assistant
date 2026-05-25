import os
import streamlit as st
import pandas as pd
from streamlit_lottie import st_lottie
import requests
import datetime
import altair as alt

st.set_page_config(page_title="📈 Progress Tracking", layout="wide")

def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# Load CSS dynamically to prevent Path errors
base_dir = os.path.dirname(__file__)
css_path = os.path.abspath(os.path.join(base_dir, "../assets/style.css"))
if not os.path.exists(css_path):
    css_path = os.path.abspath(os.path.join(base_dir, "../../assets/style.css"))
load_css(css_path)

lottie_progress = load_lottieurl("https://lottie.host/9f35120a-328b-49f0-9851-12b8c74c7a15/2m2tCwKPVv.json")
lottie_trophy = load_lottieurl("https://lottie.host/17e231eb-fdfb-4cd7-b2eb-ba9ce4b25e79/Pz7q5hUf8q.json")

st.title("📈 Progress Tracking")
st.write("Automatically compares your diagnostic history to track your recovery.")

# Initialize the gamified streak and logging history
if "progress_history" not in st.session_state:
    st.session_state.progress_history = []
if "streak" not in st.session_state:
    st.session_state.streak = 0

# --- GUARDRAIL: Check if we have enough scans ---
if 'scan_history' not in st.session_state or len(st.session_state.scan_history) < 2:
    st.warning("⚠️ Insufficient Scans for Progression Tracking")
    st.info("Please go to the Diagnosis module and perform at least two separate image scans to unlock visual progression comparisons.")
    if st.button("🏥 Go to Diagnosis", type="primary"):
        # FIXED: Removed emojis from the file path
        st.switch_page("pages/1_Diagnosis.py")
    
    colA, colB = st.columns([1, 1])
    with colA:
        if lottie_progress:
            st_lottie(lottie_progress, height=350, key="progress_lottie")
    st.stop()

# --- AUTOMATED DATA EXTRACTION ---
col1, col2 = st.columns([1.4, 1])

with col1:
    st.subheader("📸 Automated Scan Comparison")
    
    history = st.session_state.scan_history
    options = [f"Scan: {s['date']} ({s['condition']} - Sev: {s['severity']}%)" for s in history]
    
    # Dropdowns default to comparing the very first scan vs the most recent scan
    c1, c2 = st.columns(2)
    with c1:
        idx1 = st.selectbox("Baseline (Initial) Scan", range(len(options)), format_func=lambda x: options[x], index=0)
    with c2:
        idx2 = st.selectbox("Follow-up (Current) Scan", range(len(options)), format_func=lambda x: options[x], index=len(options)-1)
        
    scan1 = history[idx1]
    scan2 = history[idx2]

    # Automatically display the stitched images side-by-side
    img_col1, img_col2 = st.columns(2)
    with img_col1:
        st.image(scan1['image_bytes'], caption=f"Baseline: {scan1['date']}", use_container_width=True)
    with img_col2:
        st.image(scan2['image_bytes'], caption=f"Follow-up: {scan2['date']}", use_container_width=True)

    st.markdown("### 📊 Progression Analytics")
    initial_severity = scan1['severity']
    current_severity = scan2['severity']
    
    if current_severity < initial_severity:
        status = "Improving"
        line_color = "#28a745" # Green
    elif current_severity > initial_severity:
        status = "Worsening"
        line_color = "#dc3545" # Red
    else:
        status = "Unchanged"
        line_color = "#ffc107" # Yellow
            
    severity_change = current_severity - initial_severity

    m1, m2 = st.columns(2)
    with m1:
        st.metric(
            label="Disease Severity Status", 
            value=f"{current_severity}%", 
            delta=f"{severity_change}% ({status})",
            delta_color="inverse" if status != "Unchanged" else "off"
        )
    with m2:
        st.metric(label="🔥 Current Logging Streak", value=f"{st.session_state.streak} Updates")

    # Chart shows all historical scans, plotting the journey over time
    df_chart = pd.DataFrame({
        "Timeline": [s['date'] for s in history],
        "Severity (%)": [s['severity'] for s in history]
    })
    
    line = alt.Chart(df_chart).mark_line(
        color=line_color, strokeWidth=4, point=alt.OverlayMarkDef(color=line_color, size=150, filled=True)
    ).encode(
        x=alt.X('Timeline', sort=None, axis=alt.Axis(labelAngle=-15, labelFontSize=11, titlePadding=15)),
        y=alt.Y('Severity (%)', scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(labelFontSize=12)),
        tooltip=['Timeline', 'Severity (%)']
    )
    
    area = alt.Chart(df_chart).mark_area(color=line_color, opacity=0.15).encode(
        x=alt.X('Timeline', sort=None), y=alt.Y('Severity (%)')
    )
    
    chart = (area + line).properties(height=350).configure_view(strokeWidth=0)
    st.altair_chart(chart, use_container_width=True)

    # Manual submit button to keep the gamified streak logic working
    if st.button("Log Progress & Update Streak", type="primary"):
        st.session_state.streak += 1
        if st.session_state.streak > 0 and st.session_state.streak % 3 == 0:
            st.balloons()
            
        record = {
            "Date Logged": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Initial Severity (%)": initial_severity,
            "Current Severity (%)": current_severity,
            "Status": status,
            "Compared Scans": f"{scan1['date']} vs {scan2['date']}"
        }
        st.session_state.progress_history.append(record)
        st.rerun()

    st.markdown("---")
    st.subheader("📋 Progress Tracking History")
    
    if st.session_state.progress_history:
        history_df = pd.DataFrame(st.session_state.progress_history)
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("No progress records logged yet. Click 'Log Progress' above.")

with col2:
    if st.session_state.streak > 0 and st.session_state.streak % 3 == 0 and lottie_trophy:
        st_lottie(lottie_trophy, height=350, key="trophy_lottie")
    elif lottie_progress:
        st_lottie(lottie_progress, height=350, key="progress_lottie")

st.markdown("<hr><div class='footer'>🏠 <a href='../app.py'>Back to Dashboard</a></div>", unsafe_allow_html=True)