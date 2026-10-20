import subprocess
import imageio_ffmpeg
import os
from PIL import Image
import numpy as np

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

# Let's inspect voice_v1_final.ass
ass_path = r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\audio\voice_v1_final.ass".replace("\\", "/").replace(":", "\\:")
out_img = r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\test_ass_1080.jpg"

cmd = [
    ffmpeg_exe, "-y",
    "-ss", "00:00:18",
    "-i", r"c:\Users\ARKAN STOER\Desktop\777\recordings\minute_v1_cursor\page@e7888648ac88ef5e097e7b1401afbc4f.webm",
    "-vf", f"ass='{ass_path}'",
    "-vframes", "1",
    out_img
]

p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print("Return code:", p.returncode)

if os.path.exists(out_img):
    im = Image.open(out_img)
    arr = np.array(im)
    white_mask = (arr[:, :, 0] > 220) & (arr[:, :, 1] > 220) & (arr[:, :, 2] > 220)
    y_idx, x_idx = np.where(white_mask)
    if len(y_idx) > 0:
        print(f"ASS Text Y range: {y_idx.min()} to {y_idx.max()} (Height: {y_idx.max() - y_idx.min()}px)")
        print(f"ASS Text X range: {x_idx.min()} to {x_idx.max()} (Width: {x_idx.max() - x_idx.min()}px)")
    else:
        print("No white pixels detected in ASS output")
