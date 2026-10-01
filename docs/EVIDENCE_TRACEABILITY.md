# Evidence links

The repository now has an explicit layer for connecting **research scenes**, **manual annotations**, and **document objects**.

Previously these layers were reproducible but parallel. `data/evidence_links.csv` makes the relationships among them inspectable.

## Schema

Each evidence link has:

- a stable `link_id`;
- optional `scene_id`;
- optional `annotation_id`;
- optional `document_ref`;
- a named `relation`;
- a short note explaining the scholarly connection.

Examples include a scene **supporting** an annotation, a document **materializing** a transfer claim, or a confession **mediating** a readerly scene.

## Validation

The pipeline checks referential integrity against the declared scene and annotation IDs and, when available, known TEI document IDs.

This matters because a research edition can otherwise accumulate dead references as schemas evolve. Broken scene, annotation, or document links are emitted as data-quality issues.

## Evidence bundles

The pipeline generates a flattened evidence-bundle table that brings together:

- scene title, section, and scene type;
- annotation category and claim role;
- document reference;
- relation and explanatory note.

This is intended for the browser interface and for later notebooks.

## Evidence graph

The same declarations are also exported as graph nodes and edges. Node types remain explicit:

- scene
- annotation
- document
- evidence link

An evidence-link row is modeled as its own relation node rather than being converted into an invented pairwise chain such as scene → annotation → document. The graph connects the evidence-link node to its declared endpoints with role edges (`has_scene`, `has_annotation`, `has_document`) and retains the scholarly relation (for example, `supports` or `materializes`) as data on those edges.

This matters because one row can function like a small hyperedge: its declared relation spans a bundle of evidence, and the CSV does not necessarily assert that the scene causes the annotation or that the annotation points directionally to the document. The graph therefore preserves the declaration without adding unsupported semantics.
