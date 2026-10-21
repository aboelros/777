"""
Meta App Review test account datasets - Part 2: Electronics & BioWellness.
"""

from typing import List, Dict, Any

TECH_AND_WELLNESS_ACCOUNTS: List[Dict[str, Any]] = [
    {
        "email": "meta.reviewer3@automio.online",
        "name": "Nova Electronics Admin",
        "project": {
            "name": "Nova Electronics Lab",
            "code": "NOVA-ELEC-03",
            "description": "Cutting-edge consumer smart accessories, audio gear, and ergonomic workspace tech.",
            "bot_name": "Nova Assistant",
            "bot_tone": "Technical & Concise",
            "personality_prompt": "You are a tech specialist answering customer specifications and compatibility."
        },
        "integrations": [
            {
                "provider": "facebook",
                "status": "connected",
                "config": {
                    "page_name": "Nova Electronics Lab",
                    "page_id": "102938475610293",
                    "connected_at": "2026-03-15T10:00:00Z"
                }
            },
            {
                "provider": "instagram",
                "status": "connected",
                "config": {
                    "account_name": "@novaelectronicslab",
                    "page_id": "178414002348933"
                }
            }
        ],
        "products": [
            {
                "name": "NovaPulse ANC Wireless Headphones",
                "description": "Active noise cancelling with 40-hour battery and spatial audio drivers.",
                "sku": "NOVA-HP-01",
                "price": 219.00,
                "category": "Audio",
                "stock_quantity": 50,
                "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop"]
            },
            {
                "name": "MagCharge Trio Wireless Dock",
                "description": "15W fast-charging station for phone, watch, and wireless earbuds.",
                "sku": "NOVA-CHG-02",
                "price": 79.99,
                "category": "Charging",
                "stock_quantity": 80,
                "images": ["https://images.unsplash.com/photo-1622445268045-8173426781f3?w=800&auto=format&fit=crop"]
            },
            {
                "name": "UltraView 4K HDR Webcam",
                "description": "4K 60fps streaming camera with AI auto-framing and stereo dual mics.",
                "sku": "NOVA-CAM-04",
                "price": 129.50,
                "category": "Workspace Tech",
                "stock_quantity": 35,
                "images": ["https://images.unsplash.com/photo-1588508065123-287b28e013da?w=800&auto=format&fit=crop"]
            }
        ],
        "customers": [
            {
                "customer_id": "cust_fb_davidchen",
                "name": "David Chen",
                "email": "david.chen@example.com",
                "phone": "+15556782201",
                "customer_type": "vip",
                "avatar_url": "https://i.pravatar.cc/150?u=david_chen",
                "platform_accounts": {"facebook": "fb_dchen_998"}
            },
            {
                "customer_id": "cust_fb_amandabrooks",
                "name": "Amanda Brooks",
                "email": "amanda.b@example.com",
                "phone": "+15556782202",
                "customer_type": "regular",
                "avatar_url": "https://i.pravatar.cc/150?u=amanda_brooks",
                "platform_accounts": {"facebook": "fb_abrooks_112"}
            }
        ],
        "orders": [
            {
                "customer_index": 0,
                "external_id": "ORD-NOVA-401",
                "provider": "facebook",
                "status": "shipped",
                "total": 298.99
            },
            {
                "customer_index": 1,
                "external_id": "ORD-NOVA-402",
                "provider": "facebook",
                "status": "processing",
                "total": 129.50
            }
        ],
        "messages": [
            {"customer_index": 0, "role": "user", "content": "Hi, does the NovaPulse ANC headphones come with a 2-year warranty?", "platform": "facebook"},
            {"customer_index": 0, "role": "assistant", "content": "Hello David! Yes, all NovaPulse headphones include our 2-year warranty and 30-day money-back guarantee 🎧.", "platform": "facebook"},
            {"customer_index": 0, "role": "user", "content": "Can it pair with two devices simultaneously?", "platform": "facebook"},
            {"customer_index": 0, "role": "assistant", "content": "Yes, Bluetooth Multipoint allows seamless switching between your laptop and phone ⚡.", "platform": "facebook"}
        ]
    },
    {
        "email": "meta.reviewer4@automio.online",
        "name": "Aura BioWellness Admin",
        "project": {
            "name": "Aura BioWellness Lab",
            "code": "AURA-WELL-04",
            "description": "Science-backed botanical skincare, clean wellness formulas, and organic elixirs.",
            "bot_name": "Aura Guide",
            "bot_tone": "Calm & Scientific",
            "personality_prompt": "You are a holistic wellness consultant and cosmetic formulator."
        },
        "integrations": [
            {
                "provider": "facebook",
                "status": "connected",
                "config": {
                    "page_name": "Aura BioWellness",
                    "page_id": "104928374619482"
                }
            },
            {
                "provider": "instagram",
                "status": "connected",
                "config": {
                    "account_name": "@aurabiowellness",
                    "page_id": "178414002348944"
                }
            },
            {
                "provider": "whatsapp",
                "status": "connected",
                "config": {
                    "display_phone": "+1 (555) 892-0194",
                    "phone_number_id": "104928374829104"
                }
            }
        ],
        "products": [
            {
                "name": "Cellular Radiance Vitamin C Serum",
                "description": "15% THD Ascorbate with Ferulic acid and Kakadu plum for brightening.",
                "sku": "AURA-SRM-01",
                "price": 68.00,
                "category": "Skincare",
                "stock_quantity": 45,
                "images": ["https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800&auto=format&fit=crop"]
            },
            {
                "name": "Deep Sleep Magnesium Elixir",
                "description": "Triple-chelated bioavailable magnesium with chamomile and L-theanine.",
                "sku": "AURA-SLP-03",
                "price": 42.00,
                "category": "Wellness",
                "stock_quantity": 60,
                "images": ["https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&auto=format&fit=crop"]
            },
            {
                "name": "Organic Antioxidant Greens Blend",
                "description": "Cold-pressed spirulina, wheatgrass, chlorella and digestive prebiotics.",
                "sku": "AURA-GRN-04",
                "price": 49.99,
                "category": "Nutrition",
                "stock_quantity": 30,
                "images": ["https://images.unsplash.com/photo-1540420773420-3366772f4999?w=800&auto=format&fit=crop"]
            }
        ],
        "customers": [
            {
                "customer_id": "cust_omni_drchloe",
                "name": "Dr. Chloe Bennett",
                "email": "dr.chloe@example.com",
                "phone": "+15558921101",
                "customer_type": "vip",
                "avatar_url": "https://i.pravatar.cc/150?u=dr_chloe",
                "platform_accounts": {"instagram": "@drchloewellness", "whatsapp": "+15558921101"}
            },
            {
                "customer_id": "cust_omni_jsterling",
                "name": "James Sterling",
                "email": "j.sterling@example.com",
                "phone": "+15558921102",
                "customer_type": "regular",
                "avatar_url": "https://i.pravatar.cc/150?u=j_sterling",
                "platform_accounts": {"facebook": "fb_jsterling_44"}
            }
        ],
        "orders": [
            {
                "customer_index": 0,
                "external_id": "ORD-AURA-501",
                "provider": "instagram",
                "status": "delivered",
                "total": 110.00
            },
            {
                "customer_index": 1,
                "external_id": "ORD-AURA-502",
                "provider": "whatsapp",
                "status": "processing",
                "total": 91.99
            }
        ],
        "messages": [
            {"customer_index": 0, "role": "user", "content": "Is the Cellular Radiance Vitamin C serum safe for ultra-sensitive skin?", "platform": "instagram"},
            {"customer_index": 0, "role": "assistant", "content": "Hello Dr. Bennett! Yes, it uses an encapsulated, non-acidic lipid-soluble Vitamin C 🌿.", "platform": "instagram"},
            {"customer_index": 0, "role": "user", "content": "Can I combine it with the Deep Sleep Magnesium Elixir at night?", "platform": "instagram"},
            {"customer_index": 0, "role": "assistant", "content": "Certainly! Taking the Magnesium Elixir 30 minutes before sleep works synergistically ✨.", "platform": "instagram"}
        ]
    }
]
