"""
Step 1: Dataset Splitting Script
Stratified Train / Validation / Test Splitting for Leaf Disease & Quality Datasets.
Supports individual crops or combined all-crop classification.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import json
import random
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split
from tabulate import tabulate

from config import (
    RAW_DATASET_DIR,
    SPLITS_DIR,
    DATA_DIR,
    CROPS_CONFIG,
    SPLIT_CONFIG
)

def scan_crop_images(crop_key: str):
    """
    Scans image files for a given crop key or 'all'.
    Returns a list of dicts with filepath, crop, label_name.
    """
    records = []
    
    if crop_key == "all":
        crops_to_scan = CROPS_CONFIG.keys()
    else:
        if crop_key not in CROPS_CONFIG:
            raise ValueError(f"Unknown crop key: '{crop_key}'. Valid options: {list(CROPS_CONFIG.keys())} or 'all'")
        crops_to_scan = [crop_key]

    for c in crops_to_scan:
        cfg = CROPS_CONFIG[c]
        crop_dir = RAW_DATASET_DIR / cfg["folder"]
        if not crop_dir.exists():
            print(f"⚠️ Warning: Crop directory does not exist: {crop_dir}")
            continue

        for cls_name in cfg["classes"]:
            cls_dir = crop_dir / cls_name
            if not cls_dir.exists():
                print(f"⚠️ Warning: Class directory does not exist: {cls_dir}")
                continue

            for file in cls_dir.iterdir():
                if file.is_file() and file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                    # When training 'all', prefix crop to prevent class name collisions
                    final_label = f"{c}_{cls_name}" if crop_key == "all" else cls_name
                    records.append({
                        "filepath": str(file.resolve()),
                        "crop": c,
                        "raw_label": cls_name,
                        "label_name": final_label,
                        "filename": file.name,
                        "filesize": file.stat().st_size
                    })

    return records

def split_dataset(
    crop: str = "corn",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
    create_dirs: bool = False
):
    print(f"\n=======================================================")
    print(f"🌱 Splitting Dataset for Target: [{crop.upper()}]")
    print(f"   Ratios -> Train: {train_ratio*100:.1f}%, Val: {val_ratio*100:.1f}%, Test: {test_ratio*100:.1f}%")
    print(f"   Seed: {seed}")
    print(f"=======================================================\n")

    records = scan_crop_images(crop)
    if not records:
        print(f"❌ Error: No images found for crop '{crop}'. Check dataset path.")
        return

    df = pd.DataFrame(records)
    print(f"Found {len(df)} total images across {df['label_name'].nunique()} classes.")

    # Assign integer label IDs
    unique_classes = sorted(df["label_name"].unique().tolist())
    class_to_id = {cls_name: i for i, cls_name in enumerate(unique_classes)}
    df["label_id"] = df["label_name"].map(class_to_id)

    # Stratified Train / (Val + Test) split
    val_test_ratio = val_ratio + test_ratio
    train_df, temp_df = train_test_split(
        df,
        test_size=val_test_ratio,
        random_state=seed,
        stratify=df["label_id"]
    )

    # Split (Val + Test) into Val and Test
    test_share_in_temp = test_ratio / val_test_ratio
    val_df, test_df = train_test_split(
        temp_df,
        test_size=test_share_in_temp,
        random_state=seed,
        stratify=temp_df["label_id"]
    )

    train_df = train_df.copy().reset_index(drop=True)
    val_df = val_df.copy().reset_index(drop=True)
    test_df = test_df.copy().reset_index(drop=True)

    # Save splits to disk
    target_split_dir = SPLITS_DIR / crop
    target_split_dir.mkdir(parents=True, exist_ok=True)

    train_csv = target_split_dir / "train.csv"
    val_csv = target_split_dir / "val.csv"
    test_csv = target_split_dir / "test.csv"

    train_df.to_csv(train_csv, index=False)
    val_df.to_csv(val_csv, index=False)
    test_df.to_csv(test_csv, index=False)

    # Optional: Create directory symlinks (train/class, val/class, test/class)
    if create_dirs:
        dir_splits = {
            "train": train_df,
            "val": val_df,
            "test": test_df
        }
        for split_name, split_data in dir_splits.items():
            for _, row in split_data.iterrows():
                dest_dir = target_split_dir / split_name / row["label_name"].replace(" ", "_")
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_file = dest_dir / row["filename"]
                if not dest_file.exists():
                    try:
                        os.symlink(row["filepath"], dest_file)
                    except OSError:
                        pass

    # Summary table
    table_data = []
    summary_dict = {
        "crop": crop,
        "total_images": len(df),
        "classes": unique_classes,
        "class_to_id": class_to_id,
        "distribution": {}
    }

    for cls_name in unique_classes:
        n_train = len(train_df[train_df["label_name"] == cls_name])
        n_val = len(val_df[val_df["label_name"] == cls_name])
        n_test = len(test_df[test_df["label_name"] == cls_name])
        n_total = n_train + n_val + n_test
        table_data.append([
            cls_name,
            f"{n_train} ({n_train/n_total*100:.1f}%)",
            f"{n_val} ({n_val/n_total*100:.1f}%)",
            f"{n_test} ({n_test/n_total*100:.1f}%)",
            n_total
        ])
        summary_dict["distribution"][cls_name] = {
            "train": n_train,
            "val": n_val,
            "test": n_test,
            "total": n_total
        }

    # Add totals row
    table_data.append([
        "TOTAL",
        f"{len(train_df)} ({len(train_df)/len(df)*100:.1f}%)",
        f"{len(val_df)} ({len(val_df)/len(df)*100:.1f}%)",
        f"{len(test_df)} ({len(test_df)/len(df)*100:.1f}%)",
        len(df)
    ])

    print(tabulate(
        table_data,
        headers=["Class Name", "Train", "Validation", "Test", "Total"],
        tablefmt="github"
    ))

    # Save summary json
    summary_path = target_split_dir / "split_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_dict, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Splits successfully saved to: {target_split_dir}")
    print(f"   - {train_csv.name} ({len(train_df)} rows)")
    print(f"   - {val_csv.name} ({len(val_df)} rows)")
    print(f"   - {test_csv.name} ({len(test_df)} rows)")
    print(f"   - {summary_path.name}")
    return summary_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stratified Train/Val/Test Splitter for Leaf AI")
    parser.add_argument("--crop", type=str, default="corn", help="Target crop: banana, mango, orange, coffee, corn, potato, or all")
    parser.add_argument("--train_ratio", type=float, default=SPLIT_CONFIG["train_ratio"], help="Train ratio (default 0.70)")
    parser.add_argument("--val_ratio", type=float, default=SPLIT_CONFIG["val_ratio"], help="Val ratio (default 0.15)")
    parser.add_argument("--test_ratio", type=float, default=SPLIT_CONFIG["test_ratio"], help="Test ratio (default 0.15)")
    parser.add_argument("--seed", type=int, default=SPLIT_CONFIG["random_seed"], help="Random seed")
    parser.add_argument("--create_dirs", action="store_true", help="Create train/val/test directories with symlinks")
    args = parser.parse_args()

    split_dataset(
        crop=args.crop,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
        create_dirs=args.create_dirs
    )
