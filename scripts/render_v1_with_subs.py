import subprocess
import imageio_ffmpeg
import os
from PIL import Image
import numpy as np

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
base_dir = r"c:\Users\ARKAN STOER\Desktop\777"
raw_v1 = os.path.join(base_dir, "recordings", "minute_v1_cursor", "page@e7888648ac88ef5e097e7b1401afbc4f.webm")
overlay_v1 = os.path.join(base_dir, "meta_review_videos", "overlays", "overlay_v1_top.png")
audio_v1 = os.path.join(base_dir, "meta_review_videos", "audio", "voice_v1_final.mp3")
srt_v1 = os.path.join(base_dir, "meta_review_videos", "audio", "voice_v1_final.srt").replace("\\", "/").replace(":", "\\:")
out_v1 = os.path.join(base_dir, "meta_review_videos", "Meta_Review_1_Messaging_and_Social_Care_1Min.mp4")

# Style with dark slate backdrop box for 100% legibility
style = "Fontname=Arial,FontSize=26,Bold=1,PrimaryColour=&H00FFFFFF,BackColour=&HA00F172A,BorderStyle=3,Outline=1,MarginV=45,Alignment=2"
filter_str = f"[0:v][1:v]overlay=0:0[v_head];[v_head]subtitles='{srt_v1}':force_style='{style}'[vout]"

cmd = [
    ffmpeg_exe, "-y",
    "-stream_loop", "-1",
    "-i", raw_v1,
    "-i", overlay_v1,
    "-i", audio_v1,
    "-filter_complex", filter_str,
    "-map", "[vout]",
    "-map", "2:a",
    "-c:v", "libx264",
    "-preset", "fast",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    out_v1
]

print("[*] Rendering Video 1 with subtitles...")
p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print("Return code:", p.returncode)
if p.returncode != 0:
    print("Error:", p.stderr[-800:])
else:
    print(f"[+] Success! Output size: {os.path.getsize(out_v1)} bytes")

# Extract and verify 4 test frames: 5s, 18s, 35s, 55s
for ts in ["00:00:05", "00:00:18", "00:00:35", "00:00:55"]:
    f_path = f"c:\\Users\\ARKAN STOER\\Desktop\\777\\meta_review_videos\\verify_v1_{ts.replace(':', '_')}.jpg"
    sub_cmd = [ffmpeg_exe, "-y", "-ss", ts, "-i", out_v1, "-vframes", "1", f_path]
    subprocess.run(sub_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if os.path.exists(f_path):
        im = Image.open(f_path)
        arr = np.array(im)
        w, h = im.size
        # Bottom subtitle crop
        crop = arr[int(h * 0.85):h - 10, 200:w - 200]
        white_count = ((crop[:, :, 0] > 220) & (crop[:, :, 1] > 220) & (crop[:, :, 2] > 220)).sum()
        print(f"Timestamp {ts} -> Saved {f_path}, Subtitle text pixels: {white_count}")
