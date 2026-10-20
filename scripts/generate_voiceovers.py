import asyncio
import os
import edge_tts

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
        "name": "voice_v1"
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
        "name": "voice_v2"
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
        "name": "voice_v3"
    }
}

async def generate_all():
    os.makedirs("meta_review_videos/audio", exist_ok=True)
    voice = "en-US-GuyNeural"
    
    for key, data in SCRIPTS.items():
        base_path = os.path.join("meta_review_videos/audio", data["name"])
        mp3_path = f"{base_path}.mp3"
        vtt_path = f"{base_path}.vtt"
        srt_path = f"{base_path}.srt"
        
        communicate = edge_tts.Communicate(data["text"], voice, rate="-4%")
        submaker = edge_tts.SubMaker()
        
        with open(mp3_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.feed(chunk)
                    
        with open(vtt_path, "w", encoding="utf-8") as f:
            f.write(submaker.get_srt())
            
        # Also write clean SRT
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(submaker.get_srt())
            
        print(f"[+] Generated {mp3_path} and {srt_path}")

if __name__ == "__main__":
    asyncio.run(generate_all())
