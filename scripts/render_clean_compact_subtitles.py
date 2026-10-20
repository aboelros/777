import subprocess
import imageio_ffmpeg
import os
from PIL import Image
import numpy as np

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
base_dir = r"c:\Users\ARKAN STOER\Desktop\777"
out_dir = os.path.join(base_dir, "meta_review_videos")
audio_dir = os.path.join(out_dir, "audio")

# Define ASS templates with PlayResX=1920, PlayResY=1080, elegant clean subtitles (Height ~28px at bottom)
ASS_HEADER = """[Script Info]
Title: Meta App Review Screencast Subtitles
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: MetaSub,Arial,24,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,1,2.5,1.5,2,80,80,35,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

EVENTS_V1 = """Dialogue: 0,0:00:00.10,0:00:02.98,MetaSub,,0,0,0,,Welcome to AI Sales Commander.
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

EVENTS_V2 = """Dialogue: 0,0:00:00.10,0:00:07.81,MetaSub,,0,0,0,,In this video, we demonstrate how AI Sales Commander integrates with Meta Ads, the Marketing API, and Lead Ads retrieval.
Dialogue: 0,0:00:07.76,0:00:11.33,MetaSub,,0,0,0,,We begin in the Reports and Analytics dashboard.
Dialogue: 0,0:00:11.33,0:00:20.50,MetaSub,,0,0,0,,Using the ads read permission and Marketing API access, our platform synchronizes real-time performance metrics across active Meta advertising campaigns.
Dialogue: 0,0:00:20.50,0:00:28.52,MetaSub,,0,0,0,,Merchants can monitor essential indicators including total ad spend, impressions, click-through rates, and overall return on ad spend.
Dialogue: 0,0:00:28.52,0:00:32.43,MetaSub,,0,0,0,,Next, we transition to the CRM Deals pipeline.
Dialogue: 0,0:00:32.43,0:00:41.97,MetaSub,,0,0,0,,When prospective customers submit lead information through Meta Instant Forms or click-to-chat ads, our leads retrieval integration instantly captures their contact details.
Dialogue: 0,0:00:41.97,0:00:53.42,MetaSub,,0,0,0,,Sales teams can track each lead through pipeline stages—from initial qualification to deal closure—enabling rapid follow-ups and maximizing advertising ROI.
"""

EVENTS_V3 = """Dialogue: 0,0:00:00.10,0:00:07.60,MetaSub,,0,0,0,,This video highlights AI Sales Commander's integration with Meta Commerce Catalogs, Business Management, and media publishing.
Dialogue: 0,0:00:07.55,0:00:15.32,MetaSub,,0,0,0,,Under the Products module, our catalog management integration synchronizes product inventory directly with Meta Commerce Manager.
Dialogue: 0,0:00:15.32,0:00:24.00,MetaSub,,0,0,0,,Merchants can view active SKUs, stock levels, and pricing, allowing agents to instantly share verified product cards during live customer chats.
Dialogue: 0,0:00:24.00,0:00:33.63,MetaSub,,0,0,0,,Under WhatsApp Business settings, the platform monitors verified phone numbers, health status, and pre-approved notification templates.
Dialogue: 0,0:00:33.63,0:00:42.80,MetaSub,,0,0,0,,In the Social Media section, merchants can schedule and publish promotional video content directly to their Facebook Page audience.
Dialogue: 0,0:00:42.80,0:00:51.83,MetaSub,,0,0,0,,Furthermore, the Live Video API enables merchants to launch interactive live shopping streams and automate real-time comment assistance during product broadcasts.
"""

FILES = [
    ("voice_v1_proper.ass", EVENTS_V1),
    ("voice_v2_proper.ass", EVENTS_V2),
    ("voice_v3_proper.ass", EVENTS_V3)
]

for fname, events in FILES:
    path = os.path.join(audio_dir, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(ASS_HEADER + events)
    print(f"[+] Written {path}")

VIDEOS = [
    {
        "name": "Meta_Review_1_Messaging_and_Social_Care_1Min.mp4",
        "raw": os.path.join(base_dir, "recordings", "minute_v1_cursor", "page@e7888648ac88ef5e097e7b1401afbc4f.webm"),
        "overlay": os.path.join(out_dir, "overlays", "overlay_v1_top.png"),
        "audio": os.path.join(audio_dir, "voice_v1_final.mp3"),
        "ass": os.path.join(audio_dir, "voice_v1_proper.ass"),
        "check_ts": "00:00:05"
    },
    {
        "name": "Meta_Review_2_Ads_Leads_and_Analytics_1Min.mp4",
        "raw": os.path.join(base_dir, "recordings", "minute_v2_cursor", "page@a44dddf6e64a2ce279657ec6265103e4.webm"),
        "overlay": os.path.join(out_dir, "overlays", "overlay_v2_top.png"),
        "audio": os.path.join(audio_dir, "voice_v2_final.mp3"),
        "ass": os.path.join(audio_dir, "voice_v2_proper.ass"),
        "check_ts": "00:00:05"
    },
    {
        "name": "Meta_Review_3_Commerce_Catalog_and_Media_1Min.mp4",
        "raw": os.path.join(base_dir, "recordings", "minute_v3_cursor", "page@841e3dcfd940930f4c13d14885f9bade.webm"),
        "overlay": os.path.join(out_dir, "overlays", "overlay_v3_top.png"),
        "audio": os.path.join(audio_dir, "voice_v3_final.mp3"),
        "ass": os.path.join(audio_dir, "voice_v3_proper.ass"),
        "check_ts": "00:00:05"
    }
]

for v in VIDEOS:
    out_video = os.path.join(out_dir, v["name"])
    ass_escaped = v["ass"].replace("\\", "/").replace(":", "\\:")
    filter_str = f"[0:v][1:v]overlay=0:0[v_head];[v_head]ass='{ass_escaped}'[vout]"

    cmd = [
        ffmpeg_exe, "-y",
        "-stream_loop", "-1",
        "-i", v["raw"],
        "-i", v["overlay"],
        "-i", v["audio"],
        "-filter_complex", filter_str,
        "-map", "[vout]",
        "-map", "2:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        out_video
    ]
    print(f"[*] Rendering {v['name']} with compact subtitles...")
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        print(f"[-] Error: {p.stderr[-400:]}")
    else:
        print(f"[+] Finished: {v['name']} ({os.path.getsize(out_video)} bytes)")

        # Verify height of subtitle on test frame
        test_frame = os.path.join(out_dir, f"clean_sub_check_{v['name']}.jpg")
        subprocess.run([ffmpeg_exe, "-y", "-ss", v["check_ts"], "-i", out_video, "-vframes", "1", test_frame], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if os.path.exists(test_frame):
            im = Image.open(test_frame)
            arr = np.array(im)
            # Check bottom 200px
            crop = arr[880:, :]
            white_mask = (crop[:, :, 0] > 220) & (crop[:, :, 1] > 220) & (crop[:, :, 2] > 220)
            y_i, x_i = np.where(white_mask)
            if len(y_i) > 0:
                print(f"   -> Subtitle on screen height: {y_i.max() - y_i.min()}px (Y: {880 + y_i.min()} to {880 + y_i.max()})")
            else:
                print("   -> No subtitle detected in bottom 200px")
