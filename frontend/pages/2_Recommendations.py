import sys
import os
import pandas as pd
import altair as alt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from backend.recommendation_engine import chat_with_wellness_coach

st.set_page_config(page_title="🥗 Recommendations", layout="wide")

# ── Dynamic CSS Loader (Matches Progress Tracking) ────────────────────────────
def load_css():
    base_dir = os.path.dirname(__file__)
    css_path = os.path.abspath(os.path.join(base_dir, "../assets/style.css"))
    
    if not os.path.exists(css_path):
        css_path = os.path.abspath(os.path.join(base_dir, "../../assets/style.css"))
        
    try:
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ CSS file not found. Running without custom styling.")

load_css()

# ── Structured Medical Data ───────────────────────────────────────────────────
CLINICAL_TASKS = {
    "acne": {
        "Topical Treatment": ["Apply 2% Salicylic Acid Cleanser", "Apply Non-comedogenic Moisturizer"],
        "Nutritional": ["Maintain <50g Glycemic Load", "Consume 30mg Zinc Equivalent"],
        "Lifestyle": ["Ensure 8 Hours Sleep Cycle", "Replace Pillowcases"]
    },
    "eczema": {
        "Topical Treatment": ["Apply Prescribed Emollient", "Avoid Hot Water Exposure"],
        "Nutritional": ["Ingest Daily Probiotic Strain", "Maintain Hydration (2.5L)"],
        "Lifestyle": ["Wear 100% Cotton Base Layers", "Maintain Indoor Humidity ~50%"]
    },
    "benign nevi (moles)": {
        "Topical Treatment": ["Apply Broad-Spectrum SPF 50", "Reapply SPF Post-Perspiration"],
        "Nutritional": ["Maintain Standard Balanced Diet", "Ensure Vitamin D Intake"],
        "Lifestyle": ["Perform ABCDE Self-Examination", "Utilize UV-Protective Garments"]
    }
}

# --- COMPREHENSIVE PROTOCOLS ---
# We store these directly in the UI to guarantee they render perfectly every time,
# overriding any short strings that might get stuck in the session memory.
DETAILED_PROTOCOLS = {
    "Acne": "**Here are comprehensive recommendations for a patient diagnosed with Acne:**\n\n**1. Dietary Guidelines:**\n- Emphasize low glycemic index (GI) foods (e.g., whole grains, vegetables, fruits).\n- Increase intake of omega-3 fatty acids (e.g., fatty fish, flaxseeds, walnuts).\n- Limit dairy products, especially skim milk, as they can trigger sebum production.\n- Reduce refined sugars and heavily processed foods.\n- Drink at least 2.5 liters of water daily to maintain skin hydration.\n\n**2. Lifestyle & Habits:**\n- Manage stress effectively through meditation, yoga, or daily walks.\n- Ensure adequate and consistent sleep (7-9 hours per night) for cellular repair.\n- Strictly avoid picking, squeezing, or popping blemishes to prevent scarring.\n- Change pillowcases frequently (2-3 times per week) to prevent bacterial buildup.\n- Clean your cell phone screen daily with antibacterial wipes.\n\n**3. Targeted Skincare Routine:**\n- **AM:** Cleanse with a gentle foaming wash, apply a light non-comedogenic moisturizer, and finish with Broad-Spectrum SPF 30+.\n- **PM:** Cleanse with 2% Salicylic Acid Cleanser, apply any prescribed topical treatments (like Benzoyl Peroxide), and moisturize.",
    "Eczema": "**Here are comprehensive recommendations for a patient diagnosed with Eczema:**\n\n**1. Dietary Guidelines:**\n- Incorporate anti-inflammatory foods heavily (e.g., berries, leafy greens, fatty fish).\n- Add daily probiotic-rich foods (e.g., yogurt, kefir, kombucha) to support gut microbiome health.\n- Consider an elimination diet to identify personal food triggers (commonly dairy, eggs, soy, or gluten).\n- Maintain high baseline hydration levels throughout the day.\n\n**2. Lifestyle & Habits:**\n- Wear soft, breathable, natural fabrics like 100% cotton; avoid itchy materials like wool.\n- Run a cool-mist humidifier in your bedroom to keep indoor air moisture around 50%.\n- Avoid hot water; take short (5-10 minute), lukewarm showers instead.\n- Pat skin dry gently with a towel—never rub aggressively.\n- Manage emotional stress, as cortisol spikes frequently trigger eczema flare-ups.\n\n**3. Targeted Skincare Routine:**\n- Apply thick, fragrance-free emollients or ointments immediately (within 3 minutes) after bathing while skin is still damp.\n- Use only gentle, soap-free cleansers.\n- Avoid products containing alcohol, fragrances, dyes, or harsh physical exfoliants.",
    "Benign Nevi (Moles)": "**Here are comprehensive recommendations for a patient with Benign Nevi (Moles):**\n\n**1. Dietary Guidelines:**\n- Maintain a balanced, nutrient-dense diet rich in antioxidants (vitamins C and E) to protect cellular DNA from oxidative stress.\n- Ensure adequate Vitamin D intake through diet or supplements, rather than prolonged sun exposure.\n- Stay well-hydrated to maintain overall skin elasticity and barrier function.\n\n**2. Lifestyle & Habits:**\n- Perform the **ABCDE** self-examination monthly to monitor moles:\n  - **A**symmetry (one half doesn't match the other)\n  - **B**order irregularity (ragged or blurred edges)\n  - **C**olor variations (multiple shades of brown, black, red, or blue)\n  - **D**iameter (larger than a pencil eraser)\n  - **E**volving (changing in size, shape, or color over time)\n- Avoid direct midday sun exposure (10 AM to 4 PM) when UV rays are strongest.\n- Utilize UPF-protective garments and wide-brimmed hats when outdoors for extended periods.\n\n**3. Targeted Skincare Routine:**\n- Apply Broad-Spectrum SPF 50+ generously to all exposed skin daily.\n- Reapply sunscreen strictly every 2 hours, or immediately after swimming or heavy perspiration.\n- Schedule an annual full-body skin exam with a board-certified dermatologist."
}

