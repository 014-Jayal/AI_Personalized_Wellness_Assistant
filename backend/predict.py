import torch
import torchvision.transforms as transforms
from torchvision.models import efficientnet_b3
from PIL import Image
from backend.gradcam import generate_gradcam

# ---------------------------
# DEVICE
# ---------------------------
device = torch.device("cpu")


# ---------------------------
# LOAD MODEL (UNCHANGED ARCH)
# ---------------------------
model = efficientnet_b3(weights=None)

model.classifier = torch.nn.Sequential(
    torch.nn.Linear(1536, 256),
    torch.nn.ReLU(),
    torch.nn.Dropout(0.3),
    torch.nn.Linear(256, 5)
)

model.load_state_dict(
    torch.load("model/skin_disease_efficientnet.pth", map_location=device)
)

model.to(device)
model.eval()


# ---------------------------
# CLASS LABELS
# ---------------------------
class_names = [
    "acne",
    "eczema",
    "psoriasis",
    "ringworm",
    "normal"
]


# ---------------------------
# ✅ FIXED TRANSFORM (CRITICAL)
# ---------------------------
transform = transforms.Compose([
    transforms.Resize((300, 300)),   # 🔥 correct for EfficientNet-B3
    transforms.ToTensor(),
    transforms.Normalize(            # 🔥 MUST HAVE
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# ---------------------------
# PREDICTION FUNCTION
# ---------------------------
def predict_disease(image: Image.Image):

    try:
        img_tensor = transform(image).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(img_tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)

        confidence, pred = torch.max(probs, 1)

        confidence = float(confidence.item())

        # 🔥 SAFETY THRESHOLD
        if confidence < 0.5:
            disease = "uncertain (consult dermatologist)"
        else:
            disease = class_names[pred.item()]

        # ---------------------------
        # GradCAM (safe execution)
        # ---------------------------
        try:
            heatmap = generate_gradcam(model, image)
        except Exception as e:
            print("GradCAM error:", e)
            heatmap = None

        return disease, confidence, heatmap

    except Exception as e:
        print("Prediction Error:", e)
        return "error", 0.0, None