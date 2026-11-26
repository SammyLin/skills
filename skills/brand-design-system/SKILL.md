---
name: brand-design-system
description: Create or refine a product brand identity and turn an approved logo into a reusable, implementation-ready design system for apps and websites. Use for logo concepts, wordmarks, mascots, brand guidelines, UI foundations, design tokens, and HTML design-system packages. Do not redesign an approved identity without permission.
---

# Brand Design System

## 1. Establish the brief
Identify product name, purpose, audiences, markets, languages, existing brand assets and target platforms. Reuse information already supplied. Ask only about essential unresolved choices. If a reference is named, inspect the actual reference when accessible; do not pretend to have seen it. Extract principles rather than copying another brand's distinctive mark.

## 2. Explore identity directions
When no logo is approved, propose three genuinely distinct directions (e.g. mascot, abstract symbol, typographic mark). Vary silhouette, composition and visual language, not merely color or accessories. Use an image generation capability for requested rendered logo concepts if available. Separate primary identity from app icons and decorative illustrations. Give each option a stable label A/B/C and preserve the correspondence to its actual image. Show concepts on a clean background at comparable scale.

For international products, prefer a single globally consistent symbol and wordmark unless the user requests localized lockups. Keep local names in product copy or store metadata rather than crowding the logo. Use the exact approved spelling and capitalization.

## 3. Refine and lock the identity
- Resolve feedback against the exact selected image, not a newly imagined interpretation of its label.
- Change only the requested elements; preserve approved composition, mascot proportions, colors and text unless instructed otherwise.
- Separate symbol, wordmark, combination mark, mascot and app icon as distinct asset types.
- Treat AI-rendered lettering as provisional artwork, not an identified typeface or editable vector. Do not label a raster image as SVG/vector artwork.
- After the user approves the identity, preserve its original bytes as the canonical reference. Do not silently regenerate it, recolor it or replace it with a text mockup.
- If a user asks for a design system before identity approval, use the latest supplied asset and explicitly mark the system draft.

## 4. Translate identity into product foundations
Inspect the approved logo. Derive proposed brand colors, checking sampled pixels when possible; distinguish sampled values from chosen production tokens. Define semantic UI roles separately from brand colors (primary, background, surface, text, muted, border, success, warning, error, info). Choose readable foreground/background pairs and verify WCAG AA contrast for text; never rely on color alone for status. Keep branding accents from competing with functional signals.

Define typography for display, headings, body, labels, captions; distinguish custom wordmark from UI fonts. Prefer native platform fonts for mobile when appropriate and language-specific fallbacks for web. Specify responsive layout, spacing scale, radius, elevation, icon size, touch target, motion and reduced-motion support. A 4pt grid and 44pt iOS / 48dp Android targets are useful starting points, not mandatory brand values.

Define usage rules for the logo: clear space, minimum size (validate visually), backgrounds, prohibited transformations, and alternate lockups. If a mascot exists, document immutable anatomy, colors, clothing/marks and permitted expressions or poses. Label variants not yet produced as pending; do not invent assets and call them approved.

## 5. Design actual product components
Use examples relevant to the product, not generic dashboard filler. Include buttons, inputs, search, filters, cards, navigation and status indicators as appropriate. Show default, pressed/hover, focus, disabled, selected, loading, empty, error and stale-data states where relevant. Keep loading skeleton dimensions consistent with loaded components to prevent layout shift. Include a representative app or web screen using real brand assets. Mark example data as illustrative. Support responsive layouts, keyboard access, visible focus, accessible labels, localization, long text, and locale-sensitive numbers/dates; address RTL if target languages need it. Define dark-mode tokens only if produced and checked; otherwise mark pending.

## 6. Deliver a portable package
Default deliverables:
- `index.html`: responsive, self-contained visual brand and UI guide with the actual approved logo embedded as a data URI; CSS and essential JS inline, no network dependency.
- `assets/logo-reference.png` (or original extension): unchanged approved source asset. Include actual standalone variants only when available.
- `design-tokens.json`: machine-readable source of truth for brand and semantic colors, typography, spacing, radius, sizes, motion and other defined foundations.
- `README.md`: scope, version, asset provenance, usage, approved versus proposed decisions, missing assets, and implementation instructions.
- ZIP containing the above; additionally offer the standalone HTML.

For JSON conventions and QA see `references/delivery.md`. For a real example see `references/parkbird-example.md`.

## 7. Verify before delivery
Confirm HTML contains the exact approved image and renders offline. Ensure token names and values match the HTML/CSS. Verify relative asset paths in ZIP, parse JSON, test ZIP integrity, inspect responsive layout and interactions if browser tools exist, check text contrast and readable localization. Do not claim visual or accessibility tests that were not executed. Report any gaps (e.g. no vector source, pending icon, untested dark mode). Provide links only to files created and verified in the current session.

## Working style
Communicate in the user's language. Make concrete proposals, accept iterative feedback, and preserve decisions across turns. Never promise later work. Keep the final deliverables focused on the brand and product, not on the design process itself.
