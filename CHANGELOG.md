# Changelog

All notable changes to AI Sales Commander will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.5.3] - 2026-11-06

### Fixed & Enhanced
- 📱 **WhatsApp Linked Identity (LID) Routing & Delivery**:
  - Resolved outbound messaging failure where responses sent to WhatsApp Linked Identity (LID) users were routed to `{digits}@s.whatsapp.net` instead of `{digits}@lid`, causing silent drop by WhatsApp servers.
  - Updated `WhatsAppBaileysService.normalize_jid` and `parse_webhook` to detect and preserve `@lid` domains and 15-digit LIDs.
  - Updated `whatsapp-gateway/src/SessionManager.js` to normalize and route recipient addresses to `@lid` when length $\ge 15$ digits or when domain is specified.
  - Verified live delivery to user LID accounts directly via the gateway and updated historical customer records.

## [2.5.2] - 2026-11-06

### Fixed & Enhanced
- 🔄 **WhatsApp QR & Session Resiliency**:
  - Implemented automatic fallback in `get_whatsapp_integration` and `_get_whatsapp_integration` so stale integration IDs from cached browser tabs gracefully resolve to the active project WhatsApp integration instead of failing with 404 or 500 errors.
  - Enhanced `get_wa_gateway_qr` to bypass expired cached QR codes and automatically invoke `ensure_linked_device_session` whenever the gateway reports `not_found` or `disconnected`.
  - Updated `Integrations.jsx` to dynamically fallback to `getIntegrationId('whatsapp')` if `activeWhatsAppIntegrationId` is unset or stale.
  - Added direct "Device" status modal launcher to `IntegrationCard.jsx` even when in connected state, allowing instant QR re-inspection and pairing verification.
  - Added automated query cache invalidation on QR load errors in `WhatsAppQRModal.jsx` to prevent stuck loading states.

## [2.5.1] - 2026-11-06

### Fixed & Enhanced
- 📱 **WhatsApp Baileys AI Orchestrator & Outbound Messaging**:
  - Resolved `WhatsAppService.__init__() missing 1 required positional argument: 'access_token'` by dynamically resolving `WhatsAppBaileysService` for unofficial self-hosted Baileys sessions vs `WhatsAppService` for official Cloud API in `AIOrchestrator._get_integration_client`.
  - Added on-demand lazy loading fallback in `AIOrchestrator._send_message` ensuring outbound client resolution never fails even when webhook processing immediately follows QR linking.
  - Hardened `WhatsAppService` and `TelegramService` constructors to defensively accept both dictionary configuration payloads and positional parameter arguments.
  - Updated `WhatsAppBaileysService.send_message` to absorb `**kwargs` (e.g. `messaging_type`, `quick_replies`) without throwing type errors, and properly recorded outbound message IDs from gateway response bodies (`message_id` and `id`).
  - Added support for `"baileys"` and `"wa_gateway"` providers in `ServiceFactory.get_whatsapp_gateway_service`.
  - Expanded test coverage across `backend/tests/test_whatsapp_orchestrator.py` verifying full end-to-end integration client instantiation and outbound payload delivery.

## [2.5.0] - 2026-11-06

### Added & Compliance
- 🛡️ **Meta App Review 2026 Compliance Suite**:
  - Integrated full permission suite: `pages_read_user_content`, `pages_manage_engagement`, `pages_messaging`, `instagram_manage_messages`, `instagram_manage_comments`, `catalog_management`, `ads_read`, `leads_retrieval`, `ads_management`.
  - Added public `TermsOfService` page (`/terms`, `/terms-of-service`) and explicit User Data Deletion callback instructions (`/privacy-policy#data-deletion`).
  - Generated official 1024x1024 square App Icon (`Automio_App_Icon_1024x1024.png`) conforming to Meta Developer Asset Guidelines.
  - Produced 6 studio-narrated dual-screen screencasts with synchronized English subtitles, glass HUD telemetry badges, and reviewer verification checklists.

