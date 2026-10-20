import subprocess
import imageio_ffmpeg
import os
from PIL import Image

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

# Test styling: Yellow highlight or crisp white with dark translucent pill box
srt_path = r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\audio\voice_v1_final.srt".replace("\\", "/").replace(":", "\\:")

# BorderStyle=3 is an opaque bounding box behind the text
# PrimaryColour=&H00FFFFFF (White), BackColour=&HB0000000 (Black background with ~70% opacity)
style = "Fontname=Arial,FontSize=28,Bold=1,PrimaryColour=&H00FFFFFF,BackColour=&HB0000000,BorderStyle=3,Outline=1,Shadow=0,MarginV=45,Alignment=2"

filter_str = f"subtitles='{srt_path}':force_style='{style}'"

out_img = r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\test_pill_sub.jpg"

cmd = [
    ffmpeg_exe, "-y",
    "-ss", "00:00:06",
    "-i", r"c:\Users\ARKAN STOER\Desktop\777\recordings\minute_v1_cursor\page@e7888648ac88ef5e097e7b1401afbc4f.webm",
    "-vf", filter_str,
    "-vframes", "1",
    out_img
]

p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print("Code:", p.returncode)
if os.path.exists(out_img):
    im = Image.open(out_img)
    w, h = im.size
    crop = im.crop((200, int(h * 0.82), w - 200, h - 15))
    crop.save(r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\test_pill_crop.jpg")
    print("Saved crop! Size:", crop.size)
