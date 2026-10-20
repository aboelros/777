import subprocess
import imageio_ffmpeg
import os

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
srt_path = r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\audio\voice_v1_final.srt".replace("\\", "/").replace(":", "\\:")

# Style 1: Box (BorderStyle=3)
style1 = "Fontname=Arial,FontSize=26,Bold=1,PrimaryColour=&H00FFFFFF,BackColour=&HA00F172A,BorderStyle=3,Outline=1,MarginV=45,Alignment=2"

# Style 2: Black outline + drop shadow (BorderStyle=1)
style2 = "Fontname=Arial,FontSize=28,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=2,MarginV=45,Alignment=2"

for idx, (name, s) in enumerate([("box", style1), ("outline", style2)], 1):
    out_img = f"c:\\Users\\ARKAN STOER\\Desktop\\777\\meta_review_videos\\test_style_{name}.jpg"
    filter_str = f"subtitles='{srt_path}':force_style='{s}'"
    cmd = [
        ffmpeg_exe, "-y",
        "-ss", "00:00:06",
        "-i", r"c:\Users\ARKAN STOER\Desktop\777\recordings\minute_v1_cursor\page@e7888648ac88ef5e097e7b1401afbc4f.webm",
        "-vf", filter_str,
        "-vframes", "1",
        out_img
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(f"Generated {out_img}, exists: {os.path.exists(out_img)}")
