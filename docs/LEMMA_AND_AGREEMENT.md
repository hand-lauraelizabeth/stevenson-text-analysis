# Lemma-aware retrieval and annotation reliability

## Controlled lemma groups

The project now supports lemma-aware retrieval through an **explicit research lexicon** in `data/lemma_groups.json`.

This is intentionally not presented as a universal English lemmatizer. Literary texts contain irregular morphology, historically specific usage, nominalizations, puns, and forms whose grouping is itself interpretive. The project therefore records which surface forms are collapsed into a research lemma.

Examples include:

- `write` → write, writes, writing, written, wrote
- `strange` → strange, stranger, strangest, strangely, strangeness
- `sign` → sign, signs, signed, signing, signature, signatures

The code validates that a surface form is not silently assigned to multiple lemma groups. Counts and concordances preserve the original surface form so the normalization can always be reversed during close reading.

## Why not use an opaque lemmatizer?

A general NLP library would be convenient, but it would also import linguistic decisions that are difficult to inspect and may be poorly suited to a small nineteenth-century literary corpus. The controlled lexicon keeps the relevant assumptions in version control and makes them editable as the research question changes.

The architecture can later support an external lemmatizer as a comparison layer without making it the sole representation.

## Inter-annotator comparison

The annotation layer now includes tools for comparing two independently coded annotation files using stable annotation IDs.

The comparison reports:

- labels assigned by coder A and coder B;
- exact agreement for each shared annotation;
- IDs missing from either coding set;
- observed agreement;
- Cohen's kappa for nominal labels.

When both coders assign the same single category to every matched unit, the expected-agreement denominator is zero and Cohen's kappa is mathematically undefined. The code reports that case as `NaN` rather than incorrectly treating it as perfect reliability.

No second-coder score is published in the repository because no independent second coding has yet been performed. The functionality is tested with synthetic examples rather than presenting simulated agreement as research evidence.

A genuine second coding pass can be produced by copying the annotation schema, coding the same stable IDs independently, and running the comparison on fields such as `category` or `claim_role`.

## Interpretation

Agreement statistics do not determine whether an interpretation is correct. They answer a narrower methodological question: whether a coding protocol can be applied consistently enough by more than one annotator to support comparative quantitative claims.
