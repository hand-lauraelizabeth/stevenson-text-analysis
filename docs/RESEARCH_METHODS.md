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

## Structure-aware analysis

The second development stage adds a distinction that exploratory interfaces often blur: equal-length segments are useful for visualizing distributions, but literary texts also have authored structure. For *Jekyll and Hyde*, chapter headings are therefore stored in `data/structure_rules.json` and applied as explicit editorial data rather than inferred silently.

Character references are handled similarly. `data/character_aliases.json` groups forms such as "Dr. Jekyll," "Henry Jekyll," and "Jekyll" under a canonical entity while preventing a long form and its substring from double-counting the same occurrence. This makes entity decisions auditable and prepares the project for later named-entity and TEI work.

The project now also distinguishes **frequency** from **distribution**. A term's range records how many sequential segments contain it, while coefficient of variation records how unevenly its occurrences are distributed. Comparative corpus analysis uses log-likelihood (G²) and log ratio so words can be examined for relative over- or under-use between texts. These statistics remain prompts for interpretation rather than proxies for significance in the literary-critical sense.

## Next extensions

- phrase- and lemma-aware search;
- richer named-entity resolution beyond the current inspectable alias maps;
- automatic/TEI-backed structural parsing beyond the current explicit heading rules;
- additional keyness and effect-size methods beyond log-likelihood and log ratio;
- additional dispersion measures beyond range and coefficient of variation;
- n-gram and skip-gram analysis;
- character and document-exchange networks;
- TEI/XML import and structural querying;
- semantic HTML/CSS/JavaScript research interface;
- exportable visualizations with auditable data tables.
