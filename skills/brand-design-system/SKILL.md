---
name: brand-design-system
description: Create or refine a product brand identity and turn an approved logo into a reusable, implementation-ready design system for apps and websites. Use for product discovery, logo concepts, wordmarks, mascots, reusable product illustrations, brand guidelines, UI foundations, design tokens, and HTML design-system packages. Do not redesign an approved identity without permission.
---

# Brand Design System

## 1. Product discovery — mandatory approval gate
Act as a product manager before acting as a designer. Inspect available product docs, existing screens and brand assets when accessible; reuse already confirmed answers. Do not generate logos or illustrations yet. Ask a short, prioritized round of questions about unresolved decisions (typically 3–6, up to 8 when needed). Offer meaningful options, a recommendation with its rationale, and an "other" choice. Ask follow-ups only when an answer changes the design materially.

Cover product purpose and core user journey; primary audience and markets; differentiation and desired brand personality; exact brand name, wordmark language and existing constraints; reference styles and what the user likes/dislikes; target platforms and key product screens; illustration needs and practical deliverables. See `references/discovery-and-illustrations.md` for the interview and asset planning checklist. Inspect actual references if accessible; do not pretend to have seen them. Extract principles rather than copying distinctive marks.

Summarize a short design brief, including confirmed decisions, proposed defaults, open risks and a proposed illustration inventory. **Stop and obtain explicit approval of the brief before generating any images.** Do not interpret silence or partial answers as approval. If a complete brief was explicitly approved already, do not repeat the interview. For a targeted revision to an approved identity, reuse that approval and confirm only changed scope.

## 2. Explore identity directions
When no logo is approved, propose three genuinely distinct directions (e.g. mascot, abstract symbol, typographic mark). Vary silhouette, composition and visual language, not merely color or accessories. Use an image generation capability for requested rendered logo concepts if available. Separate primary identity from app icons and decorative illustrations. Give each option a stable label A/B/C and preserve the correspondence to its actual image. Show concepts on a clean background at comparable scale.

### Recommended logo generation workflow
Prefer **ChatGPT image generation or Codex with access to image generation** for creating and iterating rendered logo concepts. ChatGPT is recommended for visual exploration and conversational refinements; Codex is recommended for a repository-based workflow, asset management and design-system implementation, and may generate logo images when a suitable image-generation capability is available in that environment. Check actual capabilities before attempting generation. If the current agent lacks image generation, prepare three distinct, ready-to-use prompts for ChatGPT, ask the user to supply the selected generated image, and continue from that asset. Do not substitute an improvised programmatic SVG, emoji or text mockup for requested rendered logo concepts unless the user explicitly chooses that medium. Preserve the selected source image when handing off between tools.

For international products, prefer a single globally consistent symbol and wordmark unless the user requests localized lockups. Keep local names in product copy or store metadata rather than crowding the logo. Use the exact approved spelling and capitalization.

## 3. Refine and lock the identity
- Resolve feedback against the exact selected image, not a newly imagined interpretation of its label.
- Change only the requested elements; preserve approved composition, mascot proportions, colors and text unless instructed otherwise.
- Separate symbol, wordmark, combination mark, mascot and app icon as distinct asset types.
- Treat AI-rendered lettering as provisional artwork, not an identified typeface or editable vector. Do not label a raster image as SVG/vector artwork.
- After the user approves the identity, preserve its original bytes as the canonical reference. Do not silently regenerate it, recolor it or replace it with a text mockup.
- If a user asks for a design system before identity approval, use the latest supplied asset and explicitly mark the system draft.

## 4. Create a reusable product illustration library
After identity approval, derive a consistent illustration art direction (palette, outline weight, geometry, character anatomy, perspective, texture, lighting, backgrounds and visual density). Map assets to actual user journeys and UI states rather than generating arbitrary decorations. Present a prioritized asset inventory and one proposed style direction for approval before batch generation; generate a representative sample first and confirm its style before scaling to the remaining assets.

Default to a useful starter set of roughly 6–10 distinct assets, adjusted to the product: hero/landing visual, onboarding or key-feature illustrations, empty/no-results state, error/offline state, success/completion, and optional permission, maintenance or seasonal assets when justified. For mascot brands, include reusable poses/expressions; for non-mascot brands, use a coherent object or scene vocabulary. Avoid illustrations where they interfere with information or accessibility. Do not create unnecessary assets to meet a quota.

