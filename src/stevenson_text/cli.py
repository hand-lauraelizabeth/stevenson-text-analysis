from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .analysis import concordance, count_terms, lexical_summary, segment_term_counts, significant_collocates
from .corpus import fetch_document

def main() -> None:
    parser = argparse.ArgumentParser(description="Run reproducible Stevenson corpus analysis.")
    parser.add_argument("--manifest", default="data/source_manifest.csv")
    parser.add_argument("--terms", default="data/research_terms.json")
    parser.add_argument("--segments", type=int, default=10)
    parser.add_argument("--output", default="outputs")
    args = parser.parse_args()

    manifest = pd.read_csv(args.manifest)
    research = json.loads(Path(args.terms).read_text(encoding="utf-8"))
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    all_terms = sorted({
        term.lower()
        for group in research["term_sets"].values()
        for term in group["terms"]
        if " " not in term
    })

    summaries = []
    term_counts = []
    for row in manifest.to_dict("records"):
        doc = fetch_document(row["title"], row["source_url"])
        tokens = doc.tokens
        summaries.append({"title": doc.title, **lexical_summary(tokens)})
        term_counts.append({"title": doc.title, **count_terms(tokens, all_terms)})
        stem = str(row["ebook_id"])
        pd.DataFrame(segment_term_counts(tokens, all_terms, segments=args.segments)).to_csv(
            output / f"{stem}_term_trajectories.csv", index=False
        )
        for anchor in research["anchor_terms"]:
            pd.DataFrame(concordance(doc.text, anchor, window=10, max_hits=100)).to_csv(
                output / f"{stem}_concordance_{anchor}.csv", index=False
            )
            pd.DataFrame(significant_collocates(tokens, anchor, window=5, min_count=2)).to_csv(
                output / f"{stem}_collocates_{anchor}.csv", index=False
            )

    pd.DataFrame(summaries).to_csv(output / "lexical_summary.csv", index=False)
    pd.DataFrame(term_counts).to_csv(output / "research_term_counts.csv", index=False)
    print(pd.DataFrame(summaries).to_string(index=False))
    print(f"\nWrote reproducible research outputs to {output.resolve()}")

if __name__ == "__main__":
    main()