### Fixed & Enhanced
- 💬 **Social Media & Feed Ingestion Engine**:
  - Resolved customer author name resolution in Social Media Comments tab by harmonizing `author_name` and `author_username` across API and UI layers.
  - Added dedicated "Sent Reply:" visual cards displaying auto-drafted and published AI responses underneath each customer comment.
  - Implemented self-echo webhook filtering for Facebook (`page_id`) and Instagram (`ig_id`), preventing automated self-reply feedback loops.
  - Stripped artificial telemetry prefixes (`"New Comment on meta:"`) from incoming comment streams.
- 🔐 **RBAC & Authorization Hardening**:
  - Added `ADMIN` role to `ProjectRole` enum schema and domain models, enabling multi-tier administrative governance.
  - Configured project memberships for test reviewer credentials (`reviewer@automio.io`).
- ⚡ **Infrastructure & High Availability**:
  - Deployed continuous background keep-alive daemon for Render microservices to eliminate cold-start latencies during review evaluations.

## [2.4.0] - 2026-10-21

### Added & Enhanced
- 📱 **Mobile-First Responsive Engine for Admin Commander**: Implemented dynamic off-canvas slide drawer navigation with mobile backdrop overlay, auto-closing route changes, touch-friendly min 44px tap targets, and high-contrast hamburger navigation bar.
- 🎨 **Unified Automio Visual Identity**: Integrated canonical Neuro-Prism Brand Mark (`Logo` and `LogoSymbol`) and migrated design tokens from generic purple to Automio's electric sky cyan (`#0ea5e9`, `#38bdf8`) and deep obsidian slate surfaces (`#020617`, `rgba(15, 23, 42, 0.85)`).
- 📊 **Responsive Data Tables & Grid Wrappers**: Added `.table-responsive-container` with smooth horizontal touch momentum across user accounts, store fleet, billing subscriptions, webhooks, and audit log tables to prevent column compression on phone screens.
- 🛡️ **Pydantic Validation Guard for Enterprise Domains**: Enhanced `UserListItem` schema to support custom enterprise, development, and internal domain email addresses (`.local`, staging environments).

## [2.3.0] - 2026-10-21

### Added & Architecture
- 👑 **Enterprise Admin Command Center**: Comprehensive administration suite in `admin-panel` featuring executive telemetry, user management, store fleet oversight, billing overrides, AI fleet control, webhook inspector, system diagnostics, and platform toggles.
- ⚙️ **Modular Backend Admin Services**: Introduced `AdminService` and `AdminTelemetryService` in `backend/app/services/` cleanly decoupled from endpoint routers with strict Pydantic V2 data validation schemas (`admin_schemas.py`).
- 📁 **Feature-Driven Frontend Architecture**: Divided `admin-panel` strictly by feature (`/features/auth`, `/features/dashboard`, `/features/users`, `/features/projects`, `/features/billing`, `/features/ai-fleet`, `/features/webhooks`, `/features/system`, `/features/settings`) adhering to strict $\le 250$ LOC per file limits.
- ⚡ **Lightweight Global State & Path Aliasing**: Powered by Zustand store (`useAdminStore`) and configured `@/` path aliasing across Vite and IDE configs.
- 🛡️ **Role-Based Cross-Navigation**: Added conditional "Admin Commander" access in the main `frontend` sidebar dynamically surfaced for authenticated root administrators.
- 📱 **Mobile Founder & Executive Card Responsiveness**: Resolved horizontal overflow on mobile viewports for the founder profile and footer signatures across marketing pages, ensuring seamless readability in native portrait mobile mode without requiring desktop mode.

## [2.2.0] - 2026-10-20

### Added & Rebranded
- 🌐 **Automio Brand Ecosystem & Domain Routing**: Rebranded identity to **Automio** across all platform touchpoints. Connected production apex marketing site `https://automio.online` and dedicated web console `https://app.automio.online` with active Vercel DNS and SSL.
- 🛡️ **Authentication Resilience**: Implemented defensive runtime API endpoint resolution preventing masked secret failures (`[SENSITIVE]`), null-safe store state guards, and accessible form standards.
- 🔗 **Cross-Platform Navigation**: Seamless bi-directional launching between marketing landing views (`automio-website`) and secure console workflows (`frontend`).

