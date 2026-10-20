import subprocess
import imageio_ffmpeg
import os
from PIL import Image
import numpy as np

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
base_dir = r"c:\Users\ARKAN STOER\Desktop\777"
out_dir = os.path.join(base_dir, "meta_review_videos")

VIDEOS_CONFIG = [
    {
        "id": "1",
        "name": "Meta_Review_1_Messaging_and_Social_Care_1Min.mp4",
        "raw": os.path.join(base_dir, "recordings", "minute_v1_cursor", "page@e7888648ac88ef5e097e7b1401afbc4f.webm"),
        "overlay": os.path.join(out_dir, "overlays", "overlay_v1_top.png"),
        "audio": os.path.join(out_dir, "audio", "voice_v1_final.mp3"),
        "srt": os.path.join(out_dir, "audio", "voice_v1_final.srt"),
        "test_timestamps": ["00:00:05", "00:00:18", "00:00:35", "00:00:55"]
    },
    {
        "id": "2",
        "name": "Meta_Review_2_Ads_Leads_and_Analytics_1Min.mp4",
        "raw": os.path.join(base_dir, "recordings", "minute_v2_cursor", "page@a44dddf6e64a2ce279657ec6265103e4.webm"),
        "overlay": os.path.join(out_dir, "overlays", "overlay_v2_top.png"),
        "audio": os.path.join(out_dir, "audio", "voice_v2_final.mp3"),
        "srt": os.path.join(out_dir, "audio", "voice_v2_final.srt"),
        "test_timestamps": ["00:00:05", "00:00:15", "00:00:25", "00:00:45"]
    },
    {
        "id": "3",
        "name": "Meta_Review_3_Commerce_Catalog_and_Media_1Min.mp4",
        "raw": os.path.join(base_dir, "recordings", "minute_v3_cursor", "page@841e3dcfd940930f4c13d14885f9bade.webm"),
        "overlay": os.path.join(out_dir, "overlays", "overlay_v3_top.png"),
        "audio": os.path.join(out_dir, "audio", "voice_v3_final.mp3"),
        "srt": os.path.join(out_dir, "audio", "voice_v3_final.srt"),
        "test_timestamps": ["00:00:05", "00:00:15", "00:00:25", "00:00:45"]
    }
]

# Style: High-contrast white text inside a semi-transparent dark-slate box
STYLE = "Fontname=Arial,FontSize=26,Bold=1,PrimaryColour=&H00FFFFFF,BackColour=&HA00F172A,BorderStyle=3,Outline=1,MarginV=45,Alignment=2"

def render_all():
    results = []
    for item in VIDEOS_CONFIG:
        out_path = os.path.join(out_dir, item["name"])
        srt_escaped = item["srt"].replace("\\", "/").replace(":", "\\:")
        filter_str = f"[0:v][1:v]overlay=0:0[v_head];[v_head]subtitles='{srt_escaped}':force_style='{STYLE}'[vout]"

        cmd = [
            ffmpeg_exe, "-y",
            "-stream_loop", "-1",
            "-i", item["raw"],
            "-i", item["overlay"],
            "-i", item["audio"],
            "-filter_complex", filter_str,
            "-map", "[vout]",
            "-map", "2:a",
            "-c:v", "libx264",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            out_path
        ]

        print(f"[*] Rendering {item['name']}...")
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if p.returncode != 0:
            print(f"[-] ERROR in {item['name']}: {p.stderr[-500:]}")
            continue

        file_size = os.path.getsize(out_path)
        print(f"[+] Successfully rendered {item['name']} ({file_size} bytes)")

        # Verify subtitles on sample frames
        verified_frames = []
        for ts in item["test_timestamps"]:
            f_path = os.path.join(out_dir, f"sub_verify_v{item['id']}_{ts.replace(':', '_')}.jpg")
            sub_cmd = [ffmpeg_exe, "-y", "-ss", ts, "-i", out_path, "-vframes", "1", f_path]
            subprocess.run(sub_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if os.path.exists(f_path):
                im = Image.open(f_path)
                w, h = im.size
                arr = np.array(im)
                crop = arr[int(h * 0.82):h - 10, 150:w - 150]
                white_count = int(((crop[:, :, 0] > 220) & (crop[:, :, 1] > 220) & (crop[:, :, 2] > 220)).sum())
                verified_frames.append({"timestamp": ts, "white_pixels": white_count, "frame_file": f_path})
                print(f"   -> Frame {ts}: {white_count} white subtitle pixels detected")

        results.append({
            "name": item["name"],
            "path": out_path,
            "size": file_size,
            "frames": verified_frames
        })

    return results

if __name__ == "__main__":
    res = render_all()
    print("\n[SUMMARY]")
    for r in res:
        print(f"- {r['name']}: {r['size']} bytes, verified {len(r['frames'])} subtitle frames")
