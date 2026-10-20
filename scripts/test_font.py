import subprocess
import os

FFMPEG = r"C:\Users\ARKAN STOER\AppData\Local\Programs\Python\Python311\Scripts\ffmpeg.exe"
font_path = "C\\:/Windows/Fonts/arial.ttf"
filter_str = f"drawtext=fontfile='{font_path}':text='TESTING SUBTITLES':fontsize=40:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=10:x=(w-text_w)/2:y=h-120"
cmd = [
    FFMPEG, "-y",
    "-i", r"c:\Users\ARKAN STOER\Desktop\777\recordings\minute_v1_cursor\page@e7888648ac88ef5e097e7b1401afbc4f.webm",
    "-vf", filter_str,
    "-vframes", "1",
    r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\test_drawtext.jpg"
]
p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print("Returncode:", p.returncode)
print("Stderr tail:\n", p.stderr[-400:])
if os.path.exists(r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\test_drawtext.jpg"):
    print("JPG created! Size:", os.path.getsize(r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\test_drawtext.jpg"))
