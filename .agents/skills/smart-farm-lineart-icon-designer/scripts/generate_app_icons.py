#!/usr/bin/env python3
"""
Smart Farm Line-Art Icon Generator & Deployer
Resizes master icon into Android mipmaps, iOS AppIcon, Web icons, and Flutter assets.
"""

import os
import sys
import argparse
from PIL import Image

def generate_icons(source_path: str, project_dir: str):
    if not os.path.exists(source_path):
        print(f"Error: Source image not found at {source_path}")
        sys.exit(1)

    print(f"Loading master icon from: {source_path}")
    img = Image.open(source_path).convert("RGBA")

    # 1. Android Mipmaps
    android_res = os.path.join(project_dir, "android/app/src/main/res")
    android_sizes = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }

    if os.path.exists(android_res):
        for folder, size in android_sizes.items():
            folder_path = os.path.join(android_res, folder)
            os.makedirs(folder_path, exist_ok=True)
            out_file = os.path.join(folder_path, "ic_launcher.png")
            img.resize((size, size), Image.Resampling.LANCZOS).save(out_file, "PNG")
            print(f"  ✓ Android {folder}/ic_launcher.png ({size}x{size})")

    # 2. Web Icons & Favicon
    web_dir = os.path.join(project_dir, "web")
    if os.path.exists(web_dir):
        icons_dir = os.path.join(web_dir, "icons")
        os.makedirs(icons_dir, exist_ok=True)
        img.resize((192, 192), Image.Resampling.LANCZOS).save(os.path.join(icons_dir, "Icon-192.png"), "PNG")
        img.resize((512, 512), Image.Resampling.LANCZOS).save(os.path.join(icons_dir, "Icon-512.png"), "PNG")
        img.resize((32, 32), Image.Resampling.LANCZOS).save(os.path.join(web_dir, "favicon.png"), "PNG")
        print("  ✓ Web icons: favicon (32px), Icon-192.png, Icon-512.png")

    # 3. iOS AppIcon
    ios_icon_dir = os.path.join(project_dir, "ios/Runner/Assets.xcassets/AppIcon.appiconset")
    if os.path.exists(ios_icon_dir):
        out_file = os.path.join(ios_icon_dir, "Icon-App-1024x1024@1x.png")
        img.resize((1024, 1024), Image.Resampling.LANCZOS).save(out_file, "PNG")
        print("  ✓ iOS AppIcon 1024x1024@1x.png")

    print("\n🎉 Icon generation and deployment completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Flutter/Android/iOS/Web app icons from master image.")
    parser.add_argument("--source", default="/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/LEQs_AIoT/assets/icons/app_icon.png", help="Path to master PNG/JPG icon")
    parser.add_argument("--project-dir", default="/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/LEQs_AIoT", help="Path to Flutter project directory")
    args = parser.parse_args()

    generate_icons(args.source, args.project_dir)
