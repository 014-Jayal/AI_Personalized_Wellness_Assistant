import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import os
import numpy as np

# =========================
# CONFIG
# =========================
DATASET_DIR = "../dataset/test"
BATCH_SIZE = 16
NUM_CLASSES = 5
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MODEL_PATHS = {
    "EfficientNet-B3": "skin_disease_efficientnet.pth",
    "MobileNetV2": "mobilenet_v2.pth",
    "ResNet18": "resnet18.pth",
    "DenseNet121": "densenet121.pth",
    "ResNet50": "resnet50.pth"
}

# =========================
# DATASET
# =========================
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

dataset = datasets.ImageFolder(DATASET_DIR, transform=transform)
loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False)

class_names = dataset.classes
print("Classes:", class_names)
print("Test samples:", len(dataset))

# =========================
# MODEL LOADER (EXACT MATCH)
# =========================
def load_model(model_name):
    if model_name == "EfficientNet-B3":
        model = models.efficientnet_b3(weights=None)
        model.classifier = nn.Sequential(
            nn.Linear(1536, 256),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(256, NUM_CLASSES)
        )

    elif model_name == "MobileNetV2":
        model = models.mobilenet_v2(weights=None)
        # IMPORTANT: DO NOT redefine classifier
        model.classifier[1] = nn.Linear(
            model.classifier[1].in_features,
            NUM_CLASSES
        )

    elif model_name == "ResNet18":
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)

    elif model_name == "DenseNet121":
        model = models.densenet121(weights=None)
        model.classifier = nn.Linear(
            model.classifier.in_features,
            NUM_CLASSES
        )

    elif model_name == "ResNet50":
        model = models.resnet50(weights=None)
        model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)

    else:
        raise ValueError("Unknown model")

    model.load_state_dict(
        torch.load(MODEL_PATHS[model_name], map_location=DEVICE)
    )
    model.to(DEVICE)
    model.eval()
    return model

# =========================
# PER-CLASS ACCURACY
# =========================
def evaluate_per_class(model):
    correct = np.zeros(NUM_CLASSES)
    total = np.zeros(NUM_CLASSES)

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)
            preds = torch.argmax(outputs, dim=1)

            for i in range(len(labels)):
                label = labels[i].item()
                total[label] += 1
                if preds[i].item() == label:
                    correct[label] += 1

    acc = {}
    for i, cls in enumerate(class_names):
        acc[cls] = 100 * correct[i] / total[i] if total[i] > 0 else 0.0
    return acc

# =========================
# RUN EVALUATION
# =========================
results = {}

for model_name in MODEL_PATHS:
    print(f"\n🔍 Evaluating {model_name}")
    model = load_model(model_name)
    acc = evaluate_per_class(model)
    results[model_name] = acc
    for cls, val in acc.items():
        print(f"{cls}: {val:.2f}%")

print("\n📊 FINAL MATRIX (Model × Disease)")
for model, scores in results.items():
    print(model, scores)
