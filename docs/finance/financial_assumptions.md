# Automind Financial Assumptions & Data Provenance

## 1. Assumption Integrity Framework

Every financial parameter in Automind is governed by a strict metadata schema:
- **Value & Currency**: Standardized in base currency (USD) with dynamic conversion support.
- **Source**: Explicit documentation of the originating benchmark, model, or regulatory code.
- **Source Type**:
  - `actual`: Derived directly from verified production database records (Stripe, PostgreSQL).
  - `verified_external`: Official tariff tables (Meta, Google DeepMind) or national statistical bodies.
  - `user_assumption`: User-configurable simulation overrides.
  - `illustrative_default`: Calibrated baseline constants for scenario modeling.
- **Last Updated & Editability**: Explicit timestamp and permission state.

---

## 2. Infrastructure & COGS Unit Tariffs

### 2.1 AI Model Token Pricing (Google Gemini API — Q4 2024 / Q1 2025)
*Source: Google Cloud Gemini Official Documentation (Verified External)*

| Model | Input / 1M Tokens | Output / 1M Tokens | Cached / 1M Tokens | Target Latency |
| :--- | :--- | :--- | :--- | :--- |
| `gemini-2.0-flash` (Default) | \$0.10 | \$0.40 | \$0.025 | < 500ms |
| `gemini-1.5-pro` (Complex) | \$1.25 | \$5.00 | \$0.3125 | < 1500ms |

### 2.2 Messaging Channel Tariffs (Meta WhatsApp Business API — 2024/2025)
*Source: Meta for Developers Official WhatsApp Business Platform Pricing (Verified External)*

| Country | Service Conversation | Marketing Conversation | Currency Equivalent |
| :--- | :--- | :--- | :--- |
| **Egypt (EG)** | \$0.0105 | \$0.0620 | ~0.52 EGP |
| **Saudi Arabia (SA)** | \$0.0180 | \$0.0380 | ~0.068 SAR |
| **United Arab Emirates (AE)** | \$0.0165 | \$0.0350 | ~0.061 AED |
| **United States (US)** | \$0.0150 | \$0.0250 | \$0.0150 USD |
| **United Kingdom (GB)** | \$0.0200 | \$0.0450 | ~£0.0158 GBP |
| **European Union (EU)** | \$0.0200 | \$0.0450 | ~€0.0185 EUR |

### 2.3 Payment Processing Gateway (Stripe)
*Source: Stripe Pricing Schedule (Verified External)*
- **Rate**: 2.9% of gross invoice amount + \$0.30 fixed per transaction.

---

## 3. Global Market Datasets (TAM / SAM / SOM)

All regional market sizing figures cite verified national registries and statistical reports:

| Region | Active MSMEs / Merchants | Source & Citation Date | SAM Qualification Criteria |
| :--- | :--- | :--- | :--- |
| **Egypt** | 3,850,000 | Ministry of Communications and IT (MCIT) / CAPMAS 2024 | Social commerce & retail merchants on WhatsApp/Shopify |
| **Saudi Arabia** | 1,300,000 | Monsha'at SME Authority Q3 2024 Report | Registered e-commerce & retail businesses adopting digital commerce |
| **UAE** | 550,000 | Dubai Chamber of Digital Economy 2024 | Omnichannel retail and cross-border commercial merchants |
| **Other GCC** | 450,000 | GCC Statistical Centre (GCC-Stat) 2024 | Commercial businesses across Kuwait, Qatar, Bahrain, and Oman |
| **United States** | 33,200,000 | US Small Business Administration (SBA) / US Census 2024 | Shopify, WooCommerce, and conversational commerce stores |
| **United Kingdom** | 5,500,000 | UK Department for Business & Trade (DBT) 2024 | Active retail, direct-to-consumer, and customer support businesses |
| **European Union** | 24,000,000 | Eurostat European Commission SME Fact Sheets 2024 | Digitally active e-commerce and retail MSMEs across 27 member states |

---

## 4. Multi-Currency Exchange Rate Registry

Exchange rates are normalized against USD with UTC timestamps:
- **USD / EGP**: 49.50 (Central Bank of Egypt, 2024 benchmark)
- **USD / SAR**: 3.75 (Saudi Central Bank pegged rate)
- **USD / AED**: 3.6725 (Central Bank of the UAE pegged rate)
- **USD / EUR**: 0.92 (European Central Bank reference)
- **USD / GBP**: 0.79 (Bank of England reference)
