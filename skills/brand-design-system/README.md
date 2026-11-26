# brand-design-system

English · [繁體中文](README.zh-TW.md)

Create a brand identity from three distinct concepts, refine the chosen logo, and build a portable design system around the approved asset.

## Install

```bash
npx skills add SammyLin/skills -s brand-design-system --global
```

## Recommended tools for logo creation

Prefer ChatGPT image generation or Codex with image-generation access for logo concepts. ChatGPT is suitable for visual exploration and refinement; Codex is suitable for repository-based asset management and design-system implementation. If the current agent cannot generate images, use ChatGPT with the prepared prompts and bring the approved image back into the workflow.

## Usage

Ask your agent: "Use brand-design-system to design my app's logo and design system. Show three distinct concepts first."

The skill preserves approved logo bytes, separates brand and semantic UI colors, defines typography and components, and delivers offline HTML, original assets, JSON tokens, documentation and a ZIP. Image generation is capability-dependent; unproduced assets are marked pending.

Use this skill for brand identity and foundations; use mobile-app-design for comprehensive native screen and flow design, and mobile-layout-stability for implementation-level layout checks.

See [SKILL.md](SKILL.md), [delivery conventions](references/delivery.md), and the [worked example](references/parkbird-example.md).
