"""
Step 3: Model Evaluation Pipeline
Evaluates trained models on the independent Test Set.
Generates Confusion Matrix heatmaps, per-class metrics, and comprehensive reports.
"""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import json
import torch
import torch.nn as nn
from tqdm import tqdm

from config import (
    CHECKPOINTS_DIR,
    REPORTS_DIR
)
from utils.dataset import get_dataloaders
from utils.metrics import compute_classification_metrics, plot_confusion_matrix
from utils.device import select_device
from models.transfer_learning import build_model

def evaluate_model(checkpoint_path: str, batch_size: int = 32):
    ckpt_path = Path(checkpoint_path)
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}")

    device = select_device()
    checkpoint = torch.load(ckpt_path, map_location=device)

    crop = checkpoint.get("crop", "corn")
    backbone = checkpoint.get("backbone", "mobilenet_v2")
    num_classes = checkpoint.get("num_classes", 4)
    classes = checkpoint.get("classes", [])

    print("\n" + "="*60)
    print(f"📊 EVALUATING MODEL ON TEST SET: [{crop.upper()}]")
    print(f"   Checkpoint: {ckpt_path.name}")
    print(f"   Backbone: {backbone} | Num Classes: {num_classes}")
    print("="*60 + "\n")

    # Load Test DataLoader
    _, _, test_loader, meta = get_dataloaders(crop=crop, batch_size=batch_size)

    # Build and load model
    model = build_model(backbone=backbone, num_classes=num_classes, pretrained=False).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    all_preds = []
    all_targets = []
    all_paths = []

    with torch.no_grad():
        for images, labels, paths in tqdm(test_loader, desc="Testing"):
            images = images.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)

            all_preds.extend(preds.cpu().tolist())
            all_targets.extend(labels.tolist())
            all_paths.extend(paths)

    # Compute metrics
    metrics = compute_classification_metrics(all_targets, all_preds, class_names=classes)

    print("\n" + "-"*50)
    print(f"🏆 TEST EVALUATION RESULTS:")
    print(f"   Accuracy:         {metrics['accuracy']*100:.2f}%")
    print(f"   Macro F1-Score:   {metrics['macro_avg']['f1_score']*100:.2f}%")
    print(f"   Weighted F1-Score:{metrics['weighted_avg']['f1_score']*100:.2f}%")
    print("-"*50)
    print("\nDetailed Classification Report:")
    print(metrics["classification_report_str"])

    # Plot Confusion Matrix
    cm_path = REPORTS_DIR / f"{crop}_{backbone}_confusion_matrix.png"
    plot_confusion_matrix(
        y_true=all_targets,
        y_pred=all_preds,
        class_names=classes,
        output_path=str(cm_path),
        title=f"Confusion Matrix: {crop.capitalize()} ({backbone})"
    )
    print(f"🖼️ Saved Confusion Matrix to: {cm_path}")

    # Save JSON Report
    report_json_path = REPORTS_DIR / f"{crop}_{backbone}_test_report.json"
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"📄 Saved JSON metrics to: {report_json_path}")

    return metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Leaf AI Model on Test Set")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to checkpoint .pth")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    args = parser.parse_args()

    evaluate_model(args.checkpoint, args.batch_size)
