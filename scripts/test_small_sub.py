import subprocess
import imageio_ffmpeg
from PIL import Image
import numpy as np

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
srt_v1 = r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\audio\voice_v1_final.srt".replace("\\", "/").replace(":", "\\:")
out_img = r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\test_small_sub.jpg"

# Test standard clean subtitles: FontSize=14 (scales appropriately in libass default virtual canvas), BorderStyle=1, Outline=1.5, Shadow=1, MarginV=25
style = "Fontname=Arial,FontSize=13,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1.5,Shadow=1,MarginV=25,Alignment=2"

cmd = [
    ffmpeg_exe, "-y",
    "-i", r"c:\Users\ARKAN STOER\Desktop\777\recordings\minute_v1_cursor\page@e7888648ac88ef5e097e7b1401afbc4f.webm",
    "-ss", "00:00:05",
    "-vf", f"subtitles='{srt_v1}':force_style='{style}'",
    "-vframes", "1",
    out_img
]
subprocess.run(cmd)

f_sub = Image.open(out_img)
f_raw = Image.open(r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\test_raw_frame.jpg")

arr_sub = np.array(f_sub, dtype=np.int16)
arr_raw = np.array(f_raw, dtype=np.int16)
diff = np.abs(arr_sub - arr_raw).max(axis=2)
changed_mask = diff > 30
y_idx, x_idx = np.where(changed_mask)
print("Pixels changed:", changed_mask.sum())
if len(y_idx) > 0:
    print(f"Y from {y_idx.min()} to {y_idx.max()} (Height: {y_idx.max() - y_idx.min()}px)")
    print(f"X from {x_idx.min()} to {x_idx.max()} (Width: {x_idx.max() - x_idx.min()}px)")
