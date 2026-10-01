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

def _text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return " ".join(" ".join(element.itertext()).split())

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
        body_parts = [
            _text(child)
            for child in div
            if child.tag != f"{{{TEI_NS}}}head"
        ]
        body = " ".join(part for part in body_parts if part)
        sections.append(TEISection(
            xml_id=div.get(f"{{{XML_NS}}}id"),
            section_type=div.get("type"),
            heading=heading or div.get("type") or "Untitled division",
            text=body,
        ))
    return sections

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

def extract_correspondence(root: ET.Element) -> list[TEICorrespondence]:
    """Read TEI correspDesc metadata from the header.

    The function follows the common TEI correspondence pattern of
    correspAction elements with type="sent" and type="received".
    """
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
    """Create directed sender→recipient edges from explicit TEI metadata."""
    edges = Counter()
    for record in records:
        for sender in record.senders:
            for recipient in record.recipients:
                edges[(sender, recipient)] += 1
    return [
        {"source": source, "target": target, "weight": weight}
        for (source, target), weight in sorted(edges.items(), key=lambda item: (-item[1], item[0]))
    ]
