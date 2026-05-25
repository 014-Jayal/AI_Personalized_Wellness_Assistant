import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, f1_score
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# =========================
# CONFIGURATION
# =========================
DATASET_DIR = "dataset/test"
BATCH_SIZE = 16
NUM_CLASSES = 5
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CLASS_NAMES = ["acne", "eczema", "normal", "psoriasis", "ringworm"]

MODEL_PATHS = {
    "EfficientNet-B3": "model/skin_disease_efficientnet.pth",
    "MobileNetV2": "model/mobilenet_v2.pth",
    "ResNet18": "model/resnet18.pth",
    "DenseNet121": "model/densenet121.pth",
    "ResNet50": "model/resnet50.pth"
}

# =========================
# DATASET
# =========================
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

dataset = datasets.ImageFolder(DATASET_DIR, transform=transform)
loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False)

print("Classes:", CLASS_NAMES)
print("Test samples:", len(dataset))

# =========================
# MODEL LOADER (MATCH TRAINING)
# =========================
def load_model(name):
    if name == "EfficientNet-B3":
        model = models.efficientnet_b3(weights=None)
        model.classifier = nn.Sequential(
            nn.Linear(1536, 256),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(256, NUM_CLASSES)
        )

    elif name == "MobileNetV2":
        model = models.mobilenet_v2(weights=None)
        model.classifier[1] = nn.Linear(
            model.classifier[1].in_features, NUM_CLASSES
        )

    elif name == "ResNet18":
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)

    elif name == "DenseNet121":
        model = models.densenet121(weights=None)
        model.classifier = nn.Linear(
            model.classifier.in_features, NUM_CLASSES
        )

    elif name == "ResNet50":
        model = models.resnet50(weights=None)
        model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)

    else:
        raise ValueError("Unknown model")

    model.load_state_dict(torch.load(MODEL_PATHS[name], map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model

# =========================
# COLLECT PREDICTIONS
# =========================
def get_predictions(model):
    y_true, y_pred = [], []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(DEVICE)
            outputs = model(images)
            preds = torch.argmax(outputs, dim=1).cpu().numpy()

            y_pred.extend(preds)
            y_true.extend(labels.numpy())

    return np.array(y_true), np.array(y_pred)

# =========================
# F1 SCORE COMPUTATION
# =========================
f1_table = pd.DataFrame(index=MODEL_PATHS.keys(), columns=CLASS_NAMES)
summary = []

for model_name in MODEL_PATHS:
    print(f"Evaluating {model_name}")
    model = load_model(model_name)
    y_true, y_pred = get_predictions(model)

    report = classification_report(
        y_true,
        y_pred,
        target_names=CLASS_NAMES,
        output_dict=True,
        zero_division=0
    )

    for cls in CLASS_NAMES:
        f1_table.loc[model_name, cls] = report[cls]["f1-score"]

    summary.append({
        "Model": model_name,
        "Macro F1": f1_score(y_true, y_pred, average="macro"),
        "Weighted F1": f1_score(y_true, y_pred, average="weighted")
    })

f1_table = f1_table.astype(float)
summary_df = pd.DataFrame(summary)

# =========================
# SAVE TABLES
# =========================
f1_table.to_csv("f1_per_class_5class.csv")
summary_df.to_csv("f1_macro_weighted.csv", index=False)

# =========================
# 1️⃣ HEATMAP (BEST FIGURE)
# =========================
plt.figure(figsize=(8, 5))
sns.heatmap(
    f1_table,
    annot=True,
    fmt=".2f",
    cmap="YlGnBu"
)
plt.title("Per-Class F1 Score Heatmap (5-Class Skin Disease)")
plt.xlabel("Disease")
plt.ylabel("Model")
plt.tight_layout()
plt.savefig("f1_heatmap_5class.png", dpi=300)
plt.show()

# =========================
# 2️⃣ GROUPED BAR CHART
# =========================
f1_table.plot(
    kind="bar",
    figsize=(10, 5)
)
plt.title("Per-Class F1 Score Comparison (5 Classes)")
plt.ylabel("F1 Score")
plt.xticks(rotation=0)
plt.legend(title="Disease")
plt.tight_layout()
plt.savefig("f1_grouped_bar_5class.png", dpi=300)
plt.show()

# =========================
# 3️⃣ MACRO vs WEIGHTED F1
# =========================
summary_df.set_index("Model")[["Macro F1", "Weighted F1"]].plot(
    kind="bar",
    figsize=(8, 5)
)
plt.title("Macro vs Weighted F1 Score")
plt.ylabel("F1 Score")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("f1_macro_weighted.png", dpi=300)
plt.show()

print("\n✅ F1-score evaluation and visualization completed successfully.")
