import urllib.request
import re
import json
import subprocess
import os
import sys

def main():
    video_id = '1225886795'
    url = f'https://player.vimeo.com/video/{video_id}'
    headers = {
        'Referer': 'https://www.lifelong.cmu.ac.th/lms/e5d1b14e7a47450c1f6afbba2512aac2',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print("Fetching fresh Vimeo player configuration...")
    req = urllib.request.Request(url, headers=headers)
    html = urllib.request.urlopen(req).read().decode('utf-8')

    hls_url = None
    for s in re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL):
        if s.strip().startswith('window.playerConfig'):
            code = s.strip()
            json_str = code.split('window.playerConfig =', 1)[1].rstrip(';')
            cfg = json.loads(json_str)
            title = cfg.get('video', {}).get('title', 'Module 1 Video')
            print(f"Found Video Title: {title}")
            cdns = cfg.get('request', {}).get('files', {}).get('hls', {}).get('cdns', {})
            # Prefer akfire or fastly
            for cdn_name in ['akfire_interconnect_quic', 'fastly_skyfire']:
                if cdn_name in cdns:
                    hls_url = cdns[cdn_name].get('url')
                    print(f"Using CDN: {cdn_name}")
                    break
            if not hls_url and cdns:
                hls_url = list(cdns.values())[0].get('url')
            break

    if not hls_url:
        print("Error: Could not find HLS URL in playerConfig", file=sys.stderr)
        sys.exit(1)

    output_file = '/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module1/Module1_video.mp4'
    temp_file = output_file + '.tmp.mp4'

    print("Starting download via ffmpeg (1080p stream)...")
    ffmpeg_cmd = [
        '/opt/homebrew/bin/ffmpeg',
        '-y',
        '-headers', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\r\n',
        '-i', hls_url,
        '-map', '0:p:0:v',  # highest quality 1080p video stream
        '-map', '0:p:0:a',  # audio stream
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        temp_file
    ]

    print("Running ffmpeg...")
    proc = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("FFmpeg error:", proc.stderr[-500:], file=sys.stderr)
        # Fallback to general copy without explicit program map
        print("Retrying with fallback stream mapping...")
        fallback_cmd = [
            '/opt/homebrew/bin/ffmpeg',
            '-y',
            '-headers', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\r\n',
            '-i', hls_url,
            '-c', 'copy',
            temp_file
        ]
        proc2 = subprocess.run(fallback_cmd, capture_output=True, text=True)
        if proc2.returncode != 0:
            print("Fallback FFmpeg error:", proc2.stderr[-500:], file=sys.stderr)
            sys.exit(1)

    if os.path.exists(temp_file):
        os.rename(temp_file, output_file)
        sz = os.path.getsize(output_file)
        print(f"Download complete: {output_file} ({sz / 1024 / 1024:.2f} MB)")
    else:
        print("Error: Output file was not created", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
