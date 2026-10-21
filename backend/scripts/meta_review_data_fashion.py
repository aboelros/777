"""
Meta App Review test account datasets - Part 1: Fashion & Gourmet.
"""

from typing import List, Dict, Any

FASHION_AND_GOURMET_ACCOUNTS: List[Dict[str, Any]] = [
    {
        "email": "meta.reviewer1@automio.online",
        "name": "Apex Fashion Admin",
        "project": {
            "name": "Apex Fashion Boutique",
            "code": "APEX-FASH-01",
            "description": "Curated contemporary apparel, luxury silk garments, and handcrafted accessories.",
            "bot_name": "Sonia",
            "bot_tone": "Chic & Helpful",
            "personality_prompt": "You are Sonia, a high-end luxury fashion styling assistant for Apex Boutique."
        },
        "integrations": [
            {
                "provider": "instagram",
                "status": "connected",
                "config": {
                    "account_name": "@apexfashionboutique",
                    "page_id": "178414002348911",
                    "connected_at": "2026-03-15T10:00:00Z"
                }
            },
            {
                "provider": "facebook",
                "status": "connected",
                "config": {
                    "page_name": "Apex Fashion Official",
                    "page_id": "109847291029384",
                    "connected_at": "2026-03-15T10:00:00Z"
                }
            }
        ],
        "products": [
            {
                "name": "Silk Evening Gown",
                "description": "100% pure Mulberry silk formal evening gown with delicate draping.",
                "sku": "APX-DRS-01",
                "price": 320.00,
                "category": "Evening Wear",
                "stock_quantity": 18,
                "images": ["https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&auto=format&fit=crop"]
            },
            {
                "name": "Italian Leather Tote",
                "description": "Hand-stitched Tuscan calfskin leather handbag with brass hardware.",
                "sku": "APX-BAG-02",
                "price": 240.00,
                "category": "Accessories",
                "stock_quantity": 25,
                "images": ["https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800&auto=format&fit=crop"]
            },
            {
                "name": "Cashmere Oversized Scarf",
                "description": "Ultra-soft grade-A Mongolian cashmere scarf for versatile styling.",
                "sku": "APX-SCF-03",
                "price": 110.00,
                "category": "Winter Wear",
                "stock_quantity": 40,
                "images": ["https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?w=800&auto=format&fit=crop"]
            }
        ],
        "customers": [
            {
                "customer_id": "cust_ig_sophiavance",
                "name": "Sophia Vance",
                "email": "sophia.vance@example.com",
                "phone": "+1555234101",
                "customer_type": "vip",
                "avatar_url": "https://i.pravatar.cc/150?u=sophia_vance",
                "platform_accounts": {"instagram": "@sophia_style"}
            },
            {
                "customer_id": "cust_ig_lucasmiller",
                "name": "Lucas Miller",
                "email": "lucas.m@example.com",
                "phone": "+1555234102",
                "customer_type": "regular",
                "avatar_url": "https://i.pravatar.cc/150?u=lucas_m",
                "platform_accounts": {"instagram": "@lucas_fits"}
            }
        ],
        "orders": [
            {
                "customer_index": 0,
                "external_id": "ORD-APX-201",
                "provider": "instagram",
                "status": "delivered",
                "total": 560.00
            },
            {
                "customer_index": 1,
                "external_id": "ORD-APX-202",
                "provider": "instagram",
                "status": "processing",
                "total": 110.00
            }
        ],
        "messages": [
            {"customer_index": 0, "role": "user", "content": "Hi! Do you have the Silk Evening Gown in Midnight Blue size M in stock?", "platform": "instagram"},
            {"customer_index": 0, "role": "assistant", "content": "Hello Sophia! Yes, we have 4 units in stock 👗. Would you like me to send a checkout link?", "platform": "instagram"},
            {"customer_index": 0, "role": "user", "content": "Yes please, could you share the checkout link?", "platform": "instagram"},
            {"customer_index": 0, "role": "assistant", "content": "Here is your checkout link: https://app.automio.online/checkout/APX-DRS-01. Thank you ✨!", "platform": "instagram"}
        ]
    },
    {
        "email": "meta.reviewer2@automio.online",
        "name": "Gourmet Roastery Admin",
        "project": {
            "name": "Gourmet Express Roastery",
            "code": "GOURMET-COF-02",
            "description": "Specialty single-origin coffee beans, cold brew equipment, and artisan brew gear.",
            "bot_name": "Barista Bot",
            "bot_tone": "Warm & Expert",
            "personality_prompt": "You are an expert barista guiding coffee lovers to the finest roasts."
        },
        "integrations": [
            {
                "provider": "whatsapp",
                "status": "connected",
                "config": {
                    "display_phone": "+1 (555) 438-2910",
                    "phone_number_id": "104928374829102",
                    "verified_name": "Gourmet Express Roastery"
                }
            },
            {
                "provider": "instagram",
                "status": "connected",
                "config": {
                    "account_name": "@gourmetexpresscoffee",
                    "page_id": "178414002348922"
                }
            }
        ],
        "products": [
            {
                "name": "Ethiopian Yirgacheffe Beans 500g",
                "description": "Light roast with fragrant floral notes, jasmine, and citrus acidity.",
                "sku": "COF-ETH-01",
                "price": 28.50,
                "category": "Coffee Beans",
                "stock_quantity": 60,
                "images": ["https://images.unsplash.com/photo-1587734195503-904fca47e0e9?w=800&auto=format&fit=crop"]
            },
            {
                "name": "Cold Brew Reserve Keg 2L",
                "description": "Micro-filtered nitrogen-infused cold brew concentrate.",
                "sku": "COF-CLD-02",
                "price": 42.00,
                "category": "Ready to Drink",
                "stock_quantity": 30,
                "images": ["https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=800&auto=format&fit=crop"]
            },
            {
                "name": "Conical Burr Grinder Pro",
                "description": "40mm stainless steel burrs with 30 precise grind settings.",
                "sku": "COF-GRN-03",
                "price": 165.00,
                "category": "Brew Equipment",
                "stock_quantity": 15,
                "images": ["https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=800&auto=format&fit=crop"]
            }
        ],
        "customers": [
            {
                "customer_id": "cust_wa_marcusthorne",
                "name": "Marcus Thorne",
                "email": "marcus.t@example.com",
                "phone": "+15554381122",
                "customer_type": "vip",
                "avatar_url": "https://i.pravatar.cc/150?u=marcus_t",
                "platform_accounts": {"whatsapp": "+15554381122"}
            },
            {
                "customer_id": "cust_wa_elenarostova",
                "name": "Elena Rostova",
                "email": "elena.r@example.com",
                "phone": "+15554383344",
                "customer_type": "regular",
                "avatar_url": "https://i.pravatar.cc/150?u=elena_r",
                "platform_accounts": {"whatsapp": "+15554383344"}
            }
        ],
        "orders": [
            {
                "customer_index": 0,
                "external_id": "ORD-GOUR-301",
                "provider": "whatsapp",
                "status": "delivered",
                "total": 70.50
            },
            {
                "customer_index": 1,
                "external_id": "ORD-GOUR-302",
                "provider": "whatsapp",
                "status": "processing",
                "total": 165.00
            }
        ],
        "messages": [
            {"customer_index": 0, "role": "user", "content": "Hey! What is the roast date on the Ethiopian Yirgacheffe batch?", "platform": "whatsapp"},
            {"customer_index": 0, "role": "assistant", "content": "Hello Marcus! All batches are roasted fresh every Tuesday and Friday ☕. These were roasted yesterday!", "platform": "whatsapp"},
            {"customer_index": 0, "role": "user", "content": "Awesome, can I get it ground for V60 pour over?", "platform": "whatsapp"},
            {"customer_index": 0, "role": "assistant", "content": "Absolutely! We will grind it to medium-fine specifically optimized for V60 before sealing.", "platform": "whatsapp"}
        ]
    }
]
