"""
Object Detection & Lesion Bounding Box Analyzer
Provides automated lesion localization, bounding box generation,
and YOLO/COCO annotation utilities for plant disease & quality inspection.
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

# Class color palette for visual bounding boxes
CLASS_COLORS = {
    "Blight_Lesion": "#EF4444",      # Vibrant Red
    "Rust_Pustule": "#F59E0B",       # Amber / Orange
    "Spot_Damage": "#EC4899",        # Pink
    "Rotten_Defect": "#DC2626",      # Deep Crimson
    "Healthy_Area": "#10B981",       # Mint Green
    "Fruit_Body": "#3B82F6",         # Sky Blue
    "Ripe_Yellow": "#EAB308",        # Yellow
    "Unripe_Green": "#22C55E",       # Lime
    "Leaf_Boundary": "#06B6D4"       # Cyan
}

def calculate_iou(box1, box2):
    """
    Computes Intersection over Union (IoU) of two bounding boxes.
    Boxes format: [x, y, w, h]
    """
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1 + w1, x2 + w2)
    yi2 = min(y1 + h1, y2 + h2)

    inter_w = max(0, xi2 - xi1)
    inter_h = max(0, yi2 - yi1)
    inter_area = inter_w * inter_h

    area1 = w1 * h1
    area2 = w2 * h2
    union_area = area1 + area2 - inter_area

    if union_area <= 0:
        return 0.0
    return inter_area / union_area

def apply_nms(boxes_with_scores, iou_threshold=0.45):
    """
    Applies Non-Maximum Suppression to filter redundant overlapping boxes.
    boxes_with_scores: list of dicts with 'bbox' and 'confidence'
    """
    if not boxes_with_scores:
        return []

    # Sort descending by confidence
    sorted_boxes = sorted(boxes_with_scores, key=lambda b: b['confidence'], reverse=True)
    kept = []

    while sorted_boxes:
        current = sorted_boxes.pop(0)
        kept.append(current)
        sorted_boxes = [
            b for b in sorted_boxes
            if calculate_iou(current['bbox'], b['bbox']) < iou_threshold
        ]

    return kept

def detect_leaf_lesions_and_objects(
    image_path,
    crop_type="auto",
    conf_threshold=0.35,
    iou_threshold=0.45,
    max_detections=15
):
    """
    Detects disease lesions, necrotic spots, or fruit objects,
    producing Bounding Boxes [x, y, w, h] and YOLO normalized coordinates.
    """
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    total_pixels = width * height

    # Resize for fast multi-scale gradient analysis if image is huge
    max_dim = 800
    scale = 1.0
    if max(width, height) > max_dim:
        scale = max_dim / float(max(width, height))
        proc_w = int(width * scale)
        proc_h = int(height * scale)
        proc_img = img.resize((proc_w, proc_h), Image.Resampling.BILINEAR)
    else:
        proc_img = img.copy()
        proc_w, proc_h = width, height

    # Convert to NumPy array
    arr = np.array(proc_img, dtype=np.float32)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    # Color difference indices for plant pathology & fruit detection
    # 1. Necrotic / Brown / Lesion Index (Blight, Rust, Spot)
    # Brown/rust has high red, low green, and very low blue
    lesion_index = (r * 1.3) - (g * 0.9) - (b * 1.1)

    # 2. Yellowing / Chlorosis Index
    yellow_index = (r * 0.5 + g * 0.5) - b

    # 3. Normalized Green Leaf Index
    green_index = (2.0 * g - r - b) / (r + g + b + 1e-5)

    # Mask thresholding
    lesion_thresh = np.percentile(lesion_index, 82)
    lesion_mask = (lesion_index > lesion_thresh) & (lesion_index > 15)

    yellow_thresh = np.percentile(yellow_index, 88)
    yellow_mask = (yellow_index > yellow_thresh) & (yellow_index > 25)

    # Combine disease candidates
    candidate_mask = lesion_mask | yellow_mask

    # Simple morphological dilation using PIL MaxFilter to merge adjacent spots
    mask_img = Image.fromarray((candidate_mask * 255).astype(np.uint8))
    filtered_mask = mask_img.filter(ImageFilter.MaxFilter(size=5))
    mask_arr = np.array(filtered_mask) > 128

    # Grid-based connected component clustering
    grid_size = max(12, int(min(proc_w, proc_h) / 28))
    grid_rows = int(math.ceil(proc_h / grid_size))
    grid_cols = int(math.ceil(proc_w / grid_size))

    cells_active = []
    for gr in range(grid_rows):
        y0 = gr * grid_size
        y1 = min(proc_h, (gr + 1) * grid_size)
        for gc in range(grid_cols):
            x0 = gc * grid_size
            x1 = min(proc_w, (gc + 1) * grid_size)
            patch = mask_arr[y0:y1, x0:x1]
            if np.mean(patch) > 0.12:  # over 12% affected
                cells_active.append((gc, gr))

    # Cluster adjacent grid cells into Bounding Boxes
    visited = set()
    clusters = []

    for cell in cells_active:
        if cell in visited:
            continue
        cluster = []
        queue = [cell]
        visited.add(cell)

        while queue:
            curr = queue.pop(0)
            cluster.append(curr)
            cx, cy = curr
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
                neighbor = (cx + dx, cy + dy)
                if neighbor in cells_active and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        if len(cluster) >= 1:
            clusters.append(cluster)

    raw_detections = []
    det_id = 1

    for cl in clusters:
        min_gx = min(c[0] for c in cl)
        max_gx = max(c[0] for c in cl)
        min_gy = min(c[1] for c in cl)
        max_gy = max(c[1] for c in cl)

        # Scale coordinates back to original image
        orig_x1 = int((min_gx * grid_size) / scale)
        orig_y1 = int((min_gy * grid_size) / scale)
        orig_x2 = int(((max_gx + 1) * grid_size) / scale)
        orig_y2 = int(((max_gy + 1) * grid_size) / scale)

        # Clamp
        orig_x1 = max(0, min(width - 1, orig_x1))
        orig_y1 = max(0, min(height - 1, orig_y1))
        orig_x2 = max(orig_x1 + 8, min(width, orig_x2))
        orig_y2 = max(orig_y1 + 8, min(height, orig_y2))

        box_w = orig_x2 - orig_x1
        box_h = orig_y2 - orig_y1
        box_area = box_w * box_h

        # Ignore boxes that are too tiny or cover 95% of image
        if box_area < (width * height * 0.003) or box_area > (width * height * 0.85):
            continue

        # Extract patch to analyze specific class
        patch_lesion = lesion_index[
            int(orig_y1 * scale):int(orig_y2 * scale),
            int(orig_x1 * scale):int(orig_x2 * scale)
        ]
        mean_intensity = float(np.mean(patch_lesion)) if patch_lesion.size > 0 else 20.0

        # Heuristic classification for leaf workshop
        crop_lower = str(crop_type).lower()
        if "corn" in crop_lower or "maize" in crop_lower:
            aspect = box_h / float(max(1, box_w))
            if aspect > 1.8:
                cls_name = "Gray_Leaf_Spot"
                conf = min(0.97, max(0.45, 0.65 + (mean_intensity / 80.0)))
            elif mean_intensity > 35:
                cls_name = "Common_Rust"
                conf = min(0.96, max(0.48, 0.70 + (mean_intensity / 70.0)))
            else:
                cls_name = "Blight_Lesion"
                conf = min(0.95, max(0.42, 0.60 + (mean_intensity / 90.0)))
        elif "coffee" in crop_lower:
            if mean_intensity > 30:
                cls_name = "Rust_Pustule"
                conf = min(0.96, max(0.50, 0.68 + (mean_intensity / 60.0)))
            else:
                cls_name = "Spot_Damage"
                conf = min(0.93, max(0.40, 0.58 + (mean_intensity / 80.0)))
        elif "potato" in crop_lower:
            if box_area > (width * height * 0.08):
                cls_name = "Late_Blight_Lesion"
                conf = min(0.98, max(0.55, 0.72 + (mean_intensity / 65.0)))
            else:
                cls_name = "Early_Blight_Spot"
                conf = min(0.94, max(0.45, 0.62 + (mean_intensity / 75.0)))
        elif "orange" in crop_lower or "fruit" in crop_lower:
            if box_area > (width * height * 0.05):
                cls_name = "Fruit_Body"
                conf = min(0.98, max(0.60, 0.75 + (mean_intensity / 70.0)))
            else:
                cls_name = "Rotten_Defect"
                conf = min(0.92, max(0.42, 0.55 + (mean_intensity / 80.0)))
        else:
            # Generic auto detection
            if mean_intensity > 28:
                cls_name = "Blight_Lesion"
                conf = min(0.95, max(0.48, 0.65 + (mean_intensity / 70.0)))
            else:
                cls_name = "Spot_Damage"
                conf = min(0.91, max(0.42, 0.58 + (mean_intensity / 80.0)))

        # Severity assessment
        if conf > 0.80 or box_area > (width * height * 0.08):
            sev = "High"
        elif conf > 0.55:
            sev = "Medium"
        else:
            sev = "Low"

        # YOLO format: normalized center x, center y, width, height (0.0 to 1.0)
        norm_cx = (orig_x1 + (box_w / 2.0)) / float(width)
        norm_cy = (orig_y1 + (box_h / 2.0)) / float(height)
        norm_w = box_w / float(width)
        norm_h = box_h / float(height)

        raw_detections.append({
            "id": det_id,
            "class": cls_name,
            "confidence": round(conf, 4),
            "confidence_pct": round(conf * 100, 1),
            "bbox": [orig_x1, orig_y1, box_w, box_h],
            "yolo_bbox": [round(norm_cx, 5), round(norm_cy, 5), round(norm_w, 5), round(norm_h, 5)],
            "area_px": int(box_area),
            "area_pct": round((box_area / float(total_pixels)) * 100, 2),
            "severity": sev,
            "color": CLASS_COLORS.get(cls_name, "#EF4444")
        })
        det_id += 1

    # Filter by confidence threshold
    filtered_by_conf = [d for d in raw_detections if d['confidence'] >= conf_threshold]

    # Non-Maximum Suppression to remove redundant duplicates
    final_detections = apply_nms(filtered_by_conf, iou_threshold=iou_threshold)
    final_detections = final_detections[:max_detections]

    # Re-index ids
    for idx, d in enumerate(final_detections, 1):
        d['id'] = idx

    # If no disease found, create a healthy region indicator or report clean
    total_lesion_area = sum(d['area_px'] for d in final_detections)
    damage_pct = round((total_lesion_area / float(total_pixels)) * 100, 2)

    if not final_detections:
        diagnosis = "ไม่พบรอยโรคผิดปกติ (สภาพใบสมบูรณ์ / No Lesions Detected)"
        recommendation = "สภาพใบมีความเขียวสมบูรณ์ ไม่จำเป็นต้องพ่นสารเคมีรักษาโรค"
        health_status = "Healthy"
    elif damage_pct > 25.0:
        diagnosis = f"พบการระบาดรุนแรง (รอยโรคกระทบพื้นที่ {damage_pct}%)"
        recommendation = "ควรแยกแปลงหรือพ่นสารควบคุมชีวภัณฑ์ทันทีเพื่อป้องกันการลุกลาม"
        health_status = "Severe"
    elif damage_pct > 8.0:
        diagnosis = f"พบอาการระดับปานกลาง (รอยโรค {damage_pct}%)"
        recommendation = "ติดตามการเปลี่ยนแปลงใน 48 ชม. และลดการให้น้ำพ่นใบ"
        health_status = "Moderate"
    else:
        diagnosis = f"ตรวจพบจุดรอยโรคระยะเริ่มต้น ({len(final_detections)} ตำแหน่ง)"
        recommendation = "เฝ้าระวังแปลงและตรวจสอบความชื้นบรรยากาศ (VPD)"
        health_status = "Early"

    return {
        "image_width": width,
        "image_height": height,
        "total_detections": len(final_detections),
        "damage_area_pct": damage_pct,
        "health_status": health_status,
        "diagnosis": diagnosis,
        "recommendation": recommendation,
        "detections": final_detections
    }

def draw_bounding_boxes_on_image(image_path, detections, output_path):
    """
    Renders stylish bounding boxes with labels and confidence tags onto the image.
    """
    img = Image.open(image_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Try default font
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for d in detections:
        x, y, w, h = d['bbox']
        color_hex = d.get('color', '#EF4444')
        
        # Convert hex to RGBA
        h_color = color_hex.lstrip('#')
        rgb = tuple(int(h_color[i:i+2], 16) for i in (0, 2, 4))
        fill_rgba = rgb + (45,)    # 18% transparent fill
        border_rgba = rgb + (255,) # Solid border

        # 1. Semi-transparent fill highlight
        draw.rectangle([x, y, x + w, y + h], fill=fill_rgba, outline=border_rgba, width=3)

        # 2. Corner brackets for modern HUD look
        c_len = max(8, min(24, int(min(w, h) * 0.2)))
        for (cx, cy, dx, dy) in [
            (x, y, 1, 1),
            (x + w, y, -1, 1),
            (x, y + h, 1, -1),
            (x + w, y + h, -1, -1)
        ]:
            draw.line([(cx, cy), (cx + (dx * c_len), cy)], fill=border_rgba, width=4)
            draw.line([(cx, cy), (cx, cy + (dy * c_len))], fill=border_rgba, width=4)

        # 3. Label badge
        label_text = f"#{d['id']} {d['class']} {d['confidence_pct']}%"
        badge_w = len(label_text) * 7 + 10
        badge_h = 18
        badge_y0 = max(0, y - badge_h)
        draw.rectangle([x, badge_y0, x + badge_w, badge_y0 + badge_h], fill=border_rgba)
        draw.text((x + 5, badge_y0 + 3), label_text, fill=(255, 255, 255, 255), font=font)

    result = Image.alpha_composite(img, overlay).convert("RGB")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result.save(output_path, "JPEG", quality=92)
    return output_path
