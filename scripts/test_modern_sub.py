import subprocess
import imageio_ffmpeg
import os

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
print("Modern FFmpeg:", ffmpeg_exe)
srt_path = r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\audio\voice_v1_final.srt".replace("\\", "/").replace(":", "\\:")
filter_str = f"subtitles='{srt_path}':force_style='FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2,MarginV=30'"
cmd = [
    ffmpeg_exe, "-y",
    "-ss", "00:00:05",
    "-i", r"c:\Users\ARKAN STOER\Desktop\777\recordings\minute_v1_cursor\page@e7888648ac88ef5e097e7b1401afbc4f.webm",
    "-vf", filter_str,
    "-vframes", "1",
    r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\test_modern_sub.jpg"
]
p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print("Return code:", p.returncode)
print("Stderr tail:\n", p.stderr[-500:])
out_file = r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\test_modern_sub.jpg"
if os.path.exists(out_file):
    print("Created test_modern_sub.jpg! Size:", os.path.getsize(out_file))
