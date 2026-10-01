# TEI/XML layer

The repository now includes a small TEI P5-compatible research layer. It is intentionally partial: the goal is to demonstrate how structured scholarly encoding can sit between source text and computation without presenting the sample as a complete critical edition.

## Why TEI here?

Plain text is useful for lexical analysis, but many of the questions driving this project are structural. A TEI layer can make distinctions that token streams cannot preserve reliably:

- authored divisions such as chapters;
- named people, places, and organizations;
- embedded documents and editorial notes;
- correspondence metadata;
- identifiers that allow entities to remain stable across variant surface forms;
- later distinctions among narration, quotation, speech, handwriting, documents, and editorial intervention.

## Current support

`src/stevenson_text/tei.py` uses Python's standard XML parser and understands the TEI namespace. It currently supports:

- document title extraction;
- `<div>` sections with `xml:id`, `type`, and `<head>`;
- explicit `<persName>`, `<placeName>`, and `<orgName>` entities;
- entity-frequency tables based on encoded identifiers;
- `<correspDesc>` metadata with sent/received actions;
- directed correspondence-network edges.

The implementation deliberately distinguishes **encoded entities** from statistically inferred entities. If a name is not marked up in the TEI, it is not silently treated as if an editor had identified it.

## Demonstration file

`data/tei/jekyll_research_sample.xml` is a small demonstration encoding, not a complete transcription or diplomatic edition. It exists to exercise the architecture and document editorial decisions before a larger encoding effort.

## Next editorial extensions

Future encoding can add `<sp>` / `<speaker>`, `<q>`, `<seg>`, `<rs>`, `<handShift>`, `<add>`, `<del>`, `<choice>`, `<app>`, and more complete correspondence/document metadata where those distinctions answer genuine research questions.
