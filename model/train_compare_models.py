import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from tqdm import tqdm

# =========================
# CONFIG
# =========================
DATA_DIR = "../dataset"
BATCH_SIZE = 16
IMAGE_SIZE = 224
EPOCHS = 8
LR = 1e-3

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =========================
# DATA TRANSFORMS
# =========================
train_transforms = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
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
# DATA LOADERS
# =========================
train_dataset = datasets.ImageFolder(f"{DATA_DIR}/train", transform=train_transforms)
test_dataset = datasets.ImageFolder(f"{DATA_DIR}/test", transform=test_transforms)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

NUM_CLASSES = len(train_dataset.classes)

print("Classes:", train_dataset.classes)
print("Train images:", len(train_dataset))
print("Test images:", len(test_dataset))
print("Device:", device)

# =========================
# MODEL FACTORY
# =========================
def get_model(model_name):
    if model_name == "resnet18":
        model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)

    elif model_name == "resnet50":
        model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)

    elif model_name == "densenet121":
        model = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT)
        model.classifier = nn.Linear(model.classifier.in_features, NUM_CLASSES)

    elif model_name == "mobilenet_v2":
        model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, NUM_CLASSES)

    else:
        raise ValueError("Unknown model name")

    return model.to(device)

# =========================
# TRAIN & EVALUATE
# =========================
def evaluate(model):
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

def train_model(model_name):
    print(f"\n🚀 Training {model_name.upper()}")

    model = get_model(model_name)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LR)

    best_acc = 0.0

    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0

        for images, labels in tqdm(train_loader, desc=f"{model_name} Epoch {epoch+1}/{EPOCHS}"):
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        val_acc = evaluate(model)
        print(f"Epoch {epoch+1} | Loss: {running_loss:.2f} | Val Acc: {val_acc:.2f}%")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), f"{model_name}.pth")

    print(f"🏆 Best Accuracy for {model_name}: {best_acc:.2f}%")
    return best_acc

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    models_to_compare = [

    "resnet50",        
   
    ]
    results = {}

    for model_name in models_to_compare:
        acc = train_model(model_name)
        results[model_name] = acc

    print("\n📊 FINAL COMPARISON RESULTS")
    for model, acc in results.items():
        print(f"{model}: {acc:.2f}%")
