"""
Model Export Utilities
Exports trained PyTorch weights (.pth) to ONNX (.onnx) and TorchScript (.pt)
for high-performance edge inference and web deployment.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import json
import torch

from models.transfer_learning import build_model
from config import CHECKPOINTS_DIR, OUTPUTS_DIR

def export_model(checkpoint_path: str, output_dir: str = None, input_size: int = 224):
    """
    Exports a trained checkpoint to ONNX and TorchScript formats.
    """
    ckpt_path = Path(checkpoint_path)
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Checkpoint not found at: {ckpt_path}")

    device = torch.device("cpu")
    checkpoint = torch.load(ckpt_path, map_location=device)

    backbone = checkpoint.get("backbone", "mobilenet_v2")
    num_classes = checkpoint.get("num_classes", 4)
    classes = checkpoint.get("classes", [])

    print(f"Loading checkpoint: {ckpt_path.name}")
    print(f"Backbone: {backbone} | Num Classes: {num_classes}")

    # Build model and load weights
    model = build_model(backbone=backbone, num_classes=num_classes, pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    out_dir = Path(output_dir) if output_dir else OUTPUTS_DIR / "exported"
    out_dir.mkdir(parents=True, exist_ok=True)

    dummy_input = torch.randn(1, 3, input_size, input_size)

    # 1. Export TorchScript
    ts_path = out_dir / f"{ckpt_path.stem}.pt"
    traced_model = torch.jit.trace(model, dummy_input)
    traced_model.save(str(ts_path))
    print(f"✅ Exported TorchScript: {ts_path}")

    # 2. Export ONNX
    onnx_path = out_dir / f"{ckpt_path.stem}.onnx"
    torch.onnx.export(
        model,
        dummy_input,
        str(onnx_path),
        export_params=True,
        opset_version=18,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
    )
    print(f"✅ Exported ONNX: {onnx_path}")

    # 3. Export Metadata JSON
    meta_path = out_dir / f"{ckpt_path.stem}_meta.json"
    meta = {
        "backbone": backbone,
        "classes": classes,
        "num_classes": num_classes,
        "input_size": [3, input_size, input_size],
        "mean": [0.485, 0.456, 0.406],
        "std": [0.229, 0.224, 0.225],
        "val_acc": checkpoint.get("val_acc", None),
        "epoch": checkpoint.get("epoch", None)
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"✅ Exported Metadata: {meta_path}")

    return {
        "torchscript": str(ts_path),
        "onnx": str(onnx_path),
        "metadata": str(meta_path)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export PyTorch model to ONNX & TorchScript")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to best_model.pth")
    parser.add_argument("--output_dir", type=str, default=None, help="Output directory for exports")
    parser.add_argument("--size", type=int, default=224, help="Input image dimension")
    args = parser.parse_args()

    export_model(args.checkpoint, args.output_dir, args.size)