## [2.1.0] - 2026-10-20

### Enhanced
- 🌊 **Liquid Glass Modern Architecture**: Upgraded visual identity from flat minimalism to high-depth liquid glassmorphism.
- 🔮 **Specular Light Bloom & Ambient Auroras**: Multi-layered chromatic meshes (`sky-500`, `indigo-600`, `emerald-500`) with ultra-fine directional top-edge reflection lines (`border-t-white/28`).
- 💫 **Refractive Component Primitives**: Frosted `GlassCard`, `btn-starlight` fluid gradient buttons, translucent glowing badges, and `input-fluid` frosted input beds.
- ⚡ **Vibrant Data Visualizations**: Multi-stop luminous gradient curves for AreaCharts, glowing cylindrical bar charts, and technical intelligence scanning gauges.

## [2.0.0] - 2026-10-20

### Added
- 💎 **Automio Design System 2.0**: Unified design token architecture (`tokens.css`, `themes.css`, `components.css`)
- 🎨 **Canonical Color System**: Restrained enterprise palette with semantic brand, surface, text, and status tokens
- 📐 **Modular Architecture**: 100% component decoupling with strict $\le 250$ lines of code per file across all frontend pages
- 🚀 **Standardized UI Primitives**: Enterprise-grade `Button`, `Input`, `Badge`, `Card`, `GlassCard`, `EmptyState`, `Alert`, `LoadingSpinner`, and `SkeletonLoader`
- 🛡️ **WCAG 2.2 AA Contrast Compliance**: Enhanced text contrast ratios, visible keyboard focus rings, and explicit form labeling
- 📱 **Adaptive Multi-Platform Layouts**: Fully responsive navigation and data views from 360px mobile to 1440px+ ultra-wide displays
- 🌐 **Robust i18n Fallback**: Safe translation resolution preventing raw dotted keys across multi-language views

## [1.0.0] - 2025-01-12

### Added
- 🎉 Initial release of AI Sales Commander
- ✨ FastAPI backend with async support
- 🤖 Google Gemini AI integration with function-calling
- 🔐 JWT authentication with refresh token rotation
- 📊 Multi-tenant project management
- 🔌 Integration framework for external platforms
- 🛍️ Shopify integration service
- 💬 WhatsApp Business API integration
- 📱 Telegram bot integration
- 📦 Order management and tracking
- 💬 Unified message inbox
- 📈 Analytics and reporting system
- 👷 Background workers with Celery
- 🎨 React frontend with dark glass-morphism theme
- 📱 Responsive dashboard with real-time stats
- 🤖 AI Assistant chat interface
- 🔄 WebSocket support for real-time updates
- 🐳 Docker and docker-compose configuration
- 📚 Comprehensive API documentation
- 🔒 Security guidelines and best practices
- 🧪 Testing infrastructure setup
- 🚀 CI/CD pipeline with GitHub Actions

### Security
- Implemented JWT token authentication
- Added CORS protection
- Rate limiting on API endpoints
- Input validation with Pydantic
- SQL injection prevention
- HMAC verification for webhooks
- Sensitive data masking in logs

### Documentation
- Complete README with feature list
- Detailed SETUP guide
- API documentation with examples
- Security guidelines
- Architecture overview
- Integration guides

## [Unreleased]

### Planned Features
- 📧 Email integration (Gmail, Outlook)
- 📞 Voice call support via Twilio
- 🎯 Advanced automation rules
- 📊 Custom report builder
- 🔍 Advanced search and filtering
- 📱 Mobile app (React Native)
- 🌍 Multi-language support
- 💳 Stripe payment integration
- 📈 A/B testing framework
- 🔔 Advanced notification system
- 🎨 Custom theme builder
- 🔌 Zapier integration
- 📊 Power BI/Looker connectors

---

For detailed changes, see [GitHub Releases](https://github.com/yourusername/ai-sales-commander/releases)
