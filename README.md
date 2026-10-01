# Stevenson Text Analysis

[![Validate analysis](https://github.com/hand-lauraelizabeth/stevenson-text-analysis/actions/workflows/validate.yml/badge.svg)](https://github.com/hand-lauraelizabeth/stevenson-text-analysis/actions/workflows/validate.yml)

A reproducible computational-literary research project using public-domain texts by Robert Louis Stevenson.

This repository grows out of my work in nineteenth-century literature, digital humanities, and textual analysis. Earlier exploratory work used tools such as Voyant to identify patterns of character and concept distribution across long texts. This project makes those analytical choices explicit, reproducible, and extensible rather than leaving them inside a black-box interface.

## Research principle

Quantitative outputs here are not treated as literary interpretations in themselves. They are used to identify distributions, absences, clusters, juxtapositions, and anomalies that can generate or test questions for close reading.

## Corpus

The initial corpus uses two public-domain Project Gutenberg texts:

- *The Strange Case of Dr. Jekyll and Mr. Hyde* — Project Gutenberg eBook #43
- *Treasure Island* — Project Gutenberg eBook #120

Source metadata and rights notes are stored separately from the analysis code.

## Current capabilities

- reproducible acquisition of open textual data
- Gutenberg-wrapper removal and text normalization
- reusable tokenization and corpus utilities
- lexical summaries
- research-led term and multi-word phrase counting
- token-aware phrase concordance
- frequent bigram, trigram, and bounded skip-gram analysis
- equal-segment term trajectories with explicit normalization
- KWIC concordance with token positions
- PMI-ranked collocation with raw co-occurrence counts retained
- version-controlled research questions and term sets
- explicit chapter/section parsing from inspectable structure rules
- character alias resolution with overlap protection
- character-by-section matrices
- section-based character co-occurrence networks
- term dispersion profiles (range and coefficient of variation)
- comparative log-likelihood keyness and log ratio
- semantic HTML, responsive CSS, and dependency-free JavaScript research interface
- automated tests
- GitHub Actions validation
- command-line execution
- TEI/XML parsing for divisions, encoded entities, and correspondence metadata
- directed correspondence networks from explicit TEI metadata
- explicit TEI document objects and document-circulation relations
- structural TEI queries by element, entity reference, and containing section
- accessible SVG network visualization with machine-readable fallback
- reproducible *Hyde and Hand* scholarly case-study notebook
- architecture designed for richer scholarly encoding and entity/network work

## Research-led term sets

The first analytical categories derive from questions already present in my Stevenson scholarship:

- **Embodiment** — especially the hand, face, body, skin/hide, eyes, and voice
- **Gender and social relation** — patterns of male/female and relational language
- **Concealment and disclosure** — Hyde/hide, secrecy, strangeness, peculiarity, discovery, masking
- **Writing and confession** — letters, documents, signatures, writing, confession

Single words and selected phrases are stored in `data/research_terms.json` so the research vocabulary is inspectable and version-controlled rather than buried in code.

## Repository structure

```text
stevenson-text-analysis/
├── .github/workflows/
│   └── validate.yml
├── analysis/
│   └── compare_texts.py
├── data/
│   ├── character_aliases.json
│   ├── research_terms.json
│   ├── source_manifest.csv
│   └── structure_rules.json
├── docs/
│   ├── HYDE_AND_HAND_CASE_STUDY.md
│   ├── RESEARCH_METHODS.md
│   └── TEI_NOTES.md
├── src/
│   └── stevenson_text/
│       ├── __init__.py
│       ├── analysis.py
│       ├── cli.py
│       ├── corpus.py
│       ├── networks.py
│       ├── phrases.py
│       ├── statistics.py
│       ├── structure.py
│       └── tei.py
├── data/tei/
│   └── jekyll_research_sample.xml
├── tests/
│   └── test_analysis.py
├── web/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── notebooks/
│   └── hyde_and_hand_case_study.ipynb
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Quick start

```bash
python -m pip install -e ".[dev]"
python -m stevenson_text.cli
pytest
python -m http.server 8000
```

After running the analysis pipeline, open `http://localhost:8000/web/` to use the browser interface against the generated tables.

For the research notebook:

```bash
python -m pip install -e ".[notebook]"
jupyter lab
```

Then open `notebooks/hyde_and_hand_case_study.ipynb`.

The command-line pipeline writes reproducible CSV outputs for lexical summaries, research-term and phrase counts, n-grams and skip-grams, sequential trajectories, dispersion, concordances, collocates, section structure, character-by-section matrices, network nodes/edges, comparative keyness, TEI sections/entities/entity-by-section queries, embedded document objects, correspondence metadata, relation assertions, and directed document-circulation edges.

The original `analysis/compare_texts.py` remains in the repository both for continuity and as a record of the project's earlier, lighter-weight stage.

## Why go beyond Voyant?

Voyant is useful for exploratory reading, especially for quickly visualizing term and character distributions. The aim here is not simply to reproduce it. The project exposes and extends the choices that matter for research:

- segmentation is explicit and configurable;
- authored structure can be analyzed separately from equal-length segmentation;
- normalization is inspectable;
- terms, phrases, and aliases are version-controlled;
- concordance contexts can be exported;
- collocation measures retain their raw evidence;
- character networks expose their section-based co-occurrence rule;
- statistical comparisons remain available as auditable tables;
- analysis functions can be tested independently;
- the web layer reads generated data rather than embedding opaque results;
- future structural encoding can distinguish chapters, speakers, letters, characters, and editorial layers.

See [Research Methods](docs/RESEARCH_METHODS.md) for the fuller methodological rationale and [Hyde and Hand: computational case study](docs/HYDE_AND_HAND_CASE_STUDY.md) for the argument-centered workflow.

## Planned extensions

The next stages include lemma-aware search, richer scene-level and document-level annotation, expanded TEI querying, additional research notebooks, and a more complete interactive research edition.

## Source and rights note

The corpus texts are obtained from Project Gutenberg and are identified there as public domain in the United States. Users outside the United States should check the copyright law applicable to their jurisdiction.

---

**Laura Elizabeth Hand**  
[Portfolio](https://www.lauraelizabethhand.com/) · [LinkedIn](https://www.linkedin.com/in/lauraelizabethhand)
