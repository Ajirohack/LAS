# LAS - Brand & Design System Guidelines

**Version:** 1.0
**Theme:** "The Live Command Center"
**Keywords:** Precision, Intelligence, Real-time, Glass, Depth.

---

## 1. Brand Identity

### Name

**LAS** (Local Agent System)

### Logo Concept

* **Symbol:** A geometric **Hexagon** (representing structure) with a **Pulse** in the center (representing the "alive" agent).
* **Wordmark:** `Inter` font, Weight 700, Tracking -0.02em.
* **Usage:**
  * **Full Logo:** Symbol + "LAS" (Sidebar Header, Login Screen).
  * **Mark Only:** Symbol (Collapsed Sidebar, Favicon).

### Favicon / App Icon

* **Background:** Solid Electric Blue (`#3B82F6`).
* **Foreground:** White Hexagon outline.
* **Sizes:**
  * `favicon.ico`: 32x32
  * `apple-touch-icon.png`: 180x180
  * `og-image.png`: 1200x630 (Social Share)

---

## 2. Color System ("Zinc & Electric")

We use a high-contrast dark mode palette to reduce eye strain and look professional.

### Primary Palette

| Role | Color Name | Hex | Tailwind Class | Usage |
|------|------------|-----|----------------|-------|
| **Background** | Void Black | `#09090B` | `bg-zinc-950` | Main app background. |
| **Surface** | Glass Zinc | `#18181B` | `bg-zinc-900/50` | Panels, Cards (with blur). |
| **Primary** | Electric Blue | `#3B82F6` | `text-blue-500` | Active states, Buttons, Links. |
| **Accent** | Neon Purple | `#A855F7` | `text-purple-500` | AI "Thinking" state, Special tools. |

### Functional Colors

| Role | Hex | Tailwind Class | Usage |
|------|-----|----------------|-------|
| **Text (Main)** | `#FAFAFA` | `text-zinc-50` | Headings, Primary content. |
| **Text (Muted)** | `#A1A1AA` | `text-zinc-400` | Metadata, Secondary labels. |
| **Border** | `#27272A` | `border-zinc-800` | Dividers, Panel outlines. |
| **Error** | `#EF4444` | `text-red-500` | Validation errors, System failures. |
| **Success** | `#10B981` | `text-emerald-500` | "Completed", "Online". |

---

## 3. Typography

### Primary Font: **Inter**

Used for all UI elements, headings, and body text. Clean, legible, modern.

* **Headings:** Weight 600/700, Tracking -0.02em.
* **Body:** Weight 400/500.

### Code Font: **JetBrains Mono**

Used for code blocks, logs, and technical data.

* **Ligatures:** Enabled (e.g., `=>`, `!=`).

### Type Scale (Desktop)

* **H1 (Page Title):** 24px (1.5rem) / Bold
* **H2 (Section):** 20px (1.25rem) / Semibold
* **H3 (Card Title):** 16px (1rem) / Medium
* **Body:** 14px (0.875rem) / Regular
* **Small/Label:** 12px (0.75rem) / Medium

---

## 4. Iconography

### Library: **Lucide React**

Consistent, stroke-based icons.

### Guidelines

* **Stroke Width:** `1.5px` (Elegant) or `2px` (Standard). Be consistent.
* **Sizes:**
  * **Small (Button/Meta):** 16px (`w-4 h-4`)
  * **Medium (Nav/Menu):** 20px (`w-5 h-5`)
  * **Large (Empty States):** 48px (`w-12 h-12`)
* **Style:** Rounded line caps.

---

## 5. Visual Style & Effects

### Glassmorphism (The "Layered" Look)

Instead of solid backgrounds, use translucency to show depth.

```css
.glass-panel {
  background: rgba(24, 24, 27, 0.5); /* Zinc-900 at 50% */
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

### Shadows & Depth

* **Drop Shadow:** Subtle, mostly for floating elements (modals, dropdowns).
  * `shadow-xl`: `0 20px 25px -5px rgb(0 0 0 / 0.5)`
* **Inner Glow:** Used on active buttons to make them "pop".

### Radius

* **Panels/Cards:** `8px` (`rounded-lg`) or `12px` (`rounded-xl`).
* **Buttons:** `6px` (`rounded-md`) or `9999px` (`rounded-full`).
* **Inputs:** `6px` (`rounded-md`).

---

## 6. Motion & Animation

### Principles

1. **Fast:** Transitions should be `0.2s` or faster.
2. **Smooth:** Use `ease-out` curves.
3. **Meaningful:** Only animate to show state change (e.g., opening a panel, sending a message).

### Key Animations

* **Pulse:** For "Thinking" or "Loading" states.
* **Slide In:** For Sidebars and Modals.
* **Fade In:** For new chat messages.

---

## 7. Imagery

* **Avatars:**
  * **User:** Initials on a gradient background (e.g., Blue -> Purple).
  * **Agent:** Provider Logo (OpenAI, Anthropic) or the LAS Hexagon.
* **Empty States:**
  * Use abstract, geometric SVG illustrations (lines, nodes, dots).
  * Avoid cartoony or hand-drawn styles. Keep it technical.
