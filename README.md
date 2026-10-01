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
- research-led term counting
- equal-segment term trajectories with explicit normalization
- KWIC concordance with token positions
- PMI-ranked collocation with raw co-occurrence counts retained
- version-controlled research questions and term sets
- automated tests
- GitHub Actions validation
- command-line execution
- architecture designed for later TEI/XML, entity, network, and browser-interface work

## Research-led term sets

The first analytical categories derive from questions already present in my Stevenson scholarship:

- **Embodiment** — especially the hand, face, body, skin/hide, eyes, and voice
- **Gender and social relation** — patterns of male/female and relational language
- **Concealment and disclosure** — Hyde/hide, secrecy, strangeness, peculiarity, discovery, masking
- **Writing and confession** — letters, documents, signatures, writing, confession

These categories are stored in `data/research_terms.json` so they can be inspected, revised, and cited as part of the research process.

## Repository structure

```text
stevenson-text-analysis/
├── .github/workflows/
│   └── validate.yml
├── analysis/
│   └── compare_texts.py          # original exploratory analysis
├── data/
│   ├── research_terms.json
│   └── source_manifest.csv
├── docs/
│   └── RESEARCH_METHODS.md
├── src/
│   └── stevenson_text/
│       ├── __init__.py
│       ├── analysis.py
│       ├── cli.py
│       └── corpus.py
├── tests/
│   └── test_analysis.py
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Quick start

```bash
python -m pip install -e ".[dev]"
python -m stevenson_text.cli
pytest
```

The command-line pipeline writes reproducible CSV outputs for lexical summaries, research-term counts, sequential term trajectories, concordances, and collocates.

The original `analysis/compare_texts.py` remains in the repository both for continuity and as a record of the project's earlier, lighter-weight stage.

## Why go beyond Voyant?

Voyant is useful for exploratory reading, especially for quickly visualizing term and character distributions. The aim here is not simply to reproduce it. The project exposes and extends the choices that matter for research:

- segmentation is explicit and configurable;
- normalization is inspectable;
- research terms are version-controlled;
- concordance contexts can be exported;
- collocation measures retain their raw evidence;
- analysis functions can be tested independently;
- future structural encoding can distinguish chapters, speakers, letters, characters, and editorial layers.

See [Research Methods](docs/RESEARCH_METHODS.md) for the fuller methodological rationale.

## Planned extensions

The next development stages include chapter-aware analysis, character alias resolution, dispersion and keyness statistics, n-grams, document-exchange and character networks, TEI/XML import, and a semantic HTML/CSS/JavaScript research interface with auditable underlying tables.

## Source and rights note

The corpus texts are obtained from Project Gutenberg and are identified there as public domain in the United States. Users outside the United States should check the copyright law applicable to their jurisdiction.

---

**Laura Elizabeth Hand**  
[Portfolio](https://www.lauraelizabethhand.com/) · [LinkedIn](https://www.linkedin.com/in/lauraelizabethhand)
