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
- directed correspondence-network edges;
- document-like `<div>` objects such as letters, confessions, wills, and other encoded documents;
- explicit `<relation>` assertions with active/passive participants and document references;
- directed document-circulation networks from relations named `transmits`;
- structural queries by TEI tag, `@ref`, `@type`, and containing division;
- non-document section extraction that excludes nested `<div>` text so an embedded letter/confession/packet is not counted once as chapter prose and again as a document object.

The implementation deliberately distinguishes **encoded entities** from statistically inferred entities. If a name is not marked up in the TEI, it is not silently treated as if an editor had identified it. Section exports likewise distinguish authored/non-document divisions from embedded document objects: nested document text remains available through the document-object table without being duplicated into the containing section's direct text.

## Demonstration file

`data/tei/jekyll_research_sample.xml` is a small demonstration encoding, not a complete transcription or diplomatic edition. It now includes an embedded letter object and stand-off relation assertions so the code can distinguish a document's textual existence from its circulation among characters.

## Next editorial extensions

Future encoding can add `<sp>` / `<speaker>`, `<q>`, `<seg>`, `<rs>`, `<handShift>`, `<add>`, `<del>`, `<choice>`, `<app>`, richer scene boundaries, and more complete document provenance where those distinctions answer genuine research questions.
