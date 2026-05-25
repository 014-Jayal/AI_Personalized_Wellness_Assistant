from google import genai
from backend.config import GEMINI_API_KEY
import time

client = genai.Client(api_key=GEMINI_API_KEY)


# =========================
# WELLNESS PLAN (FIXED)
# =========================
def generate_wellness_plan(disease):

    prompt = f"""
    You are a professional dermatologist assistant.

    A patient is diagnosed with: {disease}

    Provide:
    - Diet
    - Lifestyle
    - Exercise
    - Skincare

    Make it specific, practical, and structured in bullet points.
    """

    models = [
        "models/gemini-2.5-flash",
        "models/gemini-pro-latest",
        "models/gemini-flash-lite-latest"
    ]

    for model_name in models:
        try:
            print(f"Trying model: {model_name}")

            response = client.models.generate_content(
                model=model_name,
                contents=[prompt]
            )

            if hasattr(response, "text") and response.text:
                return response.text.strip()

            if response.candidates:
                return response.candidates[0].content.parts[0].text

        except Exception as e:
            print(f"{model_name} failed:", e)

    # FINAL FALLBACK (always works)
    return fallback_recommendation(disease)


# =========================
# FALLBACK (CRITICAL)
# =========================
def fallback_recommendation(disease):

    disease = disease.lower()

    # 🔴 ACNE
    if "acne" in disease:
        return """
Diet:
- Reduce high glycemic foods (white bread, sugar)
- Avoid dairy (linked to acne flare-ups)
- Increase zinc (nuts, seeds) and omega-3 (fish)

Lifestyle:
- Avoid touching face
- Change pillowcases regularly
- Manage stress (cortisol worsens acne)

Exercise:
- Moderate cardio improves circulation
- Shower immediately after sweating

Skincare:
- Use 2% salicylic acid cleanser (morning)
- Apply benzoyl peroxide (night)
- Use non-comedogenic moisturizer + sunscreen
"""

    # 🔴 ECZEMA
    elif "eczema" in disease:
        return """
Diet:
- Avoid known triggers (dairy, gluten if sensitive)
- Increase anti-inflammatory foods (leafy greens)

Lifestyle:
- Avoid hot showers (use lukewarm water)
- Maintain humidity in room

Exercise:
- Low sweat exercises (yoga, walking)

Skincare:
- Use thick ceramide-based moisturizer (3x daily)
- Avoid fragrances and harsh soaps
- Apply steroid cream during flare (if prescribed)
"""

    # 🔴 PSORIASIS
    elif "psoriasis" in disease:
        return """
Diet:
- Anti-inflammatory diet (omega-3, turmeric)
- Avoid alcohol and processed foods

Lifestyle:
- Reduce stress (major trigger)
- Get sunlight exposure (Vitamin D)

Exercise:
- Regular moderate exercise

Skincare:
- Use coal tar / salicylic acid products
- Moisturize frequently
- Avoid skin injuries (Koebner effect)
"""

    # 🔴 FUNGAL INFECTION
    elif "fungal" in disease:
        return """
Diet:
- Reduce sugar (fungus thrives on glucose)

Lifestyle:
- Keep affected area dry
- Avoid tight clothing

Exercise:
- Maintain hygiene post workout

Skincare:
- Apply antifungal creams (clotrimazole)
- Keep skin dry and clean
"""

    # 🔴 MELANOMA / SERIOUS
    elif "melanoma" in disease:
        return """
⚠️ This condition requires immediate medical attention.

Diet:
- Support immunity (fruits, antioxidants)

Lifestyle:
- Avoid sun exposure completely

Exercise:
- Light only if approved by doctor

Skincare:
- DO NOT self-treat
- Consult dermatologist urgently
"""

    # 🟡 DEFAULT
    return f"""
General Care for {disease}:

Diet:
- Balanced nutrition + hydration

Lifestyle:
- Maintain hygiene
- Avoid irritants

Exercise:
- Regular activity

Skincare:
- Gentle cleansing + moisturizing
"""


# =========================
# CHATBOT (FIXED)
# =========================
def chat_with_wellness_coach(user_message, disease_context):

    prompt = f"""
    You are a dermatology assistant.

    Condition: {disease_context}

    Answer clearly and safely.

    User: {user_message}
    """

    models = [
        "models/gemini-2.5-flash",
        "models/gemini-pro-latest",
        "models/gemini-flash-lite-latest"
    ]

    for model_name in models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[prompt]
            )

            if hasattr(response, "text") and response.text:
                return response.text.strip()

            if response.candidates:
                return response.candidates[0].content.parts[0].text

        except Exception as e:
            print(f"{model_name} chat failed:", e)

    return "⚠️ AI assistant temporarily unavailable."