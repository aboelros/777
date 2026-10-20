# Automind — Visual Identity & Design System Specification

## 1. Brand Identity & Personality

Automind is an enterprise-grade AI sales and customer communication platform engineered for precision, operational reliability, and effortless customer management.

### Core Brand Pillars
- **Intelligence**: Precise, thoughtful, and capable AI without gimmicks or visual noise.
- **Trust**: Solid, dependable interface for business owners managing revenue, transactions, and customer relationships.
- **Clarity**: High-density operational data presented with instant visual scannability and semantic hierarchy.
- **Premium Execution**: Sophisticated dark SaaS aesthetic utilizing refined glass surfaces, subtle borders, and balanced whitespace.

---

## 2. Logo System & Usage Rules

The Automind brand mark is a precision-machined **Neuro-Prism Monogram** that fuses the **"A"** (Automation/Apex) and **"M"** (Mind/Intelligence) into an interlocking faceted structure with a luminous cognitive core.

### Anatomy & Symbol Architecture
- **Milled Obsidian Squircle**: Deep space gradient (`#0F1F38` to `#03060E`) with directional rim bevel (`#38BDF8` to `#1E293B`) and top specular reflection.
- **Apex Delta Wing ("A")**: Upward-pointing supersonic chevron in electric cyan-to-sapphire gradient.
- **Interlocking Neuro-Wings ("M")**: Dual angular facets in cobalt and indigo framing the center valley.
- **Cognitive Core (Diamond Prism)**: Radiant floating diamond with ice-cyan glow (`#FFFFFF` to `#38BDF8`), pulsing softly to signal autonomous intelligence.
- **Typography**: Geometric sans logotype pairing high-contrast pure white `AUTO` with luminous gradient `MIND` and live pulsing status dot.

### Assets & Specifications
- **Symbol (`/automind-symbol.svg`)**: 32x32px minimum digital size. High-resolution vector emblem.
- **Wordmark (`/automind-logo.svg`)**: Full lockup with typography and category tag.
- **Favicon (`/favicon.svg`)**: Ultra-legible 32x32 vector icon with reinforced contrast for browser tabs.
- **Component (`@/components/brand/Logo.jsx`)**: React component supporting `variant` (`full`, `compact`, `symbol`), numeric/preset `size`, `theme` (`dark`, `light`), and interactive hover bloom.
- **Clear Space**: Minimum exclusion zone equal to 50% of the mark width on all sides.
- **Unacceptable Usage**: Do not distort aspect ratio, modify gradient stops, or display without adequate background contrast.

---

## 3. Canonical Color System

All colors are strictly governed by CSS custom properties declared in `@/styles/tokens.css` and mapped semantically in `@/styles/themes.css`.

| Token | Value | Purpose |
|---|---|---|
| `--color-brand` | `#0ea5e9` (Sky 500) | Primary interactive actions, active states, key highlights |
| `--color-brand-hover` | `#0284c7` (Sky 600) | Hover feedback for primary buttons and interactive links |
| `--color-brand-glow` | `rgba(14, 165, 233, 0.25)` | Elevated focus rings and subtle button glow |
| `--color-bg` | `#020617` (Slate 950) | Root application background |
| `--color-surface` | `rgba(15, 23, 42, 0.75)` | Primary container cards, tables, and modal backgrounds |
| `--color-surface-hover` | `rgba(30, 41, 59, 0.8)` | Hover surface for table rows, list items, dropdown options |
| `--color-text-primary` | `#f8fafc` (Slate 50) | High-contrast headings and primary labels (14.2:1 contrast) |
| `--color-text-secondary`| `#94a3b8` (Slate 400) | Descriptions, subtitles, and secondary indicators |
| `--color-text-muted` | `#64748b` (Slate 500) | Captions, placeholders, and inactive states |
| `--color-border` | `rgba(255, 255, 255, 0.08)` | Structural borders, card outlines, table dividers |
| `--color-success` | `#10b981` (Emerald 500) | Completed orders, active connections, positive indicators |
| `--color-warning` | `#f59e0b` (Amber 500) | Rate limit warnings, approaching quotas, pending approvals |
| `--color-danger` | `#f43f5e` (Rose 500) | Destructive actions, system errors, critical alerts |

---

## 4. Typography Scale & Hierarchy

The typography system uses **Inter** (with fallback system fonts) and tabular monospace font stacks for numeric and currency calculations.

- **Page Titles**: 28px - 36px (`text-3xl` / `text-4xl`), font-bold, tracking-tight.
- **Section Headings**: 18px - 20px (`text-lg` / `text-xl`), font-semibold.
- **Card Titles & Headers**: 14px - 16px (`text-sm` / `text-base`), font-semibold.
- **Body & Table Cells**: 13px - 14px (`text-xs` / `text-sm`), font-normal, line-height 1.5.
- **Captions & Metadata**: 11px - 12px (`text-[11px]` / `text-xs`), font-medium, tracking-wide.
- **Numeric & Financial Metrics**: Tabular figures (`font-numeric` / `font-mono`) ensuring strict column alignment across tables.

---

## 5. Spacing, Radii & Surface Elevation

A consistent 4px/8px modular scale standardizes layout composition and visual depth.

- **Border Radius**:
  - `rounded-lg` (8px): Inputs, badges, small action buttons.
  - `rounded-xl` (12px): Standard cards, modal panels, table wrappers.
  - `rounded-2xl` (16px): Prominent hero cards and feature containers.
- **Elevation Layers**:
  - `Layer 0 (Background)`: `#020617` solid.
  - `Layer 1 (Surface)`: GlassCard `rgba(15, 23, 42, 0.75)` with `backdrop-blur-md` and 1px white/8% border.
  - `Layer 2 (Elevated Panels)`: Modals, dropdown menus, and popovers with `shadow-xl`.

---

## 6. Standardized UI Primitives

All UI components live in `@/components/ui/` with strictly typed prop specifications.

- **`Button`**: Variants (`primary`, `secondary`, `outline`, `ghost`, `danger`, `gradient`). Supports `leftIcon`, `rightIcon`, `isLoading`, and `fullWidth`.
- **`Input`**: Standardized text, number, and password fields with integrated leading/trailing icons, error messaging, and accessible focus rings.
- **`Badge`**: Semantic status tags (`default`, `primary`, `success`, `warning`, `danger`, `outline`) with optional pulsing dot indicator.
- **`Card` & `GlassCard`**: Consistent container surfaces providing visual depth without distracting visual artifacts.
- **`EmptyState`**: Standardized fallback states (`DataEmptyState`, `NoProjectState`) with intuitive action buttons preventing blank screens.
- **`SkeletonLoader` & `LoadingSpinner`**: Content-aware loading placeholders preventing layout shifting.

---

## 7. Responsive Guidelines & Breakpoints

- **Mobile (<640px)**: Collapsible hamburger sidebar drawer, full-width modal sheets, single-column stat grids, touch targets $\ge 44 \times 44\text{px}$.
- **Tablet (640px - 1023px)**: 2-column dashboard grids, condensed navigation, responsive tables with horizontal scroll containers.
- **Desktop (1024px+)**: Persistent 260px collapsible sidebar, multi-column analytics layouts, slide-over detail panels.

---

## 8. Accessibility & Compliance (WCAG 2.2 AA)

- All text meets or exceeds 4.5:1 contrast against dark background surfaces.
- Visible focus rings (`focus-visible:ring-2 focus-visible:ring-sky-500/50`).
- Forms include explicit `aria-label` or `<label>` associations for screen readers.
- Motion reduced when `prefers-reduced-motion` is enabled.
