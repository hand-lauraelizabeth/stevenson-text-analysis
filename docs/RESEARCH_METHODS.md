# Research methods

This repository treats computational analysis as part of literary research rather than as a replacement for close reading.

## Intellectual origin

The project grows out of Laura Elizabeth Hand's research in nineteenth-century literature and digital humanities. An early version was informed by exploratory work with Voyant Tools: plotting names and concepts across sequential segments made patterns of textual presence and absence visible and generated questions for close reading.

The design here makes those analytical choices inspectable. Instead of accepting interface defaults, the project exposes how a text is acquired and cleaned, how tokens are defined, how many sequential segments are used, whether counts are raw or normalized, which research terms were selected in advance, how concordance windows are constructed, and how collocates are ranked.

## Beyond exploratory trends

The project now includes:

- sequential term trajectories with explicit normalization;
- KWIC concordance with context and token position;
- token-aware multi-word phrase search;
- bigram, trigram, and bounded skip-gram analysis;
- collocation analysis using PMI while retaining raw counts;
- version-controlled research questions and term sets;
- source provenance separated from analysis logic;
- authored section structure alongside equal-length segmentation;
- auditable character alias resolution;
- section-based character co-occurrence networks;
- dispersion and comparative keyness statistics;
- reusable modules with automated tests;
- a browser research interface written in semantic HTML, responsive CSS, and dependency-free JavaScript.

## Research questions represented in the code

The first term sets reflect questions developed in Hand's Stevenson scholarship: the role of the hand in intimacy, transformation, writing, confession, and evidence; the relation between hiding/Hyde, disclosure, and strangeness; and the imbalance of male and female textual presence in *The Strange Case of Dr. Jekyll and Mr. Hyde*.

The phrase layer also permits questions to be represented at a level above individual tokens. Phrases such as "written hand," "very great interest," and "poor Hyde" can be counted and contextualized without collapsing them into their component words.

These are research prompts. A lexical or phrasal count does not establish an interpretation. It identifies distributions, absences, juxtapositions, or contexts worth returning to in the text.

## Digital-edition influence

The architecture is informed by digital scholarly editing work involving provenance, structure, annotation, transcription/encoding, and user-facing access. The separation among source metadata, structural rules, entity maps, analytical code, generated tables, and the browser interface is deliberate: it leaves room for TEI/XML without forcing later encoding work into an analysis model designed only for plain text.

## Structure-aware analysis

Equal-length segments are useful for visualizing distributions, but literary texts also have authored structure. For *Jekyll and Hyde*, chapter headings are stored in `data/structure_rules.json` and applied as explicit editorial data rather than inferred silently.

Character references are handled similarly. `data/character_aliases.json` groups forms such as "Dr. Jekyll," "Henry Jekyll," and "Jekyll" under a canonical entity while preventing a long form and its substring from double-counting the same occurrence.

The project distinguishes **frequency** from **distribution**. A term's range records how many sequential segments contain it, while coefficient of variation records how unevenly its occurrences are distributed. Comparative corpus analysis uses log-likelihood (G²) and log ratio so words can be examined for relative over- or under-use between texts.

The comparison design now distinguishes a **same-author comparator** (*Treasure Island*) from a small **late-Victorian external reference corpus**. The external corpus currently includes Wilde's *The Picture of Dorian Gray*, Conan Doyle's *The Adventures of Sherlock Holmes*, and Stoker's *Dracula*. The code preserves author, publication year, corpus role, token totals, and exact reference membership in every aggregate table. It also includes leave-one-out rates so a result that depends strongly on one comparator can be identified rather than hidden inside a pooled statistic.

## Network model

The current character network is intentionally simple and auditable. Two canonical characters are connected when both are mentioned in the same authored section, and edge weight is the number of sections in which the pair co-occurs. This does not imply direct interaction, social intimacy, or narrative causality. It provides a reproducible structural signal that can later be compared with more specific scene-, speech-, or document-based networks.

## Research scenes

The project now includes an intermediate **research-scene** scale between authored chapters and individual concordance hits. A scene is anchored to a short phrase inside a known authored section and expands to a larger token window for analysis. This is not presented as an objective segmentation of the novella. It is a reproducible close-reading unit selected because the surrounding narrative situation matters to the research question.

Scene definitions live in `data/scenes/hand_research_scenes.csv`, and extraction reports resolved, ambiguous, unresolved, or missing-section states. Resolved scenes can then be compared for character presence and declared research-term counts. See `docs/RESEARCH_SCENES.md`.

## Browser interface

The web layer is deliberately dependency-free. Semantic HTML provides structure, CSS handles responsive presentation and keyboard-visible focus states, and JavaScript loads/filter generated CSV tables in the browser. The interface does not replace the underlying outputs: every displayed value remains available as a machine-readable table.

This makes the frontend part of the research method rather than a decorative portfolio shell.

## TEI/XML and scholarly encoding

The third development stage introduces a TEI P5-compatible layer. The project now reads explicit textual divisions, named entities, and correspondence metadata from XML while preserving `xml:id`, division type, and entity references. Encoded entities are kept conceptually separate from inferred aliases: markup represents an editorial assertion, while the plain-text alias layer remains a computational heuristic.

The included `data/tei/jekyll_research_sample.xml` is deliberately labeled as a partial demonstration encoding rather than a complete critical edition. Its purpose is to exercise the architecture and make editorial decisions inspectable before any larger-scale encoding effort.

Correspondence metadata uses `<correspDesc>` and `<correspAction>` to produce directed sender-to-recipient edges. Unlike the section co-occurrence network, these edges arise from explicit encoded document metadata, so the two network models answer different questions and are not conflated.

The TEI layer now also treats letters and similar textual artifacts as first-class document objects. Stand-off `<relation>` elements can encode actions such as transmission or scrutiny and can point to a specific document with `@corresp`. This permits a document-circulation graph in which the actors, relation type, and material text remain separately inspectable rather than collapsing into a generic social-network edge.

Structural queries can retrieve encoded elements by tag, entity reference, or type and can identify the authored divisions that contain a given encoded entity. This moves the project toward the kinds of structured querying used in digital editions while keeping the implementation small enough to audit.

## Visualization and accessibility

The browser layer now includes an SVG character-network visualization generated from the pipeline's node and edge tables. Node placement is deterministic rather than force-directed, keeping the implementation dependency-free and reproducible. Edge thickness represents shared-section weight.

The visualization is paired with an expandable text list of the same relationships, so the network is not the sole carrier of information. The underlying CSVs remain available for inspection and reuse.

The browser now also renders resolved research scenes as evidence cards with section, scene type, anchor phrase, resolution status, surrounding text, and rationale. This creates a visible path from aggregate tables back to close-reading-scale evidence.

## Comparative-corpus limits

The Victorian comparison corpus is not presented as representative of the period. It is a small, research-led context set whose heterogeneity is itself methodologically important. Genre, narrative form, publication date, length, and authorial style may all explain lexical differences. Corpus-level statistics therefore function as contextual tests and falsification opportunities, not as period-wide generalizations.

See `docs/VICTORIAN_COMPARISON_CORPUS.md` for the corpus rationale and expansion criteria.

## Next extensions

- richer named-entity resolution beyond the current inspectable alias maps;
- scene-level and document-exchange network experiments;
- TEI/XML import and structural querying;
- richer browser visualizations with downloadable/auditable source tables;
- research notebooks that reproduce specific literary arguments from question to close reading.
