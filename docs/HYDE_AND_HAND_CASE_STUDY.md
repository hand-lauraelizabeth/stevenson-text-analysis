# Hyde and Hand: computational case study

This case study links the repository's technical methods to the literary argument that originally motivated much of the project.

## Research claim

The source essay reads the hand in *The Strange Case of Dr. Jekyll and Mr. Hyde* across three interconnected functions:

1. **social and intimate mediation** — hands participate in relationships among men;
2. **embodied transformation and identity** — the hand becomes a privileged sign of Jekyll/Hyde metamorphosis;
3. **writing, handwriting, confession, and circulation** — hands produce, identify, transfer, and read documents.

The computational project does not attempt to convert those interpretive claims into a score. It asks what reproducible textual evidence can support, complicate, or redirect them.

## Evidence path

The accompanying notebook follows a deliberately staged workflow:

**research question → declared vocabulary → frequency → dispersion → concordance → phrase retrieval → collocation → authored structure → character distribution → comparative corpus → close reading**

This order matters. A word count is not treated as the endpoint. Each quantitative step is a way of deciding what to inspect next.

### Presence and absence

Gendered vocabulary is counted as a starting signal for the novel's strongly male social world. The analysis distinguishes raw terms from canonical named characters and warns against treating token counts as direct measures of representation.

### Motif distribution

`hand`, `strange`, `letter`, and related terms are measured for both frequency and dispersion. Equal-length segments answer a different question from named chapters, so the project retains both.

### Context retrieval

KWIC concordance returns every occurrence of `hand` with surrounding tokens. This allows a researcher to separate bodily hands, handwriting, transfer, idiom, touch, and transformation rather than aggregating unlike uses.

### Phrase-aware evidence

Research phrases such as `odd hand`, `my own hand`, and `written hand` can be searched as token sequences. This matters because many literary claims concern constructions, puns, and syntactic framing rather than isolated vocabulary.

### Collocation

PMI-ranked collocates surface local associations around `hand`, while raw co-occurrence counts remain visible.

### Narrative structure

Character aliases are normalized and counted by authored chapter. This makes it possible to examine entrances, absences, and concentrations without pretending that arbitrary ten-part segmentation is the novel's actual structure.

### Comparison

*Treasure Island* serves as a deliberately limited Stevenson reference text. Log-likelihood and log ratio ask whether a term is relatively distinctive in *Jekyll and Hyde*. The comparison is a check on overclaiming, not a substitute for a larger Victorian corpus.

## Interpretive boundary

The strongest claims in the essay depend on phenomena that computation alone cannot resolve: pronoun choice, dissociation, puns, material writing practices, narrative address, historical discourse around confession and sexuality, and the difference between a hand as body and a hand as handwriting.

The notebook is therefore designed to end where close reading begins again.

## Reproducibility

Open `notebooks/hyde_and_hand_case_study.ipynb` and run it after installing the project:

```bash
python -m pip install -e ".[notebook]"
jupyter lab
```

The notebook uses the same public-domain source manifest and reusable analysis modules as the command-line pipeline.