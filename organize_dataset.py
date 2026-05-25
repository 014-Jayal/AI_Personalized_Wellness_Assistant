import os
import shutil

SOURCE_DIR = "raw_dataset"
TARGET_DIR = "dataset"

CLASS_MAPPING = {
    "Acne and Rosacea Photos": "acne",
    "Atopic Dermatitis Photos": "eczema",
    "Eczema Photos": "eczema",
    "Psoriasis pictures Lichen Planus and related diseases": "psoriasis",
    "Tinea Ringworm Candidiasis and other Fungal Infections": "ringworm",
    "Light Diseases and Disorders of Pigmentation": "normal"
}

def create_dirs():
    for split in ["train", "test"]:
        for cls in set(CLASS_MAPPING.values()):
            path = os.path.join(TARGET_DIR, split, cls)
            os.makedirs(path, exist_ok=True)

def copy_images(split):
    print(f"\nProcessing {split} data...")
    for src_folder, target_class in CLASS_MAPPING.items():
        src_path = os.path.join(SOURCE_DIR, split, src_folder)

        if not os.path.exists(src_path):
            print(f"❌ Missing folder: {src_path}")
            continue

        images = [
            img for img in os.listdir(src_path)
            if img.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        for img in images:
            shutil.copy(
                os.path.join(src_path, img),
                os.path.join(TARGET_DIR, split, target_class, img)
            )

        print(f"✔ {target_class}: {len(images)} images copied")

def main():
    print("🚀 Organizing dataset...")
    create_dirs()
    copy_images("train")
    copy_images("test")
    print("\n✅ Dataset organization completed!")

if __name__ == "__main__":
    main()
