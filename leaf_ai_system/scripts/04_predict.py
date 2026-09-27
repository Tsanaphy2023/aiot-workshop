"""
Step 4: Inference & Prediction Pipeline
Performs leaf disease / quality inference on single images or directories.
Supports Top-K class probabilities and JSON output for API/IoT integrations.
"""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import json
from PIL import Image
import torch
import torch.nn.functional as F

from utils.dataset import get_transforms
from utils.device import select_device
from models.transfer_learning import build_model

def predict_single_image(model, image_path: str, classes: list, device: torch.device, topk: int = 3):
    """Predicts class probabilities for a single image."""
    img_path = Path(image_path)
    if not img_path.exists():
        raise FileNotFoundError(f"Image not found: {img_path}")

    image = Image.open(img_path).convert("RGB")
    transform = get_transforms(image_size=224, is_train=False)
    tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(tensor)
        probs = F.softmax(outputs, dim=1)[0]
        top_probs, top_indices = torch.topk(probs, k=min(topk, len(classes)))

    top_results = []
    for p, idx in zip(top_probs, top_indices):
        top_results.append({
            "class": classes[idx.item()],
            "confidence": round(p.item() * 100, 2)
        })

    best_class = top_results[0]["class"]
    best_conf = top_results[0]["confidence"]

    return {
        "image": str(img_path.resolve()),
        "predicted_class": best_class,
        "confidence_percent": best_conf,
        "top_k": top_results
    }

def run_prediction(checkpoint_path: str, image_path: str, topk: int = 3, as_json: bool = False):
    ckpt_path = Path(checkpoint_path)
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}")

    device = select_device()
    checkpoint = torch.load(ckpt_path, map_location=device)

    backbone = checkpoint.get("backbone", "mobilenet_v2")
    num_classes = checkpoint.get("num_classes", 4)
    classes = checkpoint.get("classes", [])

    model = build_model(backbone=backbone, num_classes=num_classes, pretrained=False).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    target_path = Path(image_path)
    if target_path.is_file():
        result = predict_single_image(model, str(target_path), classes, device, topk=topk)
        if as_json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("\n" + "="*50)
            print(f"🌿 INFERENCE RESULT: {target_path.name}")
            print(f"🎯 Prediction: {result['predicted_class']}")
            print(f"🔥 Confidence: {result['confidence_percent']}%")
            print("="*50)
            print("Top Predictions:")
            for rank, item in enumerate(result["top_k"], 1):
                print(f"  {rank}. {item['class']:<30} : {item['confidence']:>6.2f}%")
            print("="*50 + "\n")
        return result

    elif target_path.is_dir():
        results = []
        image_files = [f for f in target_path.iterdir() if f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
        print(f"\nBatch processing {len(image_files)} images from: {target_path}")

        for img_file in image_files:
            res = predict_single_image(model, str(img_file), classes, device, topk=topk)
            results.append(res)
            if not as_json:
                print(f" - {img_file.name:<35} -> {res['predicted_class']} ({res['confidence_percent']}%)")

        if as_json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        return results

    else:
        raise FileNotFoundError(f"Specified target path does not exist: {target_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inference for Leaf AI Model")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to best_model.pth")
    parser.add_argument("--image", type=str, required=True, help="Path to image file or directory")
    parser.add_argument("--topk", type=int, default=3, help="Top-K predictions")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    run_prediction(args.checkpoint, args.image, topk=args.topk, as_json=args.json)
