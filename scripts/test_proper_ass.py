import subprocess
import imageio_ffmpeg
import os
from PIL import Image
import numpy as np

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

# Craft proper 1080p ASS file
ass_content = """[Script Info]
Title: Meta Review Video 1 - Compact Subtitles
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: MetaSub,Arial,24,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2,1,2,100,100,35,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.10,0:00:02.98,MetaSub,,0,0,0,,Welcome to AI Sales Commander.
Dialogue: 0,0:00:02.93,0:00:09.61,MetaSub,,0,0,0,,In this demonstration, we showcase our official Meta channel integration and omnichannel customer care platform.
Dialogue: 0,0:00:09.61,0:00:12.67,MetaSub,,0,0,0,,We begin in the Integrations module.
Dialogue: 0,0:00:12.67,0:00:19.87,MetaSub,,0,0,0,,To connect a channel, the merchant selects Facebook Messenger or Instagram Direct, and clicks 'Continue with Meta Business'.
Dialogue: 0,0:00:19.87,0:00:29.22,MetaSub,,0,0,0,,Through secure Meta OAuth authorization, the merchant selects their verified Facebook Page and linked Instagram Professional asset.
Dialogue: 0,0:00:29.22,0:00:33.25,MetaSub,,0,0,0,,Once connected, we transition to the Unified Inbox.
Dialogue: 0,0:00:33.25,0:00:41.08,MetaSub,,0,0,0,,Here, incoming customer conversations across Instagram Direct, Facebook Messenger, and WhatsApp are centralized in real-time.
Dialogue: 0,0:00:41.08,0:00:44.90,MetaSub,,0,0,0,,Support agents see customer profiles and avatars.
Dialogue: 0,0:00:44.90,0:00:52.26,MetaSub,,0,0,0,,When a customer asks about product availability or sizing, the merchant can immediately type and send a live direct reply.
Dialogue: 0,0:00:52.26,0:01:02.30,MetaSub,,0,0,0,,Finally, in the Social Media module, merchants monitor post comments and leverage AI assistance to triage customer inquiries promptly.
"""

ass_file = r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\audio\voice_v1_proper_1080p.ass"
with open(ass_file, "w", encoding="utf-8") as f:
    f.write(ass_content)

out_img = r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\test_proper_sub.jpg"
ass_escaped = ass_file.replace("\\", "/").replace(":", "\\:")

cmd = [
    ffmpeg_exe, "-y",
    "-i", r"c:\Users\ARKAN STOER\Desktop\777\recordings\minute_v1_cursor\page@e7888648ac88ef5e097e7b1401afbc4f.webm",
    "-ss", "00:00:05",
    "-vf", f"ass='{ass_escaped}'",
    "-vframes", "1",
    out_img
]
p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print("Return code:", p.returncode)

# Check Y range
f_sub = Image.open(out_img)
f_raw = Image.open(r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\raw_5s.jpg")

arr_sub = np.array(f_sub, dtype=np.int16)
arr_raw = np.array(f_raw, dtype=np.int16)

diff = np.abs(arr_sub - arr_raw).max(axis=2)
diff[:100, :] = 0  # ignore top header

changed = diff > 30
y_idx, x_idx = np.where(changed)
print("Total changed pixels:", changed.sum())
if len(y_idx) > 0:
    print(f"Proper Subtitle Y range: {y_idx.min()} to {y_idx.max()} (Total Height: {y_idx.max() - y_idx.min()}px)")
    print(f"Proper Subtitle X range: {x_idx.min()} to {x_idx.max()} (Total Width: {x_idx.max() - x_idx.min()}px)")
