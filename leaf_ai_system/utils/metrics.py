"""
Evaluation Metrics and Reporting Utilities
Calculates Accuracy, Precision, Recall, F1-score, and Confusion Matrices.
"""

import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix
)

def compute_classification_metrics(y_true, y_pred, class_names=None):
    """
    Computes comprehensive classification metrics:
    - Overall Accuracy
    - Macro and Weighted Precision, Recall, F1
    - Per-class precision, recall, f1, support
    """
    accuracy = float(accuracy_score(y_true, y_pred))
    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    prec_weighted, rec_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )

    per_class_p, per_class_r, per_class_f1, per_class_support = precision_recall_fscore_support(
        y_true, y_pred, average=None, zero_division=0
    )

    per_class_metrics = {}
    if class_names:
        for idx, name in enumerate(class_names):
            per_class_metrics[name] = {
                "precision": float(per_class_p[idx]),
                "recall": float(per_class_r[idx]),
                "f1_score": float(per_class_f1[idx]),
                "support": int(per_class_support[idx])
            }

    report_text = classification_report(
        y_true, y_pred, target_names=class_names, zero_division=0
    )

    return {
        "accuracy": accuracy,
        "macro_avg": {
            "precision": float(prec_macro),
            "recall": float(rec_macro),
            "f1_score": float(f1_macro),
        },
        "weighted_avg": {
            "precision": float(prec_weighted),
            "recall": float(rec_weighted),
            "f1_score": float(f1_weighted),
        },
        "per_class": per_class_metrics,
        "classification_report_str": report_text,
    }

def plot_confusion_matrix(y_true, y_pred, class_names, output_path: str, title: str = "Confusion Matrix"):
    """
    Renders and saves a clean, publication-ready confusion matrix heatmap.
    """
    cm = confusion_matrix(y_true, y_pred)
    cm_norm = cm.astype('float') / (cm.sum(axis=1)[:, np.newaxis] + 1e-9)

    plt.figure(figsize=(max(8, len(class_names) * 1.2), max(6, len(class_names) * 1.0)), dpi=300)
    
    # Combined count and percentage display
    annot = np.empty_like(cm).astype(str)
    nrows, ncols = cm.shape
    for i in range(nrows):
        for j in range(ncols):
            c = cm[i, j]
            p = cm_norm[i, j] * 100
            annot[i, j] = f"{c}\n({p:.1f}%)"

    sns.heatmap(
        cm_norm,
        annot=annot,
        fmt="",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
        cbar_kws={'label': 'Normalized Accuracy'},
        linewidths=0.5,
        linecolor="#e2e8f0"
    )

    plt.title(title, fontsize=14, pad=16, fontweight="bold")
    plt.xlabel("Predicted Label", fontsize=12, labelpad=10)
    plt.ylabel("Ground Truth Label", fontsize=12, labelpad=10)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_file)
    plt.close()
    return str(out_file)
