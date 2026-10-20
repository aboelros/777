import subprocess
import os
import re

V1_SCRIPT = (
    "Welcome to AI Sales Commander. In this demonstration, we showcase our official Meta channel integration "
    "and omnichannel customer care platform. "
    "We begin in the Integrations module. To connect a channel, the merchant selects Facebook Messenger or Instagram Direct, "
    "and clicks 'Continue with Meta Business'. "
    "Through secure Meta OAuth authorization, the merchant selects their verified Facebook Page and linked Instagram Professional asset, "
    "and completes the channel connection. "
    "Once connected, we transition to the Unified Inbox. Here, incoming customer conversations across Instagram Direct, "
    "Facebook Messenger, and WhatsApp are centralized in real-time. "
    "Support agents see customer profiles and avatars. When a customer asks about product availability or sizing, "
    "the merchant can immediately type and send a live direct reply. "
    "Finally, in the Social Media module, merchants monitor post comments and leverage AI assistance to triage "
    "customer inquiries promptly and comply with Meta messaging guidelines."
)

def srt_time_to_ass(time_str):
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

def regenerate_v1_audio():
    audio_dir = r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\audio"
    base = os.path.join(audio_dir, "voice_v1_final")
    mp3 = f"{base}.mp3"
    vtt = f"{base}.vtt"
    srt = f"{base}.srt"
    ass = f"{base}.ass"
    
    cmd = [
        "edge-tts",
        "--voice", "en-US-GuyNeural",
        "--text", V1_SCRIPT,
        "--write-media", mp3,
        "--write-subtitles", vtt
    ]
    subprocess.run(cmd, check=True)
    
    with open(vtt, "r", encoding="utf-8") as f_in:
        lines = f_in.readlines()
    with open(srt, "w", encoding="utf-8") as f_out:
        for line in lines:
            if not line.startswith("WEBVTT"):
                f_out.write(line)
                
    srt_to_ass(srt, ass, "Meta Review Video 1")
    print(f"[+] Regenerated V1 audio and subtitles successfully!")

if __name__ == "__main__":
    regenerate_v1_audio()
