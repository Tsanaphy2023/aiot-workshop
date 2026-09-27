"""
Configuration module for Leaf AI Workshop & Disease Classification
Centralized paths, hyperparameters, and dataset definitions.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR.parent
RAW_DATASET_DIR = WORKSPACE_DIR / "leaf workshop"

DATA_DIR = BASE_DIR / "data"
SPLITS_DIR = DATA_DIR / "splits"
OUTPUTS_DIR = BASE_DIR / "outputs"
CHECKPOINTS_DIR = OUTPUTS_DIR / "checkpoints"
LOGS_DIR = OUTPUTS_DIR / "logs"
REPORTS_DIR = OUTPUTS_DIR / "reports"

# Ensure all output directories exist
for p in [DATA_DIR, SPLITS_DIR, OUTPUTS_DIR, CHECKPOINTS_DIR, LOGS_DIR, REPORTS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Dataset Crop Definitions
CROPS_CONFIG = {
    "banana": {
        "folder": "BANANA",
        "description": "กล้วย (Banana) - คุณภาพและผลผลิต",
        "classes": ["Green banana", "Rotten banana", "Yellow banana"]
    },
    "mango": {
        "folder": "MANGO",
        "description": "มะม่วง (Mango) - คุณภาพและผลผลิต",
        "classes": ["Green mango", "Rotten Mango", "Yellow mango"]
    },
    "orange": {
        "folder": "ORANGE",
        "description": "ส้ม (Orange) - ความสุกและการเก็บเกี่ยว",
        "classes": ["orange", "Ripe orange"]
    },
    "coffee": {
        "folder": "coffee_dataset",
        "description": "กาแฟ (Coffee) - โรคราสนิมและใบไหม้",
        "classes": ["healthy", "leaf_rust", "phoma"]
    },
    "corn": {
        "folder": "corn_dataset",
        "description": "ข้าวโพด (Corn) - โรคทางใบและใบสมบูรณ์",
        "classes": ["Blight", "Common_Rust", "Gray_Leaf_Spot", "Healthy"]
    },
    "potato": {
        "folder": "potato_dataset",
        "description": "มันฝรั่ง (Potato) - โรคใบไหม้ Early & Late Blight",
        "classes": ["Potato___Early_blight", "Potato___Late_blight", "Potato___healthy"]
    }
}

# Split Ratios (Standard: 70% Train, 15% Validation, 15% Test)
SPLIT_CONFIG = {
    "train_ratio": 0.70,
    "val_ratio": 0.15,
    "test_ratio": 0.15,
    "random_seed": 42,
    "stratified": True
}

# Training Hyperparameters
TRAIN_CONFIG = {
    "image_size": 224,
    "batch_size": 32,
    "num_workers": 2,
    "learning_rate": 1e-3,
    "weight_decay": 1e-4,
    "epochs": 15,
    "early_stopping_patience": 5,
    "backbone": "mobilenet_v2",  # 'mobilenet_v2', 'resnet18', 'leaf_net'
    "pretrained": True,
    "scheduler": "cosine"  # 'cosine', 'step', 'plateau'
}

# Image Normalization Constants (ImageNet standards)
IMAGE_MEAN = [0.485, 0.456, 0.406]
IMAGE_STD = [0.229, 0.224, 0.225]