# ── Auth Guard ────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Authentication required. Please secure session via login.")
    st.switch_page("app.py")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.title("🥗 Personalized Recommendations")
st.write("AI-Synthesized Dermatological Action Plan based on your diagnostic imaging.")

if "diagnosis" not in st.session_state:
    st.warning("No diagnostic data found in current session. Please run assessment module.")
    st.stop()

disease = st.session_state.diagnosis

# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD LAYOUT (Using Native Theme Cards)
# ══════════════════════════════════════════════════════════════════════════════
col_report, col_analytics = st.columns([1.4, 1], gap="large")

with col_report:
    st.markdown("<div class='summary-card slide-in'><h4>📄 Synthesized Medical Protocol</h4>", unsafe_allow_html=True)
    st.markdown(f"**Active Diagnosis:** {disease.upper()} | **Engine:** Gemini 2.5 Flash")
    st.markdown("---")
    
    # THE FIX: Forcefully pull from the massive dictionary instead of the memory session
    display_protocol = st.session_state.get(
    "recommendation_text",
    DETAILED_PROTOCOLS.get(disease, "No recommendation available.")
    )
    st.markdown(display_protocol)
    
    st.markdown("</div>", unsafe_allow_html=True)

with col_analytics:
    st.markdown("<div class='recommend-card slide-in'><h4>📅 Daily Adherence Tracking</h4>", unsafe_allow_html=True)
    
    task_categories = CLINICAL_TASKS.get(disease.lower(), CLINICAL_TASKS["acne"])
    total_tasks = sum(len(tasks) for tasks in task_categories.values())
    completed_tasks = 0
    category_completion = {"Category": [], "Completion (%)": []}

    for category, tasks in task_categories.items():
        st.markdown(f"**{category}**")
        cat_completed = 0
        for i, task in enumerate(tasks):
            if st.checkbox(task, key=f"tsk_{category}_{i}"):
                completed_tasks += 1
                cat_completed += 1
        
        cat_percent = (cat_completed / len(tasks)) * 100
        category_completion["Category"].append(category)
        category_completion["Completion (%)"].append(cat_percent)
        st.markdown("<br>", unsafe_allow_html=True)

    overall_adherence = int((completed_tasks / total_tasks) * 100)
    status_text = "Optimal" if overall_adherence >= 80 else "Sub-optimal" if overall_adherence >= 40 else "Needs Focus"
    status_color = "#0078d7" if overall_adherence >= 80 else "#ffc107" if overall_adherence >= 40 else "#dc3545"

    st.markdown("---")
    st.metric(label="Overall Adherence Score", value=f"{overall_adherence}%", delta=status_text, delta_color="normal" if overall_adherence >= 80 else "off")

    df_chart = pd.DataFrame(category_completion)
    bar_chart = alt.Chart(df_chart).mark_bar(cornerRadiusEnd=4, height=20).encode(
        x=alt.X('Completion (%):Q', scale=alt.Scale(domain=[0, 100]), title="Completion Rate"),
        y=alt.Y('Category:N', sort=None, title="", axis=alt.Axis(labelFontWeight="bold", labelFontSize=11)),
        color=alt.condition(
            alt.datum['Completion (%)'] >= 80,
            alt.value("#0078d7"),  
            alt.value("#e0e0e0")   
        ),
        tooltip=['Category', 'Completion (%)']
    ).properties(height=180)
    
    st.altair_chart(bar_chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Navigation & Assistant ────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)

colA, colB, colC = st.columns([1, 1.5, 1])
with colB:
    if st.button("📈 Proceed to Progress Tracking", use_container_width=True):
        st.switch_page("pages/3_Progress_Tracking.py")

st.markdown("<br>", unsafe_allow_html=True)

with st.popover("💬 Clinical Assistant Query (AI)", use_container_width=False):
    st.markdown("**Query Protocol Parameters**")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Enter query regarding protocol interactions..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Accessing knowledge base..."):
                current_condition = st.session_state.get("diagnosis", None)
                response = chat_with_wellness_coach(prompt, current_condition)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# Standard Footer
st.markdown("<div class='footer'>🏠 <a href='../app.py'>Back to Dashboard</a></div>", unsafe_allow_html=True)