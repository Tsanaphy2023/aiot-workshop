import urllib.request
import urllib.parse
import re
import json
import subprocess
import os
import sys

def clean_vtt_to_text(vtt_content):
    lines = vtt_content.splitlines()
    clean_lines = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('WEBVTT') or '-->' in line or line.isdigit():
            continue
        # Remove spaced Thai letters
        collapsed = re.sub(r'(?<=[ก-๙]) (?=[ก-๙])', '', line)
        clean_lines.append(collapsed)
    
    deduped = []
    for l in clean_lines:
        if not deduped or deduped[-1] != l:
            deduped.append(l)
    return '\n'.join(deduped)

def process_vimeo_video(module_dir, module_num, video_id):
    print(f"\n==========================================")
    print(f"Processing Module {module_num} (Vimeo ID: {video_id})")
    print(f"==========================================")
    
    url = f'https://player.vimeo.com/video/{video_id}'
    headers = {
        'Referer': 'https://www.lifelong.cmu.ac.th/lms/e5d1b14e7a47450c1f6afbba2512aac2',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching Vimeo player page: {e}")
        return False

    cfg = None
    prefix = 'window.playerConfig ='
    for s in re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL):
        if prefix in s:
            idx = s.find(prefix) + len(prefix)
            json_str = s[idx:].strip()
            if json_str.endswith(';'):
                json_str = json_str[:-1]
            try:
                cfg = json.loads(json_str)
                break
            except Exception as e:
                # try regex
                m = re.search(r'(\{.*?\});\s*(?:var|</script>|$)', json_str, re.DOTALL)
                if m:
                    cfg = json.loads(m.group(1))
                    break

    if not cfg:
        print(f"Failed to parse playerConfig for Vimeo ID {video_id}")
        return False

    title = cfg.get('video', {}).get('title', f'Module {module_num} Video')
    duration = cfg.get('video', {}).get('duration', 0)
    print(f"Video Title: {title}")
    print(f"Duration: {duration // 60}m {duration % 60}s")

    # Locate HLS URL
    cdns = cfg.get('request', {}).get('files', {}).get('hls', {}).get('cdns', {})
    hls_url = None
    for cdn_name in ['akfire_interconnect_quic', 'fastly_skyfire']:
        if cdn_name in cdns:
            hls_url = cdns[cdn_name].get('url')
            break
    if not hls_url and cdns:
        hls_url = list(cdns.values())[0].get('url')

    if not hls_url:
        print("No HLS master playlist found.")
        return False

    extracted_text_dir = os.path.join(module_dir, 'extracted_text')
    os.makedirs(extracted_text_dir, exist_ok=True)

    # Check text tracks / subtitles
    print("Checking subtitles / transcript...")
    vtt_content = None
    text_tracks = cfg.get('request', {}).get('text_tracks', [])
    for track in text_tracks:
        if track.get('lang', '').startswith('th') or 'thai' in track.get('label', '').lower():
            sub_url = track.get('url')
            if sub_url:
                try:
                    req_vtt = urllib.request.Request(sub_url, headers={'User-Agent': 'Mozilla/5.0'})
                    vtt_content = urllib.request.urlopen(req_vtt).read().decode('utf-8')
                    print(f"Found subtitle track: {track.get('label')} ({track.get('lang')})")
                    break
                except Exception as e:
                    print(f"Error fetching direct VTT: {e}")

    if not vtt_content and hls_url:
        try:
            req_hls = urllib.request.Request(hls_url, headers={'User-Agent': 'Mozilla/5.0'})
            master_m3u8 = urllib.request.urlopen(req_hls).read().decode('utf-8')
            sub_match = re.search(r'#EXT-X-MEDIA:TYPE=SUBTITLES.*?URI="([^"]+)"', master_m3u8)
            if sub_match:
                sub_rel = sub_match.group(1)
                sub_url = urllib.parse.urljoin(hls_url, sub_rel)
                req_sub = urllib.request.Request(sub_url, headers={'User-Agent': 'Mozilla/5.0'})
                sub_m3u8 = urllib.request.urlopen(req_sub).read().decode('utf-8')
                vtt_line = [line.strip() for line in sub_m3u8.splitlines() if '.vtt' in line]
                if vtt_line:
                    vtt_url = urllib.parse.urljoin(sub_url, vtt_line[0])
                    req_vtt = urllib.request.Request(vtt_url, headers={'User-Agent': 'Mozilla/5.0'})
                    vtt_content = urllib.request.urlopen(req_vtt).read().decode('utf-8')
        except Exception as e:
            print(f"Subtitle extraction fallback warning: {e}")

    if vtt_content:
        vtt_path = os.path.join(extracted_text_dir, f'Module_{module_num}_lecture_transcript.vtt')
        with open(vtt_path, 'w', encoding='utf-8') as f:
            f.write(vtt_content)
        clean_txt = clean_vtt_to_text(vtt_content)
        txt_path = os.path.join(extracted_text_dir, f'Module_{module_num}_lecture_transcript.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(clean_txt)
        print(f"✓ Lecture Transcript extracted: {txt_path} ({len(clean_txt.splitlines())} lines)")
    else:
        print("No subtitle track found.")

    # Video download
    output_video = os.path.join(module_dir, f'Module{module_num}_video.mp4')
    if os.path.exists(output_video) and os.path.getsize(output_video) > 50 * 1024 * 1024:
        print(f"✓ Video already exists: {output_video} ({os.path.getsize(output_video) / 1024 / 1024:.2f} MB), skipping download.")
        return True

    temp_video = output_video + '.tmp.mp4'
    print(f"Downloading 1080p MP4 to {output_video}...")
    ffmpeg_cmd = [
        '/opt/homebrew/bin/ffmpeg',
        '-y',
        '-headers', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\r\n',
        '-i', hls_url,
        '-map', '0:p:0:v',
        '-map', '0:p:0:a',
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        temp_video
    ]
    proc = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("Fallback ffmpeg copy without program mapping...")
        fallback_cmd = [
            '/opt/homebrew/bin/ffmpeg',
            '-y',
            '-headers', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\r\n',
            '-i', hls_url,
            '-c', 'copy',
            temp_video
        ]
        proc = subprocess.run(fallback_cmd, capture_output=True, text=True)
    
    if os.path.exists(temp_video) and os.path.getsize(temp_video) > 10 * 1024 * 1024:
        os.rename(temp_video, output_video)
        print(f"✓ Video downloaded successfully: {output_video} ({os.path.getsize(output_video) / 1024 / 1024:.2f} MB)")
        return True
    else:
        print(f"Error downloading video for Module {module_num}")
        return False

if __name__ == '__main__':
    modules = {
        '3': '1226126470',
        '4': '1226160948',
        '5': '1227611974',
        '6': '1227617395',
        '7': '1227614743',
    }
    
    base_dir = '/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot'
    for mod_num, vid_id in modules.items():
        mod_dir = os.path.join(base_dir, f'module{mod_num}')
        process_vimeo_video(mod_dir, mod_num, vid_id)
