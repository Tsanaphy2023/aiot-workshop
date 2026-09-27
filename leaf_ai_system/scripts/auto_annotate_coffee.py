"""
Batch Smart Select Automated Annotation Tool for Coffee Dataset
Annotates all 150 images with Smart Select Bounding Boxes (healthy, leaf_rust, phoma)
and exports in YOLO format (images, labels, data.yaml).
"""

import os
import sys
import glob
import shutil
import zipfile
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.detector import smart_select_coffee_dataset, draw_bounding_boxes_on_image

# 3 Distinct Classes
CLASS_NAMES = ["leaf_rust", "phoma", "healthy"]
CLASS_TO_ID = {name: idx for idx, name in enumerate(CLASS_NAMES)}

def main():
    coffee_dir = WORKSPACE_ROOT / "leaf workshop" / "coffee_dataset"
    output_dir = PROJECT_ROOT / "outputs" / "coffee_smart_select_dataset"
    images_dir = output_dir / "images"
    labels_dir = output_dir / "labels"
    viz_dir = output_dir / "visualized"

    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)
    viz_dir.mkdir(parents=True, exist_ok=True)

    all_images = sorted(list(coffee_dir.glob("*/*.jpg")) + list(coffee_dir.glob("*/*.png")))
    total_imgs = len(all_images)
    print(f"☕ Starting Smart Select Annotation for {total_imgs} coffee images across 3 classes: {CLASS_NAMES}...")

    annotated_count = 0
    total_boxes = 0
    class_counts = {c: 0 for c in CLASS_NAMES}

    for idx, img_path in enumerate(all_images, 1):
        class_folder = img_path.parent.name.lower()
        img_name = img_path.stem
        
        # Copy image to output images dir
        dest_img_path = images_dir / f"{img_path.name}"
        shutil.copy2(img_path, dest_img_path)

        if "healthy" in class_folder:
            target_cls = "healthy"
        elif "rust" in class_folder:
            target_cls = "leaf_rust"
        else:
            target_cls = "phoma"

        # Run Smart Select Engine
        res = smart_select_coffee_dataset(str(img_path), target_class=target_cls)

        yolo_lines = []
        boxes_for_viz = []

        for d in res["detections"]:
            cls_name = d["class"]
            cls_id = CLASS_TO_ID.get(cls_name, 0)
            cx, cy, bw, bh = d["yolo_bbox"]

            yolo_lines.append(f"{cls_id} {cx:.5f} {cy:.5f} {bw:.5f} {bh:.5f}")
            total_boxes += 1
            class_counts[cls_name] = class_counts.get(cls_name, 0) + 1

            boxes_for_viz.append(d)

        # Write YOLO label file
        label_file = labels_dir / f"{img_path.stem}.txt"
        with open(label_file, "w", encoding="utf-8") as lf:
            lf.write("\n".join(yolo_lines) + "\n")

        # Draw visual verification images
        if idx <= 30:
            draw_bounding_boxes_on_image(str(img_path), boxes_for_viz, str(viz_dir / f"viz_{img_path.name}"))

        annotated_count += 1
        if idx % 30 == 0 or idx == total_imgs:
            print(f"  [{idx}/{total_imgs}] images processed ({(idx/total_imgs)*100:.1f}%)")

    # Create data.yaml with clear names
    yaml_content = f"""# Coffee Leaf Disease & Quality Smart Select YOLO Dataset
path: .
train: images
val: images
test: images

nc: {len(CLASS_NAMES)}
names:
  0: leaf_rust
  1: phoma
  2: healthy
"""
    yaml_file = output_dir / "data.yaml"
    with open(yaml_file, "w", encoding="utf-8") as yf:
        yf.write(yaml_content)

    # Create ZIP package for 1-click upload to Roboflow
    zip_path = PROJECT_ROOT / "outputs" / "coffee_smart_select_yolo.zip"
    print(f"\n📦 Packaging dataset into {zip_path.name}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in output_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(output_dir)
                zipf.write(file, arcname)

    print("\n" + "=" * 65)
    print("✅ Smart Select Annotation Complete!")
    print("=" * 65)
    print(f"📁 Dataset Directory: {output_dir}")
    print(f"🖼️ Images Annotated: {annotated_count} images")
    print(f"🎯 Total Smart Bounding Boxes: {total_boxes} boxes")
    print(f"📊 Class Breakdown: {class_counts}")
    print(f"📦 ZIP for Roboflow Upload: {zip_path} ({zip_path.stat().st_size / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    main()
