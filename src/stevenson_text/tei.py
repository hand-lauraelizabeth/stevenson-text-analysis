from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import xml.etree.ElementTree as ET

TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"
NS = {"tei": TEI_NS}

@dataclass(frozen=True)
class TEISection:
    xml_id: str | None
    section_type: str | None
    heading: str
    text: str

@dataclass(frozen=True)
class TEICorrespondence:
    xml_id: str | None
    senders: tuple[str, ...]
    recipients: tuple[str, ...]
    date: str | None

@dataclass(frozen=True)
class TEIDocumentObject:
    xml_id: str | None
    document_type: str
    subtype: str | None
    heading: str
    text: str

@dataclass(frozen=True)
class TEIRelation:
    name: str
    active: tuple[str, ...]
    passive: tuple[str, ...]
    document_ref: str | None

def _text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return " ".join(" ".join(element.itertext()).split())

def _refs(value: str | None) -> tuple[str, ...]:
    return tuple(part for part in (value or "").split() if part)

def parse_tei(xml_text: str) -> ET.Element:
    root = ET.fromstring(xml_text)
    if root.tag != f"{{{TEI_NS}}}TEI":
        raise ValueError("Expected a TEI document in the TEI namespace.")
    return root

def tei_title(root: ET.Element) -> str:
    title = root.find(".//tei:teiHeader//tei:titleStmt/tei:title", NS)
    return _text(title) or "Untitled TEI document"

def extract_tei_sections(root: ET.Element) -> list[TEISection]:
    """Extract authored divisions while preserving TEI ids and division types."""
    sections = []
    for div in root.findall(".//tei:text//tei:div", NS):
        heading = _text(div.find("tei:head", NS))
        body_parts = [_text(child) for child in div if child.tag != f"{{{TEI_NS}}}head"]
        body = " ".join(part for part in body_parts if part)
        sections.append(TEISection(
            xml_id=div.get(f"{{{XML_NS}}}id"),
            section_type=div.get("type"),
            heading=heading or div.get("type") or "Untitled division",
            text=body,
        ))
    return sections

def query_elements(
    root: ET.Element,
    tag: str,
    *,
    ref: str | None = None,
    element_type: str | None = None,
) -> list[dict[str, str]]:
    """Query TEI text elements by local tag plus optional @ref or @type.

    This is intentionally a small, inspectable structural query layer rather
    than a replacement for XPath/XQuery.
    """
    rows = []
    for element in root.findall(f".//tei:text//tei:{tag}", NS):
        if ref is not None and element.get("ref") != ref:
            continue
        if element_type is not None and element.get("type") != element_type:
            continue
        rows.append({
            "tag": tag,
            "xml_id": element.get(f"{{{XML_NS}}}id") or "",
            "type": element.get("type") or "",
            "ref": element.get("ref") or "",
            "text": _text(element),
        })
    return rows

def sections_containing_ref(root: ET.Element, ref: str) -> list[dict[str, str]]:
    """Return outer text divisions containing an explicitly encoded entity ref."""
    rows = []
    for div in root.findall(".//tei:text//tei:div", NS):
        matched = [
            element for element in div.iter()
            if element.get("ref") == ref
        ]
        if not matched:
            continue
        rows.append({
            "xml_id": div.get(f"{{{XML_NS}}}id") or "",
            "type": div.get("type") or "",
            "heading": _text(div.find("tei:head", NS)),
            "ref": ref,
            "mentions": str(len(matched)),
        })
    return rows

def extract_named_entities(root: ET.Element) -> list[dict[str, str]]:
    """Return explicitly encoded TEI names rather than inferred entities."""
    rows = []
    for tag, entity_type in (("persName", "person"), ("placeName", "place"), ("orgName", "organization")):
        for element in root.findall(f".//tei:text//tei:{tag}", NS):
            rows.append({
                "type": entity_type,
                "text": _text(element),
                "ref": element.get("ref") or "",
                "key": element.get("key") or "",
            })
    return rows

