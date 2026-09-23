# RAG Practice Assets

These synthetic assets are designed to cover the input types in the RAG-ZERO-HERO-10DAYS roadmap.

## Main files

- `sample_rag_manual.pdf` — multi-page PDF extraction and page metadata
- `long_rag_corpus.md` / `.txt` — long corpus for chunking experiments
- `sample_technical_doc.md` — structured Markdown
- `sample_article.html` — web extraction fixture with navigation, footer, script, and ad noise
- `documents/` — 24 small topic documents for embeddings, ChromaDB, semantic search, RAG, and reranking
- `documents.csv` / `documents_metadata.json` — structured corpus variants
- `evaluation_questions.json` — evaluation questions with expected concepts and source IDs
- `test_queries.txt` — reusable search/query set
- `messy_text.txt`, `empty.txt`, `malformed.html` — edge cases for error handling and cleaning

## Suggested progression

Day 4: PDF/HTML/Markdown/TXT extraction → cleaning → chunking → metadata.

Day 5: Embed `documents/`, store vectors, run similarity and semantic search.

Day 6: Use `documents/` as the RAG knowledge base and `evaluation_questions.json` for evaluation.

Day 7–8: Reuse the same corpus so framework comparisons are controlled.

Day 9: Use `test_queries.txt` with query rewriting, BM25, hybrid search, fusion, and reranking.

Day 10: Build the API/UI around the same corpus.

All content is synthetic and safe to modify.
