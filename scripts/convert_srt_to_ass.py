import os
import re

def srt_time_to_ass(time_str):
    # 00:00:00,100 -> 0:00:00.10
    time_str = time_str.strip().replace(',', '.')
    parts = time_str.split(':')
    h = int(parts[0])
    m = parts[1]
    s = parts[2][:5]
    return f"{h}:{m}:{s}"

def srt_to_ass(srt_path, ass_path, title):
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()

    blocks = content.split('\n\n')
    
    header = f"""[Script Info]
Title: {title}
ScriptType: v4.00+
Collisions: Normal
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: MetaSub,Arial,28,&H00FFFFFF,&H000000FF,&H00000000,&H800F172A,-1,0,0,0,100,100,0,0,3,4,0,2,50,50,45,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            time_match = re.search(r'(\d+:\d+:\d+[,\.]\d+)\s*-->\s*(\d+:\d+:\d+[,\.]\d+)', lines[1])
            if time_match:
                start = srt_time_to_ass(time_match.group(1))
                end = srt_time_to_ass(time_match.group(2))
                text = " ".join([l.strip() for l in lines[2:]])
                events.append(f"Dialogue: 0,{start},{end},MetaSub,,0,0,0,,{text}")

    with open(ass_path, 'w', encoding='utf-8') as f:
        f.write(header + "\n".join(events))
    print(f"[+] Converted {srt_path} -> {ass_path} ({len(events)} events)")

if __name__ == "__main__":
    audio_dir = r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\audio"
    for v in ["v1", "v2", "v3"]:
        srt_f = os.path.join(audio_dir, f"voice_{v}_final.srt")
        ass_f = os.path.join(audio_dir, f"voice_{v}_final.ass")
        srt_to_ass(srt_f, ass_f, f"Meta Review Video {v}")
