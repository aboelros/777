import subprocess
import os

SCRIPTS = {
    "v1": {
        "text": (
            "Welcome to AI Sales Commander. In this demonstration, we showcase our unified customer care and "
            "omnichannel messaging integrations for Meta. "
            "We start in the Channels settings, where merchants connect their Facebook Pages, Instagram Professional Accounts, "
            "and WhatsApp Business numbers via Meta OAuth. "
            "Next, we navigate to the Unified Inbox. Here, incoming customer inquiries from Instagram Direct, Facebook Messenger, "
            "and WhatsApp are centralized in real-time. "
            "Support agents can view the customer's verified profile name and avatar. When a customer inquires about product sizing "
            "or availability, the merchant can immediately send a direct reply or utilize AI-suggested responses. "
            "Finally, in the Social Media module, merchants monitor public posts and incoming comments on Instagram and Facebook. "
            "With our comments triage feature, agents can promptly reply to customer questions or moderate feedback. "
            "All interactions strictly comply with Meta developer policies, respecting customer privacy and messaging windows."
        ),
        "name": "voice_v1_final"
    },
    "v2": {
        "text": (
            "In this video, we demonstrate how AI Sales Commander integrates with Meta Ads, the Marketing API, "
            "and Lead Ads retrieval. "
            "We begin in the Reports and Analytics dashboard. Using the ads read permission and Marketing API access, "
            "our platform synchronizes real-time performance metrics across active Meta advertising campaigns. "
            "Merchants can monitor essential indicators including total ad spend, impressions, click-through rates, "
            "and overall return on ad spend. "
            "Next, we transition to the CRM Deals pipeline. When prospective customers submit lead information through "
            "Meta Instant Forms or click-to-chat ads, our leads retrieval integration instantly captures their contact details. "
            "Sales teams can track each lead through pipeline stages—from initial qualification to deal closure—enabling "
            "rapid follow-ups and maximizing advertising return on investment without manual data exports."
        ),
        "name": "voice_v2_final"
    },
    "v3": {
        "text": (
            "This video highlights AI Sales Commander's integration with Meta Commerce Catalogs, Business Management, "
            "and media publishing. "
            "Under the Products module, our catalog management integration synchronizes product inventory directly with "
            "Meta Commerce Manager. Merchants can view active SKUs, stock levels, and pricing, allowing agents to instantly "
            "share verified product cards during live customer chats. "
            "Under WhatsApp Business settings, the platform monitors verified phone numbers, health status, and pre-approved "
            "notification templates via whatsapp business management. "
            "In the Social Media section, merchants can schedule and publish promotional video content directly to their "
            "Facebook Page audience using the publish video permission. "
            "Furthermore, the Live Video API enables merchants to launch interactive live shopping streams and automate "
            "real-time comment assistance during product broadcasts."
        ),
        "name": "voice_v3_final"
    }
}

def generate_voice_and_subtitles():
    audio_dir = r"c:\Users\ARKAN STOER\Desktop\777\meta_review_videos\audio"
    os.makedirs(audio_dir, exist_ok=True)
    voice = "en-US-GuyNeural"

    for key, item in SCRIPTS.items():
        base = os.path.join(audio_dir, item["name"])
        mp3 = f"{base}.mp3"
        vtt = f"{base}.vtt"
        srt = f"{base}.srt"
        
        cmd = [
            "edge-tts",
            "--voice", voice,
            "--text", item["text"],
            "--write-media", mp3,
            "--write-subtitles", vtt
        ]
        print(f"[*] Generating {item['name']}...")
        subprocess.run(cmd, check=True)
        
        # Convert VTT to standard SRT
        if os.path.exists(vtt):
            with open(vtt, "r", encoding="utf-8") as f_in:
                lines = f_in.readlines()
            
            with open(srt, "w", encoding="utf-8") as f_out:
                for line in lines:
                    if line.startswith("WEBVTT"):
                        continue
                    # replace dot with comma in timestamps if needed
                    f_out.write(line)
                    
            print(f"[+] Wrote {mp3} and {srt}")

if __name__ == "__main__":
    generate_voice_and_subtitles()
