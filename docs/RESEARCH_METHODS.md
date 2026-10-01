# Research methods

This repository treats computational analysis as part of literary research rather than as a replacement for close reading.

## Intellectual origin

The project grows out of Laura Elizabeth Hand's research in nineteenth-century literature and digital humanities. An early version was informed by exploratory work with Voyant Tools: plotting names and concepts across sequential segments made patterns of textual presence and absence visible and generated questions for close reading.

The design here makes those analytical choices inspectable. Instead of accepting interface defaults, the project exposes how a text is acquired and cleaned, how tokens are defined, how many sequential segments are used, whether counts are raw or normalized, which research terms were selected in advance, how concordance windows are constructed, and how collocates are ranked.

## Beyond exploratory trends

The project now includes:

- sequential term trajectories with explicit normalization;
- KWIC concordance with context and token position;
- collocation analysis using PMI while retaining raw counts;
- version-controlled research questions and term sets;
- source provenance separated from analysis logic;
- reusable modules with automated tests;
- a path toward TEI/XML and browser-based exploration.

## Research questions represented in the code

The first term sets reflect questions developed in Hand's Stevenson scholarship: the role of the hand in intimacy, transformation, writing, confession, and evidence; the relation between hiding/Hyde, disclosure, and strangeness; and the imbalance of male and female textual presence in *The Strange Case of Dr. Jekyll and Mr. Hyde*.

These are research prompts. A lexical count does not establish an interpretation. It identifies distributions, absences, juxtapositions, or contexts worth returning to in the text.

## Digital-edition influence

The architecture is also informed by digital scholarly editing work involving provenance, structure, annotation, transcription/encoding, and user-facing access. Future TEI/XML work can encode chapters, speakers, named entities, letters/documents, editorial notes, and other structures relevant to literary argument.

## Next extensions

- phrase- and lemma-aware search;
- named-entity aliasing for characters;
- chapter-aware segmentation;
- keyness and log-likelihood comparisons;
- dispersion measures beyond raw frequency;
- n-gram and skip-gram analysis;
- character and document-exchange networks;
- TEI/XML import and structural querying;
- semantic HTML/CSS/JavaScript research interface;
- exportable visualizations with auditable data tables.
