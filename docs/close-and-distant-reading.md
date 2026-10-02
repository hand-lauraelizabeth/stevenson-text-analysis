# Close Reading and Distant Reading Are Not Enemies

This short methods note accompanies the public-domain Stevenson text-analysis demonstration in this repository and the academic-writing work on Laura Elizabeth Hand's portfolio.

## The useful loop

A productive computational-humanities workflow can move in both directions:

> **pattern → text → anomaly → better question → revised pattern**

A quantitative model can reveal regularities that are difficult to establish from one text. Close reading can then test what those regularities mean in a particular passage, identify exceptions, and expose assumptions built into the categories used by the model.

The exception is not necessarily noise. An outlier may show where a category stops being useful, where historical context matters, or where a larger corpus has flattened a meaningful distinction.

## What computation can do

For a literary corpus, lightweight computational analysis can help:

- document the scale and composition of the corpus;
- count and compare textual features consistently;
- identify candidate patterns and unusual cases;
- make assumptions and transformations inspectable;
- create reproducible outputs that another reader can check.

Those functions are descriptive and exploratory. A term count, lexical-diversity measure, or ranked feature is not by itself an interpretation of a literary work.

## What close reading can do

Close reading can ask questions the aggregate measure cannot settle:

- Who is speaking, and to whom?
- Does the same word function differently across passages?
- Is an apparent pattern produced by genre, narration, quotation, character, or historical convention?
- What has been lost when a textual feature is converted into a count?
- Does an outlier expose a problem in the model or an important feature of the text?

## Why this repository uses both

The Stevenson analysis intentionally reports modest descriptive measures rather than presenting computation as an automated interpretation engine. Its outputs are prompts for further reading.

For example, a difference in the frequency of embodiment or identity terms can identify passages worth investigating. The literary argument still requires returning to those passages, considering narrative and historical context, and explaining why the observed difference matters.

## Reproducibility is part of interpretation

Computational work also makes methodological decisions unusually visible. Corpus selection, source provenance, cleaning rules, tokenization, missing data, and category definitions all affect what a model can see.

Documenting those decisions is therefore not merely technical housekeeping. It is part of the scholarly argument.

## Development note

This is a 2026 portfolio companion note developed from Laura Elizabeth Hand's earlier interdisciplinary literary scholarship and from the design of this public-domain Stevenson demonstration. It is not presented as a historical course handout or as evidence that computational methods replace the interpretive work of literary study.
