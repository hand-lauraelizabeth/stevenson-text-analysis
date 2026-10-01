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

The graph does not infer scholarly relationships automatically. Every edge comes from a version-controlled declaration in the evidence-link file.
