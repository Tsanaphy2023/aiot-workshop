"""
Training Visualizer Utilities
Plots Loss Curves and Accuracy Curves across epochs.
"""

from pathlib import Path
import matplotlib.pyplot as plt

def plot_training_curves(history: dict, output_path: str, title_prefix: str = "Model"):
    """
    Plots Train and Validation Loss and Accuracy side by side.
    history should be a dict with keys: 'train_loss', 'val_loss', 'train_acc', 'val_acc'.
    """
    epochs = range(1, len(history["train_loss"]) + 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

    # Loss Curve
    ax1.plot(epochs, history["train_loss"], "o-", color="#2563eb", label="Train Loss", linewidth=2)
    ax1.plot(epochs, history["val_loss"], "s--", color="#dc2626", label="Val Loss", linewidth=2)
    ax1.set_title(f"{title_prefix} - Loss Curve", fontsize=13, fontweight="bold")
    ax1.set_xlabel("Epoch", fontsize=11)
    ax1.set_ylabel("Cross Entropy Loss", fontsize=11)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(frameon=True)

    # Accuracy Curve
    ax2.plot(epochs, [a * 100 for a in history["train_acc"]], "o-", color="#16a34a", label="Train Acc (%)", linewidth=2)
    ax2.plot(epochs, [a * 100 for a in history["val_acc"]], "s--", color="#ea580c", label="Val Acc (%)", linewidth=2)
    ax2.set_title(f"{title_prefix} - Accuracy Curve", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Epoch", fontsize=11)
    ax2.set_ylabel("Accuracy (%)", fontsize=11)
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(frameon=True)

    plt.tight_layout()
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_file)
    plt.close()
    return str(out_file)