def entity_frequencies(root: ET.Element) -> list[dict[str, str | int]]:
    counts = Counter(
        (row["type"], row["ref"] or row["key"] or row["text"].casefold(), row["text"])
        for row in extract_named_entities(root)
    )
    return [
        {"type": entity_type, "identifier": identifier, "label": label, "count": count}
        for (entity_type, identifier, label), count in sorted(
            counts.items(), key=lambda item: (-item[1], item[0])
        )
    ]

def extract_document_objects(
    root: ET.Element,
    document_types: tuple[str, ...] = ("letter", "document", "confession", "will"),
) -> list[TEIDocumentObject]:
    """Extract divisions explicitly encoded as material/narrative documents."""
    objects = []
    for div in root.findall(".//tei:text//tei:div", NS):
        div_type = (div.get("type") or "").casefold()
        subtype = div.get("subtype")
        if div_type not in document_types and (subtype or "").casefold() not in document_types:
            continue
        heading = _text(div.find("tei:head", NS))
        objects.append(TEIDocumentObject(
            xml_id=div.get(f"{{{XML_NS}}}id"),
            document_type=div.get("type") or "document",
            subtype=subtype,
            heading=heading or subtype or div_type or "document",
            text=_text(div),
        ))
    return objects

def extract_relations(root: ET.Element) -> list[TEIRelation]:
    """Read explicit TEI <relation> assertions, including document references."""
    rows = []
    for relation in root.findall(".//tei:relation", NS):
        rows.append(TEIRelation(
            name=relation.get("name") or "relatedTo",
            active=_refs(relation.get("active")),
            passive=_refs(relation.get("passive")),
            document_ref=relation.get("corresp"),
        ))
    return rows

def relation_edges(
    relations: list[TEIRelation],
    *,
    relation_name: str | None = None,
) -> list[dict[str, str | int]]:
    """Aggregate directed actor→actor edges from explicit relation assertions."""
    counts = Counter()
    documents: dict[tuple[str, str, str], set[str]] = {}
    for relation in relations:
        if relation_name is not None and relation.name != relation_name:
            continue
        for source in relation.active:
            for target in relation.passive:
                key = (source, target, relation.name)
                counts[key] += 1
                if relation.document_ref:
                    documents.setdefault(key, set()).add(relation.document_ref)
    return [
        {
            "source": source,
            "target": target,
            "relation": name,
            "weight": weight,
            "documents": "; ".join(sorted(documents.get((source, target, name), set()))),
        }
        for (source, target, name), weight in sorted(
            counts.items(), key=lambda item: (-item[1], item[0])
        )
    ]

def document_circulation_edges(relations: list[TEIRelation]) -> list[dict[str, str | int]]:
    """Return directed transmission edges tied to encoded document identifiers."""
    return relation_edges(relations, relation_name="transmits")

def extract_correspondence(root: ET.Element) -> list[TEICorrespondence]:
    records = []
    for desc in root.findall(".//tei:teiHeader//tei:correspDesc", NS):
        sent = desc.find("tei:correspAction[@type='sent']", NS)
        received = desc.find("tei:correspAction[@type='received']", NS)

        def people(action: ET.Element | None) -> tuple[str, ...]:
            if action is None:
                return ()
            values = []
            for person in action.findall(".//tei:persName", NS):
                values.append(person.get("ref") or person.get("key") or _text(person))
            return tuple(value for value in values if value)

        date_element = None if sent is None else sent.find(".//tei:date", NS)
        date = None
        if date_element is not None:
            date = date_element.get("when") or _text(date_element) or None

        records.append(TEICorrespondence(
            xml_id=desc.get(f"{{{XML_NS}}}id"),
            senders=people(sent),
            recipients=people(received),
            date=date,
        ))
    return records

def correspondence_edges(records: list[TEICorrespondence]) -> list[dict[str, str | int]]:
    edges = Counter()
    for record in records:
        for sender in record.senders:
            for recipient in record.recipients:
                edges[(sender, recipient)] += 1
    return [
        {"source": source, "target": target, "weight": weight}
        for (source, target), weight in sorted(edges.items(), key=lambda item: (-item[1], item[0]))
    ]
