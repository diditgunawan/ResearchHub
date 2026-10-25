# Prototype v0.1

Static desktop mockups (5 of 18 screens) with sample data. They illustrate layout, states, labels, wording rules, and component inventory for ResearchForge.

## Where things are
| Path | What | Use |
|---|---|---|
| `canvas/*.dc.html`, `canvas/canvas.json` | Source of the Claude Design canvas (5 artboards + index with positions and notes) | Re-publish/edit in Claude Design; requires that runtime |
| `standalone/*.html` (+ `index.html`) | Plain HTML/CSS versions of the same screens | Open in any browser; reference for implementers |
| `design-tokens.json`, `design-tokens.css` | Colors, type, radii, layout extracted from the mockups | Seed the frontend design system |
| `screen-specs.md` | Per-screen purpose, requirement IDs, API calls, components, missing states | Implementation brief |

Live canvas (private to its owner unless shared): https://claude.ai/artifact/VbSG1PPUPubGPV6Tq7P29z — other agents without access should use `standalone/` and `canvas/`.

## Editing the canvas (agents with Design access)
Publish changed files to the existing canvas URL with the Artifact tool (`url` set, no `type_url`); each artboard is a whole `.dc.html` file; `canvas.json` positions boards. Read the canvas first to pick up human edits.

## Conventions
Sample data only (no real papers). Fonts: Inter, Source Serif 4 (Google Fonts). Icons: none yet (text labels); use an inline SVG set when implementing. Colors never carry meaning alone.

## Known limits
Static; no interaction. 1280×800 frames. No mobile layouts. No dark mode. No brand. Text lengths are optimistic (test long titles, Indonesian strings).
