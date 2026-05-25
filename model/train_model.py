import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from tqdm import tqdm

# =========================
# CONFIGURATION
# =========================
DATA_DIR = "../dataset"
BATCH_SIZE = 16
IMAGE_SIZE = 224
EPOCHS = 12          # total epochs (7 frozen + 5 fine-tune)
FINE_TUNE_EPOCHS = 5
MODEL_PATH = "skin_disease_efficientnet.pth"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =========================
# DATA TRANSFORMS
# =========================
train_transforms = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.1, contrast=0.1),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

test_transforms = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# =========================
# DATASETS & LOADERS
# =========================
train_dataset = datasets.ImageFolder(f"{DATA_DIR}/train", transform=train_transforms)
test_dataset = datasets.ImageFolder(f"{DATA_DIR}/test", transform=test_transforms)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

NUM_CLASSES = len(train_dataset.classes)

print("\n✅ Dataset Loaded")
print("Classes:", train_dataset.classes)
print("Train Images:", len(train_dataset))
print("Test Images:", len(test_dataset))
print("Using device:", device)

# =========================
# MODEL SETUP
# =========================
model = models.efficientnet_b3(weights=models.EfficientNet_B3_Weights.DEFAULT)

# Freeze full backbone initially
for param in model.features.parameters():
    param.requires_grad = False

# Custom classifier
num_features = model.classifier[1].in_features
model.classifier = nn.Sequential(
    nn.Linear(num_features, 256),
    nn.ReLU(),
    nn.Dropout(0.4),
    nn.Linear(256, NUM_CLASSES)
)

model = model.to(device)

# =========================
# LOSS & OPTIMIZER
# =========================
criterion = nn.CrossEntropyLoss()

optimizer = optim.Adam(
    model.classifier.parameters(),
    lr=1e-3
)

# =========================
# TRAINING FUNCTION
# =========================
def evaluate():
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    return 100 * correct / total

best_acc = 0.0

# =========================
# PHASE 1 — TRAIN CLASSIFIER
# =========================
print("\n🚀 Phase 1: Training Classifier Head\n")

for epoch in range(EPOCHS - FINE_TUNE_EPOCHS):
    model.train()
    running_loss = 0.0

    for images, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS}"):
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    val_acc = evaluate()

    print(f"Epoch {epoch+1} | Loss: {running_loss:.4f} | Val Acc: {val_acc:.2f}%")

    if val_acc > best_acc:
        best_acc = val_acc
        torch.save(model.state_dict(), MODEL_PATH)

# =========================
# PHASE 2 — FINE TUNING
# =========================
print("\n🔥 Phase 2: Fine-Tuning Last Layers\n")

# Unfreeze last EfficientNet blocks
for param in model.features[6:].parameters():
    param.requires_grad = True

optimizer = optim.Adam(
    filter(lambda p: p.requires_grad, model.parameters()),
    lr=1e-4
)

for epoch in range(FINE_TUNE_EPOCHS):
    model.train()
    running_loss = 0.0

    for images, labels in tqdm(train_loader, desc=f"FineTune Epoch {epoch+1}/{FINE_TUNE_EPOCHS}"):
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    val_acc = evaluate()

    print(f"FineTune Epoch {epoch+1} | Loss: {running_loss:.4f} | Val Acc: {val_acc:.2f}%")

    if val_acc > best_acc:
        best_acc = val_acc
        torch.save(model.state_dict(), MODEL_PATH)

# =========================
# FINAL RESULT
# =========================
print("\n🏆 TRAINING COMPLETE")
print(f"Best Validation Accuracy: {best_acc:.2f}%")
print(f"Model saved as: {MODEL_PATH}")
