import os
import streamlit as st
from streamlit_lottie import st_lottie
import time, requests, datetime
import io
from PIL import Image
import base64

st.set_page_config(page_title="🏥 Diagnosis", layout="wide")

# ---------------- CSS ----------------
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

# ---------------- Lottie ----------------
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# Load CSS
base_dir = os.path.dirname(__file__)
css_path = os.path.abspath(os.path.join(base_dir, "../assets/style.css"))
if not os.path.exists(css_path):
    css_path = os.path.abspath(os.path.join(base_dir, "../../assets/style.css"))
load_css(css_path)

lottie_ai = load_lottieurl("https://lottie.host/79c8ad39-1280-45ac-8973-022ba60d4a9d/fPcehEHDyG.json")

# ---------------- SESSION ----------------
if 'scan_history' not in st.session_state:
    st.session_state.scan_history = []

# ---------------- UI ----------------
st.title("🏥 Skin Diagnosis")
st.write("Upload an image for AI-powered dermatological analysis.")

col1, col2 = st.columns([1.3, 1])

# ================= LEFT SIDE =================
with col1:
    uploaded_file = st.file_uploader("Upload skin image", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

        if st.button("🔍 Analyze Image & Save to Records", type="primary"):

            with st.spinner("AI analyzing image..."):

                try:
                    # 🔥 SEND IMAGE TO BACKEND
                    files = {"file": uploaded_file.getvalue()}
                    response = requests.post("http://127.0.0.1:8000/predict", files=files)

                    if response.status_code == 200:
                        result = response.json()

                        # ---------------- MODEL OUTPUT ----------------
                        disease = result["predicted_disease"]
                        confidence = result["confidence"]
                        heatmap = result["heatmap"]

                        # ---------------- SAVE SESSION ----------------
                        st.session_state.diagnosis = disease
                        st.session_state.confidence = confidence
                        st.session_state.summary = f"AI detected {disease} based on image patterns."
                        st.session_state.recommendation_text = result.get("recommendation_text", "")

                        # ---------------- HEATMAP DECODE ----------------
                        if heatmap:
                            heatmap_bytes = base64.b64decode(heatmap)
                            heatmap_img = Image.open(io.BytesIO(heatmap_bytes))
                            st.session_state.heatmap_img = heatmap_img
                        else:
                            st.session_state.heatmap_img = None

                        # ---------------- REAL SEVERITY ----------------
                        severity = int(confidence * 100)

                        st.session_state.scan_history.append({
                            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "condition": disease,
                            "severity": severity,
                            "image_bytes": uploaded_file.getvalue()
                        })

                        st.success(f"Analysis Complete: {disease} ✅")

                    else:
                        st.error("Backend error. Please check server.")

                except Exception as e:
                    st.error(f"Connection failed: {e}")

# ================= RESULT DISPLAY =================
if 'diagnosis' in st.session_state:

    st.markdown("---")

    colA, colB = st.columns([1, 2])

    with colA:
        st.metric("Detected Condition", st.session_state.diagnosis)
        st.metric("Confidence", f"{st.session_state.confidence * 100:.0f}%")
        st.progress(int(st.session_state.confidence * 100))

    with colB:
        st.markdown(f"""
        <div class='summary-card'>
        <h4>Condition Summary</h4>
        <p>{st.session_state.summary}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 🔥 REAL HEATMAP DISPLAY
        with st.expander("🔥 View AI Attention Heatmap"):
            if st.session_state.get("heatmap_img"):
                st.image(st.session_state.heatmap_img, use_container_width=True)
            else:
                st.warning("Heatmap not available.")

    st.info(f"💾 {len(st.session_state.scan_history)} scan(s) saved.")

    st.markdown("Your personalized plan is ready.")

    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        if st.button("🥗 See My Recommendations", use_container_width=True):
            st.switch_page("pages/2_Recommendations.py")

    with btn_col2:
        if st.button("📈 Track Visual Progress", use_container_width=True):
            st.switch_page("pages/3_Progress_Tracking.py")

# ================= EMPTY STATE =================
else:
    if lottie_ai:
        st_lottie(lottie_ai, height=400)

# ---------------- FOOTER ----------------
st.markdown("<hr><div class='footer'>🏠 <a href='../app.py'>Back to Dashboard</a></div>", unsafe_allow_html=True)