"""
Step 5: Object Detection & Lesion Bounding Box CLI
Executes lesion localization, detects bounding boxes, and exports annotations.
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.detector import detect_leaf_lesions_and_objects, draw_bounding_boxes_on_image

def main():
    parser = argparse.ArgumentParser(description="Plant Disease Lesion & Fruit Object Detection")
    parser.add_argument("--image", type=str, required=True, help="Path to input image")
    parser.add_argument("--crop", type=str, default="auto", help="Crop type (corn, potato, coffee, orange, etc.)")
    parser.add_argument("--conf_threshold", type=float, default=0.35, help="Confidence threshold (0.1 - 0.95)")
    parser.add_argument("--iou_threshold", type=float, default=0.45, help="NMS IoU overlap threshold")
    parser.add_argument("--output_img", type=str, default="", help="Path to save annotated image with bounding boxes")
    parser.add_argument("--json", action="store_true", help="Output pure JSON format")

    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(json.dumps({"status": "error", "message": f"Image not found: {args.image}"}))
        sys.exit(1)

    result = detect_leaf_lesions_and_objects(
        image_path=args.image,
        crop_type=args.crop,
        conf_threshold=args.conf_threshold,
        iou_threshold=args.iou_threshold
    )

    # If requested, draw bounding boxes and save image
    if args.output_img:
        output_file = Path(args.output_img)
    else:
        out_dir = PROJECT_ROOT / "outputs" / "detections"
        out_dir.mkdir(parents=True, exist_ok=True)
        img_name = Path(args.image).stem
        output_file = out_dir / f"det_{img_name}.jpg"

    draw_bounding_boxes_on_image(args.image, result['detections'], str(output_file))
    result['annotated_image_path'] = str(output_file)
    result['annotated_image_filename'] = output_file.name
    result['status'] = "success"

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n" + "=" * 60)
        print("🎯 Object Detection & Bounding Box Results")
        print("=" * 60)
        print(f"📷 Image: {args.image} ({result['image_width']}x{result['image_height']})")
        print(f"📊 Detections: {result['total_detections']} objects found")
        print(f"🏥 Health Status: {result['health_status']}")
        print(f"🩺 Diagnosis: {result['diagnosis']}")
        print(f"💡 Recommendation: {result['recommendation']}")
        print(f"🖼️ Annotated Output: {output_file}")
        print("\nDetected Bounding Boxes:")
        for d in result['detections']:
            print(f"  #{d['id']} [{d['class']}] Conf: {d['confidence_pct']}% | BBox: {d['bbox']} | YOLO: {d['yolo_bbox']}")

if __name__ == "__main__":
    main()
