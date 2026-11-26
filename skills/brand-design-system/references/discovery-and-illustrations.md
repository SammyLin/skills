# Product discovery and illustration planning

## Interview like a product manager
Read existing product context first. Ask unresolved questions in a compact round, with choices and recommendations where helpful. The following are topics, not a script that must be repeated verbatim:
1. What problem does the product solve, and what is its primary user action?
2. Who is the primary audience? Which markets, languages and accessibility needs matter?
3. What differentiates the product? Which 2–3 brand attributes should it communicate, and what should it avoid?
4. What exact name and spelling must appear? Global or localized wordmark? Which existing assets are locked?
5. Which visual references are relevant and why (shape, typography, mood, palette)? Any prohibited colors, symbols or styles?
6. Which platforms, screens and states need illustration? What assets already exist and what technical constraints apply?

Record confirmed answers, proposed defaults, target user journey, exclusions, open risks and acceptance criteria in a short brief. Ask for explicit approval before generating any image. If the user changes direction, update affected decisions; do not reopen settled choices without cause.

## Plan the asset library
Once the logo is approved, map real product needs to artwork. Suggested starting inventory:

| Asset ID | Intended use | Typical composition |
| --- | --- | --- |
| hero | Landing or welcome | Landscape scene, room for live UI copy |
| onboarding-discover | Explain core value | Single clear action, square or portrait |
| onboarding-feature | Explain secondary value | Different meaningful scene |
| empty-favorites | Empty saved items | Compact isolated motif |
| empty-search | No results | Compact isolated motif |
| offline | Connectivity failure | Calm, non-alarming visual |
| success | Completion or confirmation | Positive, compact illustration |
| mascot-wave | Welcome or guidance, if mascot exists | Transparent isolated character |
| mascot-thinking | Help or discovery, if mascot exists | Transparent isolated character |

Adapt to actual product flows. For example ParkBird could use a bird exploring a map, a bird at a theme park, an empty favorites illustration and a weather/offline illustration, all preserving the approved bird anatomy. For a non-mascot product replace character poses with consistent objects or scenes. Do not generate irrelevant imagery.

## Style lock and production
Present the inventory and art direction for approval. Generate a representative sample referencing the approved brand asset. Confirm sample style before batch generation. Maintain consistent character proportions, palette, stroke, shading and perspective. Use text-free art, keep safe margins, and specify where UI copy will sit. Produce independent files in the intended aspect ratio, choose resolution based on actual display sizes (include 2x when useful), and verify alpha for isolated artwork. Do not claim an image has transparent background merely because it appears white.

Prefer ChatGPT image generation or Codex with suitable image generation access. If unavailable, hand off ready-to-use prompts and reference assets, then ingest user-approved results. Never substitute invented placeholder art as approved output.

## Manifest example
```json
{"assets":[{"id":"empty-search","role":"empty-state","screen":"Search / no results","path":"illustrations/empty-search.png","width":1024,"height":1024,"mimeType":"image/png","background":"transparent","altText":"Illustration of a character searching","status":"approved","reference":"approved-style-sample"}]}
```
Illustrative values only. Record actual dimensions, status and paths relative to assets/. Decorative illustrations should use empty alt text in actual UI where appropriate. Pending assets have null paths. Never claim an approval that did not occur.
