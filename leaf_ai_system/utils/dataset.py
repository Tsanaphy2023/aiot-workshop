"""
Leaf Dataset and Data Loader Utilities
Provides PyTorch Dataset implementations, smart augmentations, and DataLoaders.
"""

import os
import json
import pandas as pd
from pathlib import Path
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from config import (
    SPLITS_DIR,
    TRAIN_CONFIG,
    IMAGE_MEAN,
    IMAGE_STD,
    RAW_DATASET_DIR,
    WORKSPACE_DIR,
    CROPS_CONFIG
)

def get_transforms(image_size: int = 224, is_train: bool = True):
    """
    Get image transformations with data augmentation for training,
    and deterministic resize & normalization for validation/testing.
    """
    if is_train:
        return transforms.Compose([
            transforms.Resize((image_size + 32, image_size + 32)),
            transforms.RandomResizedCrop(image_size, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.3),
            transforms.RandomRotation(degrees=20),
            transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGE_MEAN, std=IMAGE_STD),
        ])
    else:
        return transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGE_MEAN, std=IMAGE_STD),
        ])

class LeafDataset(Dataset):
    """
    Custom PyTorch Dataset for loading leaf disease/quality images from
    a manifest CSV or JSON file.
    """
    def __init__(self, manifest_path: str, transform=None):
        self.manifest_path = Path(manifest_path)
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {self.manifest_path}")

        if self.manifest_path.suffix == ".csv":
            self.df = pd.read_csv(self.manifest_path)
        elif self.manifest_path.suffix == ".json":
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.df = pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported file format: {self.manifest_path.suffix}")

        self.transform = transform
        self.classes = sorted(self.df["label_name"].unique().tolist())
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}

    def __len__(self):
        return len(self.df)

    def _resolve_image_path(self, row) -> Path:
        raw_val = str(row.get("filepath", "")).strip()
        path = Path(raw_val)
        if path.exists():
            return path

        # Normalize slashes
        norm_str = raw_val.replace("\\", "/")
        rel_subpath = None
        if "leaf workshop/" in norm_str:
            rel_subpath = norm_str.split("leaf workshop/", 1)[1]
        elif "leaf workshop" in norm_str:
            parts = norm_str.split("leaf workshop")
            rel_subpath = parts[-1].lstrip("/")

        crop = row.get("crop", None)
        folder = CROPS_CONFIG.get(crop, {}).get("folder", "") if crop else ""
        raw_label = row.get("raw_label", "")
        filename = row.get("filename", path.name)

        candidate_bases = [
            RAW_DATASET_DIR,
            WORKSPACE_DIR / "leaf workshop",
            Path("../leaf workshop").resolve(),
            Path("leaf workshop").resolve(),
            Path("/content/leaf workshop"),
            Path("/content/aiot-workshop/leaf workshop"),
            Path("/content/drive/MyDrive/leaf workshop"),
            Path("/content/drive/MyDrive/aiot-workshop/leaf workshop"),
            Path(__file__).resolve().parent.parent.parent / "leaf workshop",
            Path.cwd().parent / "leaf workshop",
            Path.cwd() / "leaf workshop"
        ]

        for base in candidate_bases:
            if not base or not base.exists():
                continue

            # Candidate 1: base / rel_subpath
            if rel_subpath:
                cand = base / rel_subpath
                if cand.exists():
                    return cand

            # Candidate 2: base / folder / raw_label / filename
            if folder and raw_label and filename:
                cand = base / folder / raw_label / filename
                if cand.exists():
                    return cand

            # Candidate 3: base / raw_label / filename
            if raw_label and filename:
                cand = base / raw_label / filename
                if cand.exists():
                    return cand

        # Check relative to cwd or workspace if not absolute
        if not path.is_absolute():
            for base in [WORKSPACE_DIR, Path.cwd(), Path.cwd().parent]:
                cand = base / path
                if cand.exists():
                    return cand

        raise FileNotFoundError(
            f"Image file not found: '{raw_val}'.\n"
            f"Could not locate image under 'leaf workshop'.\n"
            f"Checked locations: {[str(b) for b in candidate_bases if b.exists()] or 'No leaf workshop directory found'}.\n"
            f"Please verify that the dataset is uncompressed/mounted at '../leaf workshop' or '/content/leaf workshop'."
        )

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = self._resolve_image_path(row)
        label_id = int(row["label_id"])

        try:
            image = Image.open(img_path).convert("RGB")
        except Exception as e:
            raise IOError(f"Error opening image at {img_path}: {e}")

        if self.transform:
            image = self.transform(image)

        return image, label_id, str(img_path)

def get_dataloaders(crop: str = "corn", batch_size: int = None, image_size: int = None, num_workers: int = 2):
    """
    Creates and returns train, val, and test DataLoaders for a specific crop or 'all'.
    """
    batch_size = batch_size or TRAIN_CONFIG["batch_size"]
    image_size = image_size or TRAIN_CONFIG["image_size"]

    crop_split_dir = SPLITS_DIR / crop
    train_manifest = crop_split_dir / "train.csv"
    val_manifest = crop_split_dir / "val.csv"
    test_manifest = crop_split_dir / "test.csv"

    if not train_manifest.exists():
        raise FileNotFoundError(
            f"Split files not found at {crop_split_dir}. "
            f"Please run 'python scripts/01_split_dataset.py --crop {crop}' first."
        )

    # Build datasets
    train_dataset = LeafDataset(train_manifest, transform=get_transforms(image_size, is_train=True))
    val_dataset = LeafDataset(val_manifest, transform=get_transforms(image_size, is_train=False))
    test_dataset = LeafDataset(test_manifest, transform=get_transforms(image_size, is_train=False))

    # Build data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )

    metadata = {
        "crop": crop,
        "classes": train_dataset.classes,
        "num_classes": len(train_dataset.classes),
        "num_train": len(train_dataset),
        "num_val": len(val_dataset),
        "num_test": len(test_dataset),
    }

    return train_loader, val_loader, test_loader, metadata
