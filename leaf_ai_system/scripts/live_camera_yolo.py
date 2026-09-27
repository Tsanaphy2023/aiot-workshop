"""
Live Camera & Webcam Object Detection with YOLO
Supports real-time inference on Webcams, USB cameras, CSI cameras, or video files.
Works with Mosquito Larvae AI and Plant Pathology models.
"""

import sys
import time
import argparse
from pathlib import Path
try:
    import cv2
except ImportError:
    print("❌ Error: OpenCV (cv2) is not installed. Please run:")
    print("   pip install opencv-python")
    sys.exit(1)

try:
    from ultralytics import YOLO
except ImportError:
    print("❌ Error: ultralytics is not installed. Please run:")
    print("   pip install ultralytics")
    sys.exit(1)

def run_live_camera(
    model_path="yolo11n.pt",
    source=0,
    imgsz=640,
    conf_threshold=0.30,
    iou_threshold=0.45,
    save_output=False
):
    print("=" * 65)
    print("📹 Starting Real-Time Camera Object Detection HUD")
    print(f"📦 Model: {model_path}")
    print(f"🎥 Video Source: {source}")
    print(f"🎯 Confidence Threshold: {conf_threshold:.2f}")
    print("⌨️  Press 'q' or 'ESC' to exit")
    print("=" * 65)

    # 1. Load YOLO model
    print("⏳ Loading YOLO weights...")
    model = YOLO(model_path)
    class_names = model.names
    print(f"🏷️ Classes ({len(class_names)}): {class_names}")

    # 2. Open Video Capture
    # Convert source to int if it's a camera index (e.g. '0' -> 0)
    try:
        cap_source = int(source)
    except ValueError:
        cap_source = source

    cap = cv2.VideoCapture(cap_source)
    if not cap.isOpened():
        print(f"❌ Failed to open video source: {source}")
        return

    # Set camera resolution (720p preferred)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    fps_history = []
    writer = None

    if save_output:
        out_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        out_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out_path = "outputs/detections/live_camera_record.mp4"
        Path("outputs/detections").mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(out_path, fourcc, 20.0, (out_w, out_h))
        print(f"💾 Recording output to {out_path}")

    while True:
        t0 = time.time()
        ret, frame = cap.read()
        if not ret:
            print("⚠️ End of video stream or failed to grab frame.")
            break

        # 3. Run YOLO inference
        results = model.predict(
            source=frame,
            imgsz=imgsz,
            conf=conf_threshold,
            iou=iou_threshold,
            verbose=False
        )

        # 4. Render Bounding Boxes on Frame
        annotated_frame = results[0].plot()

        # Calculate FPS
        infer_time = time.time() - t0
        fps = 1.0 / max(0.001, infer_time)
        fps_history.append(fps)
        if len(fps_history) > 30:
            fps_history.pop(0)
        avg_fps = sum(fps_history) / len(fps_history)

        # Count detected objects
        boxes = results[0].boxes
        total_objects = len(boxes) if boxes is not None else 0

        # Draw HUD stats overlay
        hud_bg = annotated_frame[10:90, 10:320]
        cv2.rectangle(annotated_frame, (10, 10), (320, 90), (15, 23, 42), -1)
        cv2.rectangle(annotated_frame, (10, 10), (320, 90), (124, 58, 237), 2)
        cv2.putText(
            annotated_frame,
            f"Edge AI Live Vision | {avg_fps:.1f} FPS",
            (22, 38),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )
        cv2.putText(
            annotated_frame,
            f"Detections: {total_objects} objects",
            (22, 68),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (74, 222, 128),
            2
        )

        if writer:
            writer.write(annotated_frame)

        # Show frame in window
        cv2.imshow("YOLO Live Camera Vision (Press Q to Exit)", annotated_frame)

        # Break on 'q' or ESC
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()
    print("👋 Camera stream closed cleanly.")

def main():
    parser = argparse.ArgumentParser(description="Live Camera Object Detection with YOLO")
    parser.add_argument("--model", type=str, default="yolo11n.pt", help="Path to YOLO weights (.pt / .onnx)")
    parser.add_argument("--source", type=str, default="0", help="Camera index (0, 1) or video/RTSP stream URL")
    parser.add_argument("--imgsz", type=int, default=640, help="Inference resolution")
    parser.add_argument("--conf", type=float, default=0.30, help="Confidence threshold")
    parser.add_argument("--save", action="store_true", help="Record annotated video stream to file")
    args = parser.parse_args()

    run_live_camera(
        model_path=args.model,
        source=args.source,
        imgsz=args.imgsz,
        conf_threshold=args.conf,
        save_output=args.save
    )

if __name__ == "__main__":
    main()
