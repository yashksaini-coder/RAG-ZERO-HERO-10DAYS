# RAG Practice Handbook

A short structured Markdown fixture: nested headings, a list, a table and a fenced code block, for loaders that claim to preserve document structure.

## What Retrieval-Augmented Generation Is

Retrieval-augmented generation puts a lookup step in front of a language model. The question is used to find relevant passages in a collection, those passages are placed into the prompt, and the model is asked to answer from them.

The point is to supply knowledge the model does not hold: material published after training, or private to an organisation, or too specific to have been memorised. The model supplies language ability while the collection supplies facts.

Compared with fine-tuning, the knowledge stays editable. Correcting an error means editing a document and re-indexing it, rather than assembling a dataset and running a training job.

## Overlap Between Chunks

Overlap repeats a tail of each piece at the head of the next one. A fact stated across a boundary then appears complete in at least one piece, instead of being halved and lost by both.

A common starting point is ten to twenty percent of the target size. Larger overlaps increase storage and cause the same sentence to surface several times in a result list, crowding out genuinely different material.

Overlap must be strictly smaller than the piece size. When the two are equal the window never advances and the loop that produces pieces runs forever, which is the most common bug in a hand-written splitter.

## Cosine Similarity

Cosine similarity measures the angle between two vectors and ignores their lengths. It is computed as the dot product divided by the product of the two magnitudes, and for embeddings it ranges in practice from roughly zero to one.

Ignoring magnitude is usually what is wanted, because a longer passage tends to produce a vector with a larger norm without being more relevant. Euclidean distance would let that length difference dominate the comparison.

Absolute scores are not comparable across different embedding models. One model may place unrelated sentences at 0.1 and another at 0.7, so any threshold has to be calibrated against the specific model in use rather than copied from a tutorial.

## Hybrid Search

Hybrid search runs a term-based ranker and a vector ranker over the same collection and merges their outputs. Each compensates for the other's blind spot: exact strings come from the term side, paraphrase from the vector side.

A weighted blend needs the two score scales reconciled, because a BM25 score is unbounded while a cosine value sits near one. Normalising each result list to a common range before applying the weight is the usual fix.

The weight is a tunable parameter. Sweeping it from purely lexical to purely semantic on a labelled question set and plotting the metric shows where the corpus sits; identifier-heavy material favours the lexical end, conversational material the semantic end.

## Citations and Traceability

A citation-bearing system keeps the identifier, source path, and position of every passage alongside its text, so that a sentence in the answer can be traced back to the exact place it came from.

Labelling each passage in the prompt and instructing the model to cite those labels is the mechanism. The labels must be short and distinctive, since a model asked to reproduce a long path will sometimes alter it.

Citations should be verified rather than trusted. Checking that each label the model emitted actually appears in the supplied set catches invented references before a user sees them.

## Measuring Retrieval Quality

Recall at k asks whether a known correct source appears anywhere in the first k results. It is the ceiling on the whole system, because a passage that never reaches the generator cannot contribute to the answer.

Precision at k asks what fraction of those k results are relevant, which matters because irrelevant passages consume budget and distract the model. Mean reciprocal rank rewards placing the correct source early rather than merely including it.

Reporting recall and a rank-sensitive measure together is the informative pair. Recall alone hides a system that finds the right passage but buries it in tenth place.

## Checklist

- Extract text and keep the source path with it
- Clean whitespace, headers, footers and encoding damage
- Split with a strategy chosen for the material
- Store vectors and flat scalar metadata together
- Measure recall against a labelled question set

## Default settings

| Setting | Default | Notes |
| --- | --- | --- |
| chunk_size | 500 characters | sweep 300-800 on your own corpus |
| chunk_overlap | 75 characters | must be smaller than chunk_size |
| top_k | 5 | over-fetch to 20 first when reranking |
| score_threshold | 0.35 | calibrate per embedding model |

## Minimal loop

```python
chunks = chunk_with_overlap(text, chunk_size=500, overlap=75)
store.add(chunks, metadata={"source": path})
hits = store.search(question, top_k=5)
answer = generate(question, hits)
```

> Note: every number above is a starting point, not a recommendation.