Use ChatGPT image generation or Codex with available image generation; reference the approved logo and style sample, preserve character identity, and generate separately usable assets with consistent composition. Avoid embedded text for localization. Prefer true transparent PNG for isolated objects and optimized WebP/PNG for scenes; verify transparency, dimensions and quality, never claim vector or animation unless actually delivered. Export individual files, not only a contact sheet. If only a sheet exists, separate it without clipping or inventing missing content. Include an illustration gallery in the HTML guide with actual produced assets, and an asset manifest with intended usage, filenames, dimensions, format, alt-text guidance and approval status. Mark missing assets as pending and provide actionable prompts if image generation is unavailable.

## 5. Translate identity into product foundations
Inspect the approved logo. Derive proposed brand colors, checking sampled pixels when possible; distinguish sampled values from chosen production tokens. Define semantic UI roles separately from brand colors (primary, background, surface, text, muted, border, success, warning, error, info). Choose readable foreground/background pairs and verify WCAG AA contrast for text; never rely on color alone for status. Keep branding accents from competing with functional signals.

Define typography for display, headings, body, labels, captions; distinguish custom wordmark from UI fonts. Prefer native platform fonts for mobile when appropriate and language-specific fallbacks for web. Specify responsive layout, spacing scale, radius, elevation, icon size, touch target, motion and reduced-motion support. A 4pt grid and 44pt iOS / 48dp Android targets are useful starting points, not mandatory brand values.

Define usage rules for the logo: clear space, minimum size (validate visually), backgrounds, prohibited transformations, and alternate lockups. If a mascot exists, document immutable anatomy, colors, clothing/marks and permitted expressions or poses. Label variants not yet produced as pending; do not invent assets and call them approved.

## 6. Design actual product components
Use examples relevant to the product, not generic dashboard filler. Include buttons, inputs, search, filters, cards, navigation and status indicators as appropriate. Show default, pressed/hover, focus, disabled, selected, loading, empty, error and stale-data states where relevant. Keep loading skeleton dimensions consistent with loaded components to prevent layout shift. Include a representative app or web screen using real brand assets. Mark example data as illustrative. Support responsive layouts, keyboard access, visible focus, accessible labels, localization, long text, and locale-sensitive numbers/dates; address RTL if target languages need it. Define dark-mode tokens only if produced and checked; otherwise mark pending.

## 7. Deliver a portable package
Default deliverables:
- `index.html`: responsive, self-contained visual brand and UI guide with the actual approved logo embedded as a data URI; CSS and essential JS inline, no network dependency.
- `assets/logo-reference.png` (or original extension): unchanged approved source asset. Include actual standalone variants only when available.
- `assets/illustrations/`: individual, reusable product illustrations and approved style reference; include actual produced files.
- `assets/manifest.json`: asset inventory, use cases, dimensions, formats, paths, alt-text guidance and approval status.
- `design-brief.md`: approved product discovery decisions, scope and asset priorities.
- `design-tokens.json`: machine-readable source of truth for brand and semantic colors, typography, spacing, radius, sizes, motion and other defined foundations.
- `README.md`: scope, version, asset provenance, usage, approved versus proposed decisions, missing assets, and implementation instructions.
- ZIP containing the above; additionally offer the standalone HTML.

For JSON conventions and QA see `references/delivery.md`. For a real example see `references/parkbird-example.md`.

## 8. Verify before delivery
Confirm HTML contains the exact approved image and renders offline. Ensure token names and values match the HTML/CSS. Verify every delivered illustration opens, matches its manifest, has the intended transparency/background, follows approved style, and is previewed in the offline HTML. Check that missing assets are not represented as delivered. Verify relative asset paths in ZIP, parse JSON, test ZIP integrity, inspect responsive layout and interactions if browser tools exist, check text contrast and readable localization. Do not claim visual or accessibility tests that were not executed. Report any gaps (e.g. no vector source, pending icon, untested dark mode). Provide links only to files created and verified in the current session.

## Working style
Communicate in the user's language. Make concrete proposals, accept iterative feedback, and preserve decisions across turns. Never promise later work. Keep the final deliverables focused on the brand and product, not on the design process itself.
