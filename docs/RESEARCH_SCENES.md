# Research scenes

The project now includes a **research-scene layer** that sits between chapter-scale structure and individual phrase annotations.

A research scene is not claimed to be an objectively discrete narrative unit. It is a deliberately bounded evidentiary window organized around a passage that matters to a research question.

## Why scenes?

Chapter-level analysis can be too coarse for claims about handwriting, bodily transformation, document transfer, or readerly mediation. Individual concordance hits can be too narrow because they strip away the surrounding narrative situation.

The scene layer resolves a short anchor phrase inside a known authored section and returns a larger token window around that anchor. This permits analysis at a scale closer to close reading while preserving a reproducible link to the source text.

## Scene schema

`data/scenes/hand_research_scenes.csv` records:

- stable `scene_id`;
- authored `section`;
- human-readable title;
- token-aware `anchor_phrase`;
- scene type;
- concise research rationale.

The current scenes focus on passages central to *Hyde and Hand*: failed description, handwriting as evidence, document transfer, bodily transformation, retained handwriting identity, and readerly movement through confession.

## Resolution states

Scene extraction reports:

- **resolved** — exactly one anchor match in the expected section;
- **ambiguous** — multiple matches in that section;
- **unresolved** — no matching anchor;
- **missing_section** — the expected section could not be found.

This makes scene boundaries auditable rather than silently hard-coded.

## Scene-level outputs

Once resolved, scene windows can be analyzed for:

- canonical character presence;
- selected research-term counts;
- scene type;
- token length;
- later manual annotations or TEI export.

The scene layer does not claim that co-presence equals interaction or that the chosen window is the only defensible boundary. Its purpose is to make a close-reading scale reproducible enough to inspect, compare, and revise.
