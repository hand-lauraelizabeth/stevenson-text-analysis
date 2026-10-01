# Stevenson Text Analysis

[![Validate analysis](https://github.com/hand-lauraelizabeth/stevenson-text-analysis/actions/workflows/validate.yml/badge.svg)](https://github.com/hand-lauraelizabeth/stevenson-text-analysis/actions/workflows/validate.yml)

A reproducible digital-humanities demonstration using public-domain texts by Robert Louis Stevenson.

This project pairs close-reading interests with lightweight computational methods. It is designed as an exploratory supplement to literary analysis—not as a substitute for interpretation.

## Corpus

The initial corpus uses two public-domain Project Gutenberg texts:

- *The Strange Case of Dr. Jekyll and Mr. Hyde* — Project Gutenberg eBook #43
- *Treasure Island* — Project Gutenberg eBook #120

The repository stores source metadata and retrieves the public-domain plain text from Project Gutenberg when the analysis runs.

## What this demonstrates

- Reproducible acquisition of open textual data
- Source documentation and corpus provenance
- Text cleaning and tokenization
- Descriptive corpus comparison
- Lexical diversity measures
- Exploratory keyword analysis
- Responsible separation of quantitative signals from literary interpretation
- Automated reproducibility checks through GitHub Actions

## Repository structure

```
stevenson-text-analysis/
├── .github/workflows/
│   └── validate.yml
├── analysis/
│   └── compare_texts.py
├── data/
│   └── source_manifest.csv
├── README.md
└── requirements.txt
```

## Method

The analysis retrieves each source, removes Project Gutenberg wrapper material where present, tokenizes alphabetic words, and reports descriptive measures including word count, unique-token count, type-token ratio, and average token length.

It also reports counts for a small set of predeclared embodiment and identity terms. Those counts are descriptive prompts for further reading, not claims about the meaning of a text.

Because the source texts are retrieved live, the GitHub Actions workflow provides a reproducibility check that the documented sources remain reachable and the analysis still executes.

## Research context

My graduate work in English and Comparative Literature included research on Robert Louis Stevenson, gender, and queerness. This repository demonstrates how computational text analysis can sit alongside—not replace—historical research and close reading.

## Source and rights note

The texts are obtained from Project Gutenberg and are identified there as public domain in the United States. Users outside the United States should check the copyright law applicable to their jurisdiction.

---

**Laura Elizabeth Hand**  
[Portfolio](https://www.lauraelizabethhand.com/) · [LinkedIn](https://www.linkedin.com/in/lauraelizabethhand)
