# Research annotation layer

The project now includes a version-controlled annotation layer connecting interpretive categories from *Hyde and Hand* to exact textual anchors in *The Strange Case of Dr. Jekyll and Mr. Hyde*.

This is deliberately separate from both the raw corpus and the TEI sample:

- the **corpus** supplies the text;
- **automatic analysis** supplies counts, concordances, dispersion, collocation, and statistical comparisons;
- **TEI/XML** records explicit editorial structure and encoded entities/documents;
- **research annotations** record interpretive classification decisions tied to passages.

Keeping these layers separate makes it possible to inspect which conclusions come from algorithms and which depend on human scholarly judgment.

## Annotation schema

`data/annotations/hand_motif_annotations.csv` currently includes:

- `annotation_id` — stable identifier;
- `section` — expected narrative section;
- `anchor_phrase` — short phrase used to resolve the annotation back to the corpus;
- `category` — controlled high-level interpretive category;
- `subcategory` — more specific analytic function;
- `actors` — characters implicated by the annotation;
- `document_ref` — optional document identifier;
- `claim_role` — core, supporting, counterexample, or context;
- `note` — concise research rationale.

## Controlled categories

The first controlled vocabulary represents distinctions central to the source essay:

- `embodied_transformation`
- `handwriting_identity`
- `document_transfer`
- `touch_relation`
- `readerly_mediation`
- `figuration_idiom`

The categories are intentionally revisable. Their value is not that they are objectively correct, but that they make classification choices explicit enough to test, challenge, and reproduce. They are the researcher's scholarly classifications, not an independent validation set. Agreement statistics become evidence about coding reliability only when a genuinely independent second annotation set is supplied; duplicating or lightly editing the primary coding would not constitute validation.

## Anchor resolution

`src/stevenson_text/annotations.py` validates the schema and resolves each short anchor phrase against the corpus with the same token-aware phrase matcher used elsewhere in the project.

Resolution status distinguishes:

- **resolved** — one exact token-aware match;
- **ambiguous** — multiple matches;
- **unresolved** — no match.

An unresolved or ambiguous anchor is therefore visible as a research-data quality issue instead of silently entering downstream analysis.

## Scholarly use

This layer prepares the project for later tasks such as:

- comparing manually coded categories with automatic collocation clusters;
- testing inter-annotator agreement if a second coder is added;
- exporting annotations into TEI `<seg>`, `<rs>`, or stand-off annotation;
- visualizing motif categories by chapter;
- distinguishing core evidence from counterexamples;
- tracing how an interpretive claim depends on particular passages.
