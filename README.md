````markdown
# 🌿 AI-Powered Personalized Wellness Assistant

An end-to-end, full-stack artificial intelligence platform designed to provide dermatological assessments, explainable AI visualizations, and personalized wellness protocols. The system integrates a custom-trained PyTorch CNN with Google's Gemini LLM to deliver actionable healthcare insights, secure patient authentication, and recovery tracking.

---

# ✨ Key Features

## 🔐 Secure Patient Portal
- End-to-end user authentication system
- Secure SQLite database integration
- Patient profile and wellness tracking

## 🩺 Dermatological Assessment
- Upload skin images for instant AI-based classification
- Supports 5 skin condition categories:
  - Acne
  - Eczema
  - Psoriasis
  - Ringworm
  - Normal Skin
- Powered by an EfficientNet-B3 deep learning model

## 🧠 Explainable AI (XAI)
- Generates Grad-CAM heatmaps
- Visualizes regions influencing AI predictions
- Enhances model transparency and interpretability

## 🌱 Personalized Wellness Protocols
- AI-generated wellness plans using Gemini 2.5 Flash API
- Customized:
  - Diet recommendations
  - Lifestyle improvements
  - Exercise suggestions
  - Skincare routines

## 📈 Recovery Analytics Dashboard
- Track daily wellness progress
- Compare baseline and follow-up scans
- Visualize symptom severity trends over time

---

# 🛠️ Technology Stack

## Frontend
- Streamlit
- HTML5
- CSS3
- Altair Charts
- Lottie Animations

## Backend
- FastAPI
- Python

## Deep Learning & AI
- PyTorch
- Torchvision (EfficientNet-B3)
- OpenCV (Grad-CAM)
- Google Gemini API (`genai` SDK)

## Database
- SQLite3

## Development Tools
- Git
- GitHub
- VS Code

---

# 📂 Project Structure

```text
AI_Personalized_Wellness_Assistant/
│
├── assets/
│   └── style.css
│
├── backend/
│   ├── config.py
│   ├── gradcam.py
│   ├── main.py
│   ├── predict.py
│   ├── recommendation_engine.py
│   └── wellness_plans.py
│
├── database/
│   ├── db.py
│   └── patient_data.db
│
├── frontend/
│   ├── app.py
│   └── pages/
│       ├── 1_Diagnosis.py
│       ├── 2_Recommendations.py
│       └── 3_Progress_Tracking.py
│
├── model/
│   ├── train_model.py
│   ├── evaluate_per_class.py
│   └── skin_disease_efficientnet.pth
│
├── requirements.txt
└── README.md
```

---

# 🚀 Installation & Setup

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/027sakshi/AI_Personalized_Wellness_Assistant.git
cd AI_Personalized_Wellness_Assistant
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Configure Gemini API Key

Open:

```text
backend/config.py
```

Update:

```python
GEMINI_API_KEY = "your_actual_api_key_here"
```

---

## 5️⃣ Initialize Database

```bash
python database/db.py
```

---

## 6️⃣ Run the Backend Server

```bash
uvicorn backend.main:app --reload --port 8000
```

---

## 7️⃣ Run the Frontend Application

Open a new terminal:

```bash
streamlit run frontend/app.py
```

---

## 8️⃣ Open in Browser

Visit:

```text
http://localhost:8501
```

---

# 📊 Model Performance

The diagnostic engine utilizes the **EfficientNet-B3** architecture for multi-class skin disease classification.

The model was trained and evaluated against:
- MobileNetV2
- ResNet18
- DenseNet121
- ResNet50
- EfficientNet-B3

EfficientNet-B3 achieved the best performance based on:
- Macro F1 Score
- Weighted F1 Score
- Classification Accuracy

Evaluation visualizations include:
- Heatmaps
- F1 Score Comparison Charts
- Grouped Bar Graphs

Generated using:

```text
evaluate_f1_and_plots.py
```

---

# 🔍 Explainable AI Workflow

```text
User Uploads Image
        ↓
Image Preprocessing
        ↓
EfficientNet-B3 Prediction
        ↓
Grad-CAM Heatmap Generation
        ↓
Gemini AI Wellness Recommendation
        ↓
Dashboard Analytics & Tracking
```

---

# 🌟 Future Enhancements

- Real-time AI chatbot integration
- Cloud deployment support
- Mobile application version
- Multi-language support
- Advanced recommendation engine
- Doctor consultation module
- User health history analytics

---

# 👨‍💻 Author

## Sakshi Giglani

GitHub: https://github.com/027sakshi

---

# 📄 License

This project is developed for educational and academic purposes.

---
````
