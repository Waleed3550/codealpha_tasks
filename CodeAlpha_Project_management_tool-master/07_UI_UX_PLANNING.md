# STEP 7: UI/UX PLANNING

## 1. Design System Philosophy
The platform will utilize a custom, highly polished Vanilla CSS (CSS Modules) design system. It prioritizes a premium, "wow-factor" aesthetic utilizing glassmorphism, dynamic micro-animations, and a sense of depth, avoiding flat generic utility-class designs.

## 2. Core Tokens

*   **Color Palette:**
    *   **Primary:** A vibrant, futuristic brand color (e.g., HSL 250, 100%, 65% - Electric Indigo).
    *   **Surface:** Layered dark/light backgrounds to create depth (e.g., `var(--surface-1)` for main background, `var(--surface-2)` for cards).
    *   **Accents:** Success (Emerald), Warning (Amber), Danger (Rose) tailored to match the primary saturation.
*   **Typography:**
    *   **Headings:** `Outfit` or `Inter` (sans-serif, tight tracking for a modern tech feel).
    *   **Body:** `Inter` (highly legible at small sizes).
    *   **Code:** `JetBrains Mono` or `Fira Code` (for the block editor and technical fields).
*   **Spacing & Grid:**
    *   Uses an 8px baseline grid (`--space-1: 4px`, `--space-2: 8px`, `--space-4: 16px`, etc.).
    *   Layouts rely on CSS Grid for macro-architecture and Flexbox for micro-components.

## 3. Components Library

*   **Buttons:** Soft shadows, subtle gradients on primary buttons. Hover states include slight scaling (`scale: 1.02`) and brightness adjustments.
*   **Cards:** Glassmorphic properties (`backdrop-filter: blur(12px)`, semi-transparent borders).
*   **Forms:** Floating labels, subtle inner shadows for inputs, and instant inline validation feedback (shimmer effects on success).
*   **Tables:** Sticky headers, alternating row hover states, and smooth horizontal scrolling.
*   **Modals & Drawers:** Slide-in animations using Framer Motion (or native CSS `@starting-style`). Overlays have a heavy blur effect to focus attention.
*   **Notifications:** Toast notifications slide in from the bottom right with a subtle spring physics animation.

## 4. Theming & Accessibility

*   **Dark Mode / Light Mode:** First-class support via CSS variables (`[data-theme='dark']`). The platform defaults to Dark Mode to accentuate the premium 3D/Neon aesthetic, but Light mode is fully supported.
*   **Accessibility (a11y):**
    *   All interactive elements have distinct `:focus-visible` rings (e.g., a 2px offset solid primary ring).
    *   Color contrasts meet WCAG 2.1 AA standards.
    *   ARIA attributes are implemented for the Kanban drag-and-drop and Modals.

## 5. Micro-Animations
*   Buttons have a ripple or subtle glow effect on click.
*   Kanban cards tilt slightly when picked up (dragged).
*   Checking off a task triggers a satisfying, localized particle or checkmark animation.
