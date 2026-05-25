from fastapi import FastAPI, File, UploadFile
from PIL import Image
from backend.predict import predict_disease
from backend.recommendation_engine import generate_wellness_plan
from backend.wellness_plans import DIET_PLAN, EXERCISE_PLAN

app = FastAPI(title="AI Wellness Assistant API")

@app.get("/")
def home():
    return {"message": "Skin AI Backend Running"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image = Image.open(file.file).convert("RGB")

    disease, confidence, heatmap = predict_disease(image)
    wellness_text = generate_wellness_plan(disease)

    structured_diet = DIET_PLAN.get(disease, DIET_PLAN["normal"])
    structured_exercise = EXERCISE_PLAN.get(disease, EXERCISE_PLAN["normal"])

    return {
        "predicted_disease": disease,
        "confidence": confidence,
        "heatmap": heatmap,
        "recommendation_text": wellness_text, 
        "diet_list": structured_diet,          
        "exercise_list": structured_exercise   
    }