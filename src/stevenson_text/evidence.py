from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from io import StringIO
from typing import Iterable

from .annotations import ResearchAnnotation
from .scenes import ResearchScene

@dataclass(frozen=True)
class EvidenceLink:
    link_id: str
    scene_id: str
    annotation_id: str
    document_ref: str
    relation: str
    note: str

def load_evidence_links_csv(text: str) -> list[EvidenceLink]:
    reader = csv.DictReader(StringIO(text))
    return [
        EvidenceLink(
            link_id=(row.get("link_id") or "").strip(),
            scene_id=(row.get("scene_id") or "").strip(),
            annotation_id=(row.get("annotation_id") or "").strip(),
            document_ref=(row.get("document_ref") or "").strip(),
            relation=(row.get("relation") or "").strip(),
            note=(row.get("note") or "").strip(),
        )
        for row in reader
    ]

def validate_evidence_links(
    links: Iterable[EvidenceLink],
    scenes: Iterable[ResearchScene],
    annotations: Iterable[ResearchAnnotation],
    known_documents: Iterable[str] = (),
) -> list[dict[str, str]]:
    scene_ids = {scene.scene_id for scene in scenes}
    annotation_ids = {annotation.annotation_id for annotation in annotations}
    document_ids = {doc for doc in known_documents if doc}
    issues = []
    seen = set()

    for link in links:
        if not link.link_id:
            issues.append({"link_id": "", "field": "link_id", "issue": "missing id"})
        elif link.link_id in seen:
            issues.append({"link_id": link.link_id, "field": "link_id", "issue": "duplicate id"})
        seen.add(link.link_id)

        if link.scene_id and link.scene_id not in scene_ids:
            issues.append({
                "link_id": link.link_id,
                "field": "scene_id",
                "issue": f"unknown scene {link.scene_id}",
            })
        if link.annotation_id and link.annotation_id not in annotation_ids:
            issues.append({
                "link_id": link.link_id,
                "field": "annotation_id",
                "issue": f"unknown annotation {link.annotation_id}",
            })
        if link.document_ref and document_ids and link.document_ref not in document_ids:
            issues.append({
                "link_id": link.link_id,
                "field": "document_ref",
                "issue": f"unknown document {link.document_ref}",
            })
        if not any([link.scene_id, link.annotation_id, link.document_ref]):
            issues.append({
                "link_id": link.link_id,
                "field": "link",
                "issue": "link has no endpoints",
            })
        if not link.relation:
            issues.append({
                "link_id": link.link_id,
                "field": "relation",
                "issue": "missing relation",
            })
    return issues

def evidence_bundle_rows(
    links: Iterable[EvidenceLink],
    scenes: Iterable[ResearchScene],
    annotations: Iterable[ResearchAnnotation],
) -> list[dict[str, str]]:
    scene_map = {scene.scene_id: scene for scene in scenes}
    annotation_map = {annotation.annotation_id: annotation for annotation in annotations}
    rows = []

    for link in links:
        scene = scene_map.get(link.scene_id)
        annotation = annotation_map.get(link.annotation_id)
        rows.append({
            "link_id": link.link_id,
            "relation": link.relation,
            "scene_id": link.scene_id,
            "scene_title": scene.title if scene else "",
            "scene_section": scene.section if scene else "",
            "scene_type": scene.scene_type if scene else "",
            "annotation_id": link.annotation_id,
            "annotation_category": annotation.category if annotation else "",
            "annotation_claim_role": annotation.claim_role if annotation else "",
            "annotation_note": annotation.note if annotation else "",
            "document_ref": link.document_ref,
            "note": link.note,
        })
    return rows

def evidence_graph(
    links: Iterable[EvidenceLink],
    scenes: Iterable[ResearchScene],
    annotations: Iterable[ResearchAnnotation],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Represent each declared evidence link as an explicit relation node.

    A single evidence-link row can connect a scene, annotation, and document.
    Modeling that row as a node avoids inventing pairwise directionality such
    as scene→annotation→document when the CSV declares only one scholarly
    relation spanning the bundle.
    """
    scene_map = {scene.scene_id: scene for scene in scenes}
    annotation_map = {annotation.annotation_id: annotation for annotation in annotations}
    nodes: dict[str, dict[str, str]] = {}
    edges: list[dict[str, str]] = []

    def add_node(node_id: str, node_type: str, label: str, detail: str = "") -> None:
        if node_id and node_id not in nodes:
            nodes[node_id] = {
                "id": node_id,
                "type": node_type,
                "label": label,
                "detail": detail,
            }

    for link in links:
        link_node = f"evidence_link:{link.link_id}" if link.link_id else ""
        scene_node = f"scene:{link.scene_id}" if link.scene_id else ""
        annotation_node = f"annotation:{link.annotation_id}" if link.annotation_id else ""
        document_node = f"document:{link.document_ref}" if link.document_ref else ""

        if link_node:
            add_node(
                link_node,
                "evidence_link",
                link.relation or link.link_id,
                link.note,
            )
        if link.scene_id:
            scene = scene_map.get(link.scene_id)
            add_node(
                scene_node,
                "scene",
                scene.title if scene else link.scene_id,
                scene.section if scene else "",
            )
        if link.annotation_id:
            annotation = annotation_map.get(link.annotation_id)
            add_node(
                annotation_node,
                "annotation",
                annotation.category if annotation else link.annotation_id,
                annotation.claim_role if annotation else "",
            )
        if link.document_ref:
            add_node(document_node, "document", link.document_ref)

        for target, endpoint_role in (
            (scene_node, "scene"),
            (annotation_node, "annotation"),
            (document_node, "document"),
        ):
            if not link_node or not target:
                continue
            edges.append({
                "source": link_node,
                "target": target,
                "relation": f"has_{endpoint_role}",
                "declared_relation": link.relation,
                "link_id": link.link_id,
            })

    return list(nodes.values()), edges

def evidence_summary(links: Iterable[EvidenceLink]) -> list[dict[str, str | int]]:
    counts = Counter(link.relation for link in links)
    return [
        {"relation": relation, "links": count}
        for relation, count in sorted(counts.items())
    ]
