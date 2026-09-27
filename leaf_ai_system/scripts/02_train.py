"""
Step 2: Model Training Pipeline
Trains Deep Learning models for Leaf Disease & Quality Classification.
Includes EarlyStopping, Learning Rate Scheduling, MPS/CUDA hardware acceleration,
and automated curve plotting.
"""

import sys
import os
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import json
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm

from config import (
    CHECKPOINTS_DIR,
    LOGS_DIR,
    REPORTS_DIR,
    TRAIN_CONFIG
)
from utils.dataset import get_dataloaders
from utils.visualizer import plot_training_curves
from utils.device import select_device
from models.transfer_learning import build_model

def train_epoch(model, dataloader, criterion, optimizer, device):
    """Executes a single training epoch."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    pbar = tqdm(dataloader, desc="Training", leave=False)
    for images, labels, _ in pbar:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, preds = torch.max(outputs, 1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

        pbar.set_postfix({"loss": f"{loss.item():.4f}"})

    epoch_loss = running_loss / total
    epoch_acc = correct / total
    return epoch_loss, epoch_acc

def validate_epoch(model, dataloader, criterion, device):
    """Evaluates the model on validation data."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        pbar = tqdm(dataloader, desc="Validation", leave=False)
        for images, labels, _ in pbar:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    val_loss = running_loss / total
    val_acc = correct / total
    return val_loss, val_acc

def run_training(
    crop: str = "corn",
    backbone: str = "mobilenet_v2",
    epochs: int = 15,
    batch_size: int = 32,
    lr: float = 1e-3,
    pretrained: bool = True,
    patience: int = 5
):
    print("\n" + "="*60)
    print(f"🍃 STARTING TRAINING PIPELINE: [{crop.upper()}]")
    print(f"   Backbone: {backbone} | Epochs: {epochs} | Batch: {batch_size} | LR: {lr}")
    print("="*60 + "\n")

    device = select_device()

    # Load DataLoaders
    train_loader, val_loader, test_loader, meta = get_dataloaders(
        crop=crop,
        batch_size=batch_size
    )

    num_classes = meta["num_classes"]
    classes = meta["classes"]
    print(f"Dataset stats: {meta['num_train']} train, {meta['num_val']} val, {meta['num_test']} test")
    print(f"Classes ({num_classes}): {classes}")

    # Build Model
    model = build_model(
        backbone=backbone,
        num_classes=num_classes,
        pretrained=pretrained
    ).to(device)

    # Loss & Optimizer
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)

    # Tracking History
    history = {
        "train_loss": [],
        "train_acc": [],
        "val_loss": [],
        "val_acc": [],
        "lr": []
    }

    best_val_acc = 0.0
    best_val_loss = float("inf")
    patience_counter = 0

    best_checkpoint_path = CHECKPOINTS_DIR / f"{crop}_{backbone}_best.pth"
    latest_checkpoint_path = CHECKPOINTS_DIR / f"{crop}_{backbone}_latest.pth"

    start_time = time.time()

    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        current_lr = optimizer.param_groups[0]["lr"]

        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = validate_epoch(model, val_loader, criterion, device)
        scheduler.step()

        epoch_duration = time.time() - epoch_start

        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)
        history["lr"].append(current_lr)

        print(
            f"Epoch [{epoch:02d}/{epochs:02d}] "
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc*100:.2f}% | "
            f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc*100:.2f}% | "
            f"Time: {epoch_duration:.1f}s"
        )

        # Save latest checkpoint
        torch.save({
            "epoch": epoch,
            "crop": crop,
            "backbone": backbone,
            "num_classes": num_classes,
            "classes": classes,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "val_acc": val_acc,
            "val_loss": val_loss,
            "history": history
        }, latest_checkpoint_path)

        # Check for best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_val_loss = val_loss
            patience_counter = 0

            torch.save({
                "epoch": epoch,
                "crop": crop,
                "backbone": backbone,
                "num_classes": num_classes,
                "classes": classes,
                "model_state_dict": model.state_dict(),
                "val_acc": val_acc,
                "val_loss": val_loss,
                "history": history
            }, best_checkpoint_path)
            print(f"   ⭐ New best model saved! (Val Acc: {val_acc*100:.2f}%)")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\n⏹️ Early stopping triggered at epoch {epoch} (No improvement for {patience} epochs).")
                break

    total_training_time = time.time() - start_time
    print(f"\n✨ Training finished in {total_training_time/60:.2f} minutes.")
    print(f"🏆 Best Validation Accuracy: {best_val_acc*100:.2f}%")
    print(f"📦 Checkpoint: {best_checkpoint_path}")

    # Plot & Save Training Curves
    curve_plot_path = REPORTS_DIR / f"{crop}_{backbone}_curves.png"
    plot_training_curves(history, str(curve_plot_path), title_prefix=f"{crop.capitalize()} ({backbone})")
    print(f"📈 Saved training curves to: {curve_plot_path}")

    # Save History JSON
    history_json_path = LOGS_DIR / f"{crop}_{backbone}_history.json"
    with open(history_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "crop": crop,
            "backbone": backbone,
            "best_val_acc": best_val_acc,
            "best_val_loss": best_val_loss,
            "total_epochs": len(history["train_loss"]),
            "training_time_seconds": total_training_time,
            "classes": classes,
            "history": history
        }, f, indent=2)

    return str(best_checkpoint_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Leaf Classification Model")
    parser.add_argument("--crop", type=str, default="corn", help="Target crop (banana, mango, orange, coffee, corn, potato, all)")
    parser.add_argument("--backbone", type=str, default="mobilenet_v2", help="Model backbone: mobilenet_v2, resnet18, leaf_net")
    parser.add_argument("--epochs", type=int, default=15, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Initial learning rate")
    parser.add_argument("--no_pretrained", action="store_true", help="Train from scratch without ImageNet weights")
    parser.add_argument("--patience", type=int, default=5, help="Early stopping patience")
    args = parser.parse_args()

    run_training(
        crop=args.crop,
        backbone=args.backbone,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        pretrained=not args.no_pretrained,
        patience=args.patience
    )
