# Victorian comparison corpus

The repository now includes a small, explicitly documented late-Victorian comparison corpus so claims about *Jekyll and Hyde* are not evaluated only against another Stevenson text.

## Included comparators

The initial comparison set contains public-domain Project Gutenberg editions of:

- Oscar Wilde, *The Picture of Dorian Gray* (1890)
- Arthur Conan Doyle, *The Adventures of Sherlock Holmes* (1892)
- Bram Stoker, *Dracula* (1897)

These texts were selected because they provide nearby but non-identical points of comparison around late-Victorian London, Gothic or uncanny embodiment, male social relations, detection/evidence, writing, and document-mediated narration. They are **not** treated as a representative sample of Victorian literature.

Metadata is stored in `data/victorian_comparison_manifest.csv`, including author, publication year, corpus role, genre note, source URL, and rights note.

## Why a pooled reference corpus?

Comparing *Jekyll and Hyde* only with *Treasure Island* can answer whether a pattern is unusual within a tiny Stevenson sample, but it cannot show whether the same pattern is common in roughly contemporary fiction.

The new comparison layer therefore supports:

- normalized research-term rates by text;
- target-vs-pooled-reference log-likelihood/keyness;
- explicit research-term comparisons even when a term is not statistically extreme;
- leave-one-out reference rates to show how conclusions change when the comparator set changes.

## Methodological caution

The comparison corpus is intentionally small and heterogeneous. Differences can reflect genre, narrator, length, publication context, editorial history, or authorial style rather than the specific literary phenomenon under investigation.

The code therefore preserves titles, authors, years, corpus roles, token totals, and reference membership in every comparison table. A pooled statistic is never presented without the identities of the texts that produced it.

## Expansion path

A later corpus can add more texts by Stevenson and his contemporaries, but expansion should be research-led rather than simply maximizing corpus size. Candidate additions should be documented with a reason for inclusion and should preserve edition/source provenance.
