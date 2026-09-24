# RAG Practice Assets

Synthetic fixtures covering every input type the RAG-ZERO-HERO-10DAYS assignments ask
for. All content is invented and safe to edit.

**These files are generated.** `_build/corpus.py` is the source of truth and
`_build/build.py` writes everything else from it. Editing a generated file directly
will be overwritten on the next build and will desynchronise the CSV, the JSON and
the per-document text views. To change the corpus, edit `corpus.py` and run:

```bash
python3 "RAG assets/_build/build.py"    # rebuild, then verify
python3 "RAG assets/_build/verify.py"   # verify only
```

`verify.py` asserts the requirements the assignments state (document counts, corpus
length, PDF page count, cross-file ID agreement, and that no two documents share a
sentence). Run it before relying on these files.

## Files

| File | What it is | Used from |
| --- | --- | --- |
| `documents/` | 61 topic documents, one per file, 6797 words total | Days 5-9 |
| `documents.csv` | the same corpus as a table | Days 5-8 |
| `documents_metadata.json` | the same corpus with flat scalar metadata for filtering | Days 4-6, 9 |
| `evaluation_questions.json` | 63 questions with **graded relevance labels** | Days 6, 9 |
| `test_queries.txt` | the same questions as plain lines | Days 5-9 |
| `sample_rag_manual.pdf` | 10-page PDF with title/author metadata, running header and numbered footer | Day 4, 7 |
| `long_rag_corpus.md` / `.txt` | one continuous document, 6797+ words, varied paragraph lengths | Day 4 |
| `sample_technical_doc.md` | structured Markdown: nested headings, list, table, code fence | Day 4, 8 |
| `sample_article.html` | article with nav, ad, sidebar, footer, script, table, list, links and meta tags | Day 4 |
| `sample.txt` | short multi-sentence file | Day 1 |
| `messy_text.txt` | whitespace, CRLF, smart quotes, mojibake, control characters, headers/footers, hyphenation, URLs and emails | Day 4 |
| `malformed.html` | unclosed tags and a stray entity | Day 4 |
| `empty.txt` | zero bytes | error handling |

Topics in `documents/`: python foundations (7), machine learning background (5), embeddings (6), chunking (5), vector databases (5), retrieval (9), retrieval-augmented generation (8), evaluation (4), serving (3), deployment (2), security (2), operations (3), unrelated material (2).

## How the corpus is built for retrieval exercises

The documents are not interchangeable filler. Several exist to make a specific
exercise produce a visible result rather than noise:

- **No two documents share a sentence.** An earlier version of these assets ended every
  document with the same line, which pulled all the vectors together and made similarity
  scores meaningless.
- **Lexical traps.** `audio_chunk_module` is saturated with the word *chunk* but is about
  reading audio frames. BM25 ranks it highly for chunking questions; embeddings do not.
  This is what makes Day 9's hybrid-search weight sweep show a difference.
- **Vocabulary mismatches.** `evidence_selection` describes retrieval without using the
  words *retrieval*, *search*, *chunk* or *RAG*, and `rag_grounding` describes
  hallucination without using that word. Semantic search finds them; lexical search
  cannot.
- **Out-of-domain documents.** `offtopic_sourdough` and `offtopic_tomatoes` give a
  similarity threshold something to reject and a metadata filter something to exclude.

## The evaluation set

`evaluation_questions.json` carries per-question relevance grades:

```
"relevance_grades": { "doc-037": 2, "doc-041": 1 }
```

`2` means the document answers the question, `1` means it is useful supporting context,
and anything unlisted is not relevant. Those grades are what make recall@k, precision@k,
MRR and nDCG computable, and they are the only way the Day 9 tasks that say
"measure improvement" can report a number.

Question kinds: lexical_trap (2), multi_source (5), simple (50), unanswerable (4), vocabulary_mismatch (2).

The `unanswerable` questions have no relevant documents by design. A correct system
declines to answer them; Day 6 Task 3 needs exactly this case to test what happens when
nothing passes the similarity threshold.

## Suggested progression

| Day | Use |
| --- | --- |
| 1 | `sample.txt`, then `documents/` as a directory to batch-process |
| 4 | `sample_rag_manual.pdf`, `sample_article.html`, `sample_technical_doc.md` for extraction; `messy_text.txt` for the cleaning pipeline; `long_rag_corpus.md` for comparing chunking strategies; `malformed.html` and `empty.txt` for error handling |
| 5 | Embed `documents/` (61 documents, over the 50 the assignment asks for), search with `test_queries.txt`, filter on the fields in `documents_metadata.json` |
| 6 | `documents/` as the knowledge base, `evaluation_questions.json` to score retrieval and answers, the `unanswerable` questions to test thresholds |
| 7-8 | The same corpus, so a from-scratch implementation and a framework one can be compared on equal footing |
| 9 | `test_queries.txt` with the trap and mismatch questions, scored against `relevance_grades` |
| 10 | Serve the same corpus behind the API and UI |
