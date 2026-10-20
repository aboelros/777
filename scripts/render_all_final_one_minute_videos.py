import subprocess
import os

FFMPEG = r"C:\Users\ARKAN STOER\AppData\Local\Programs\Python\Python311\Scripts\ffmpeg.exe"
BASE_DIR = r"c:\Users\ARKAN STOER\Desktop\777"
OUT_DIR = os.path.join(BASE_DIR, "meta_review_videos")

VIDEOS = [
    {
        "id": "1",
        "name": "Meta_Review_1_Messaging_and_Social_Care_1Min.mp4",
        "raw_dir": os.path.join(BASE_DIR, "recordings", "minute_v1_cursor"),
        "overlay": os.path.join(OUT_DIR, "overlays", "overlay_v1_top.png"),
        "audio": os.path.join(OUT_DIR, "audio", "voice_v1_final.mp3"),
        "ass": os.path.join(OUT_DIR, "audio", "voice_v1_final.ass")
    },
    {
        "id": "2",
        "name": "Meta_Review_2_Ads_Leads_and_Analytics_1Min.mp4",
        "raw_dir": os.path.join(BASE_DIR, "recordings", "minute_v2_cursor"),
        "overlay": os.path.join(OUT_DIR, "overlays", "overlay_v2_top.png"),
        "audio": os.path.join(OUT_DIR, "audio", "voice_v2_final.mp3"),
        "ass": os.path.join(OUT_DIR, "audio", "voice_v2_final.ass")
    },
    {
        "id": "3",
        "name": "Meta_Review_3_Commerce_Catalog_and_Media_1Min.mp4",
        "raw_dir": os.path.join(BASE_DIR, "recordings", "minute_v3_cursor"),
        "overlay": os.path.join(OUT_DIR, "overlays", "overlay_v3_top.png"),
        "audio": os.path.join(OUT_DIR, "audio", "voice_v3_final.mp3"),
        "ass": os.path.join(OUT_DIR, "audio", "voice_v3_final.ass")
    }
]

def render_all():
    for item in VIDEOS:
        files = [f for f in os.listdir(item["raw_dir"]) if f.endswith(".webm")]
        if not files:
            print(f"[-] No webm found in {item['raw_dir']}")
            continue
        raw_video = os.path.join(item["raw_dir"], files[0])
        out_video = os.path.join(OUT_DIR, item["name"])
        ass_path = os.path.relpath(item["ass"], BASE_DIR).replace("\\", "/")

        filter_str = f"[0:v][1:v]overlay=0:0[v_head];[v_head]ass={ass_path}[vout]"

        cmd = [
            FFMPEG, "-y",
            "-i", raw_video,
            "-i", item["overlay"],
            "-i", item["audio"],
            "-filter_complex", filter_str,
            "-map", "[vout]",
            "-map", "2:a",
            "-c:v", "libx264",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-strict", "-2",
            "-ar", "44100",
            "-b:a", "128k",
            out_video
        ]

        print(f"[*] Rendering {item['name']}...")
        subprocess.run(cmd, check=True)
        print(f"[+] Finished: {out_video} ({os.path.getsize(out_video)} bytes)")

if __name__ == "__main__":
    render_all()
