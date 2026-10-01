# Stevenson Text Analysis

[![Validate analysis](https://github.com/hand-lauraelizabeth/stevenson-text-analysis/actions/workflows/validate.yml/badge.svg)](https://github.com/hand-lauraelizabeth/stevenson-text-analysis/actions/workflows/validate.yml)

A reproducible computational-literary research project centered on Robert Louis Stevenson with an explicitly documented late-Victorian comparison corpus.

This repository grows out of my work in nineteenth-century literature, digital humanities, and textual analysis. Earlier exploratory work used tools such as Voyant to identify patterns of character and concept distribution across long texts. This project makes those analytical choices explicit, reproducible, and extensible rather than leaving them inside a black-box interface.

## Research principle

Quantitative outputs here are not treated as literary interpretations in themselves. They are used to identify distributions, absences, clusters, juxtapositions, and anomalies that can generate or test questions for close reading.

## Corpus

The core corpus uses two public-domain Project Gutenberg texts:

- *The Strange Case of Dr. Jekyll and Mr. Hyde* — target text
- *Treasure Island* — same-author comparator

A separate late-Victorian comparison manifest adds Oscar Wilde's *The Picture of Dorian Gray* (1890), Arthur Conan Doyle's *The Adventures of Sherlock Holmes* (1892), and Bram Stoker's *Dracula* (1897). Source metadata, publication year, corpus role, genre note, and rights note are stored separately from the analysis code.

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
- pooled late-Victorian reference-corpus comparison
- normalized term-rate matrices and leave-one-out sensitivity analysis
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
- version-controlled interpretive annotation layer with controlled categories
- automatic validation and token-aware anchor resolution for manual annotations
- transparent lemma-aware retrieval using version-controlled surface-form groups
- optional inter-annotator agreement comparison with observed agreement and Cohen's kappa
- research-scene extraction between chapter-scale structure and single concordance hits
- scene-level character and motif matrices
- browser evidence cards for resolved research scenes
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
│   ├── lemma_groups.json
│   ├── research_terms.json
│   ├── scenes/
│   │   └── hand_research_scenes.csv
│   ├── victorian_comparison_manifest.csv
│   ├── source_manifest.csv
│   └── structure_rules.json
├── docs/
│   ├── ANNOTATION_METHOD.md
│   ├── HYDE_AND_HAND_CASE_STUDY.md
│   ├── LEMMA_AND_AGREEMENT.md
│   ├── RESEARCH_METHODS.md
│   ├── RESEARCH_SCENES.md
│   ├── VICTORIAN_COMPARISON_CORPUS.md
│   └── TEI_NOTES.md
├── src/
│   └── stevenson_text/
│       ├── __init__.py
│       ├── agreement.py
│       ├── analysis.py
│       ├── annotations.py
│       ├── cli.py
│       ├── comparison.py
│       ├── corpus.py
│       ├── morphology.py
│       ├── networks.py
│       ├── phrases.py
│       ├── scenes.py
│       ├── statistics.py
│       ├── structure.py
│       └── tei.py
├── data/annotations/
│   └── hand_motif_annotations.csv
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

The command-line pipeline writes reproducible CSV outputs for lexical summaries, research-term/phrase/lemma counts, lemma concordances, n-grams and skip-grams, sequential trajectories, dispersion, concordances, collocates, section structure, research-scene windows, scene-level character/term matrices, character-by-section matrices, network nodes/edges, same-author and pooled Victorian comparative keyness, normalized Victorian term-rate matrices, leave-one-out comparator sensitivity, annotation validation/anchor resolution, optional inter-annotator agreement summaries, TEI sections/entities/entity-by-section queries, embedded document objects, correspondence metadata, relation assertions, and directed document-circulation edges.

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

See [Research Methods](docs/RESEARCH_METHODS.md) for the fuller methodological rationale, [Hyde and Hand: computational case study](docs/HYDE_AND_HAND_CASE_STUDY.md) for the argument-centered workflow, and [Research annotation layer](docs/ANNOTATION_METHOD.md) for the manual evidence schema.

## Planned extensions

The next stages include genuine independent second-coder annotation, scene-level network experiments, additional research notebooks, principled expansion of the Victorian comparison corpus, and deeper linking among scenes, annotations, TEI, and the browser research edition.

## Source and rights note

The corpus texts are obtained from Project Gutenberg and are identified there as public domain in the United States. Users outside the United States should check the copyright law applicable to their jurisdiction.

---

**Laura Elizabeth Hand**  
[Portfolio](https://www.lauraelizabethhand.com/) · [LinkedIn](https://www.linkedin.com/in/lauraelizabethhand)
