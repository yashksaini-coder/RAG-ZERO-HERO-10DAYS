# Day 9 — Assignment

## Instructions

Implement advanced RAG techniques to improve your system. These techniques make RAG production-ready. Install required libraries:

```bash
pip install sentence-transformers rank-bm25 openai numpy
```

**Important:**
- Implement each technique separately first
- Compare before/after results
- Measure improvements
- Document your findings

---

## Tasks

### Task 1: Query Rewriting System

Build a query rewriting system `query_rewriter.py`:

**Features:**
1. Generate query variations using LLM
2. Extract key terms
3. Expand with synonyms
4. Create multiple query formulations

**Requirements:**
- Generate 3-5 variations per query
- Test if variations improve retrieval
- Compare retrieval results
- Document improvements

**Test with:** `../RAG assets/test_queries.txt`, which is grouped by question type
exactly for this task. The `vocabulary_mismatch` group is where rewriting should pay
off most: those questions are phrased in words the answering document never uses, so
a rewrite that introduces the document's vocabulary is the difference between finding
it and not.

Measure against `relevance_grades` in `../RAG assets/evaluation_questions.json` —
"test if variations improve retrieval" needs a number, and that is where the labels are.

**Deliverable:** `task1_query_rewriter.py`

---

### Task 2: Reranking Implementation

Add reranking to your RAG system `reranking_rag.py`:

**Features:**
1. Use cross-encoder model for reranking
2. Rerank initial retrieval results
3. Compare before/after rankings
4. Measure improvement

**Requirements:**
- Install sentence-transformers
- Use a reranking model
- Rerank top 10, return top 5
- Show score improvements

**Test with:** `../RAG assets/test_queries.txt`, scored against the
`relevance_grades` in `../RAG assets/evaluation_questions.json` (`2` = answers the
question, `1` = supporting context). Report recall@5 and MRR before and after
reranking; "measure improvement" is not answerable without labels.

The `lexical_trap` questions are the clearest demonstration. For *"What chunk size
should I use?"* a BM25 first stage ranks `audio_chunk_module` first — it is saturated
with the word *chunk* but is about reading audio frames — while the document that
actually answers is `chunk_size_tradeoff`. A working reranker moves it to the top.

**Deliverable:** `task2_reranking_rag.py`

---

### Task 3: Fusion Techniques

Implement fusion `fusion_rag.py`:

**Features:**
1. Reciprocal Rank Fusion (RRF)
2. Weighted fusion
3. Combine multiple retrieval results
4. Deduplication

**Requirements:**
- Implement RRF algorithm
- Test with 2-3 different retrieval strategies
- Compare fused vs single retrieval
- Measure improvement

**Test with:** the same query set and labels. Fusion should help most on the
`multi_source` questions in `../RAG assets/evaluation_questions.json`, which have more
than one document graded `2` — a single retrieval strategy tends to find one of them
and miss the other.

**Deliverable:** `task3_fusion_rag.py`

---

### Task 4: Hybrid Search

Build hybrid search `hybrid_search.py`:

**Features:**
1. Semantic search (embeddings)
2. Keyword search (BM25)
3. Combine both with weights
4. Tune alpha parameter

**Requirements:**
- Implement BM25 keyword search
- Combine with semantic search
- Test different alpha values (0.0 to 1.0)
- Find optimal balance

**Test with:** `../RAG assets/documents/` and `../RAG assets/test_queries.txt`. The
corpus is built so the alpha sweep has something to find:

- `lexical_trap` questions punish alpha near pure-BM25 (`audio_chunk_module` wins on
  keywords alone)
- `vocabulary_mismatch` questions punish alpha near pure-semantic-free retrieval —
  `evidence_selection` describes retrieval without using the words *retrieval*,
  *search*, *chunk* or *RAG*, and `rag_grounding` describes hallucination without
  using that word, so BM25 cannot reach either

Plot your metric against alpha over the whole query set. If the curve is flat, check
that you normalised the two score scales before blending: a BM25 score is unbounded
while cosine sits near 1.

**Deliverable:** `task4_hybrid_search.py`

---

### Task 5: Complete Advanced RAG

Combine all techniques `advanced_rag.py`:

**Pipeline:**
1. Query rewriting
2. Multiple retrievals (with variations)
3. Fusion (combine results)
4. Reranking (improve order)
5. Generation

**Requirements:**
- Integrate all techniques
- Make it configurable
- Compare with basic RAG
- Measure overall improvement

**Deliverable:** `task5_advanced_rag.py`

---

## One Mini Project

### 🚀 Build a Production-Ready Advanced RAG System

Create a complete advanced RAG application `production_advanced_rag.py` with all optimization techniques.

**Features:**

1. **Complete Advanced Pipeline:**
   - Query rewriting
   - Multiple retrieval strategies
   - Fusion
   - Reranking
   - Generation

2. **Configuration System:**
   - Enable/disable each technique
   - Tune parameters
   - A/B testing mode
   - Performance vs quality trade-offs

3. **Multiple Retrieval Strategies:**
   - Semantic search
   - Keyword search
   - Hybrid search
   - Metadata filtering
   - Custom retrievers

4. **Advanced Features:**
   - Query expansion
   - Query decomposition
   - Multi-query fusion
   - Reranking with cross-encoders
   - Answer quality scoring

5. **Evaluation System:**
   - Compare techniques
   - Measure improvements
   - A/B testing
   - Performance metrics
   - Quality metrics

6. **Interactive Interface:**
   ```
   === Advanced RAG System ===
   1. Index documents
   2. Query (Basic RAG)
   3. Query (Advanced RAG)
   4. Compare techniques
   5. Configure settings
   6. Evaluation mode
   7. Statistics
   8. Exit
   ```

7. **Reporting:**
   - Technique comparison
   - Performance reports
   - Quality improvements
   - Recommendations

**Requirements:**
- All advanced techniques implemented
- Configurable and modular
- Comprehensive evaluation
- Production-ready quality
- Detailed documentation

**Example Usage:**
```python
rag = ProductionAdvancedRAG()

# Configure
rag.configure({
    "query_rewriting": True,
    "reranking": True,
    "fusion": True,
    "hybrid_search": True
})

# Query
result = rag.query("What is machine learning?")
print(result["answer"])
print(f"Improvement: {result['improvement_metrics']}")
```

**Deliverables:**
- `production_advanced_rag.py` - Main system
- `config_advanced.json` - Configuration
- `requirements.txt` - Dependencies
- `README_advanced.md` - Documentation
- Evaluation report template

---

## Expected Output Section

### Task 1 Expected Output:
```python
# q17, a vocabulary_mismatch question: the answering document never uses the
# word "hallucination", so the original phrasing is hard to retrieve on.
variations = rewrite_query("Why does the model make things up when it doesn't know?")
# Output:
[
    "Why does a language model produce unsupported answers?",
    "What causes hallucination in RAG systems?",
    "How do I stop the model inventing facts not in the sources?",
    "grounding answers in retrieved passages",
    "model declines when context is insufficient"
]

# Test retrieval improvement against the labels
basic_results = retrieve("Why does the model make things up when it doesn't know?")
advanced_results = retrieve_multiple(variations)
# Expected answering document: rag_grounding (graded 2 for q17)
```

### Task 2 Expected Output:
```
Query: "What chunk size should I use?"   # q06, lexical_trap
Ground truth: chunk_size_tradeoff (grade 2)

Before Reranking (BM25 top 3):
1. audio_chunk_module   (9.12)  ← keyword match, wrong topic
2. deploy_config        (8.32)
3. chunk_size_tradeoff  (4.98)  ← the document that answers

After Reranking (cross-encoder; scores below are illustrative):
1. chunk_size_tradeoff  (0.94)  ← moved to the top
2. chunk_overlap        (0.71)
3. audio_chunk_module   (0.08)  ← demoted

Improvement: recall@1 0.00 -> 1.00, MRR 0.33 -> 1.00
```

### Task 3 Expected Output:
```
Query: "How should I split documents before embedding them?"   # q05, multi_source
Ground truth: chunk_fixed, chunk_sentence, chunk_paragraph (all grade 2)

Single Retrieval (semantic): 2 of 3 graded documents in top 5
Fusion (semantic + BM25 + rewritten query, RRF): 3 of 3 in top 5
Improvement: recall@5 0.67 -> 1.00
```

### Task 5 Expected Output:
```
=== Advanced RAG Query ===
Question: "Why is a two-stage retrieval pipeline cheaper than scoring the whole index?"   # q16

[Query Rewriting] Generated 4 variations
[Multiple Retrieval] Found 12 candidates
[Fusion] Combined to 8 unique results
[Reranking] Reordered top 5
[Generation] Generated answer

Answer: Narrow to a small candidate set with a cheap method first, then spend the
expensive method only on the survivors...

Improvement Metrics:
- Retrieval: +45% relevant docs
- Answer quality: +23% improvement
- Response time: +0.3s (acceptable)
```

### Mini Project Expected Output:

The advanced RAG system should demonstrate:
- Significant quality improvements
- Configurable techniques
- Comprehensive evaluation
- Production-ready features

**Example session:**
```
=== Advanced RAG System ===
Choose: 3

Question: "Explain neural networks"

[Advanced Pipeline Running...]
✓ Query rewritten: 4 variations
✓ Retrieved: 15 candidates
✓ Fused: 8 unique results
✓ Reranked: Top 5 selected
✓ Generated answer

Answer:
Narrow to a small candidate set with a cheap method first, then spend the
expensive, more accurate method only on the survivors...

Sources (Top 5, reranked):
1. [0.94] documents/evidence_selection.txt | topic: retrieval
2. [0.91] documents/ret_rerank.txt | topic: retrieval
3. [0.89] documents/ret_topk.txt | topic: retrieval
...

Comparison with Basic RAG:
- Answer quality: +28% improvement
- Source relevance: +35% improvement
- Response time: +0.4s
```

---

## Submission Checklist

- [ ] Task 1: Query rewriting working
- [ ] Task 2: Reranking implemented
- [ ] Task 3: Fusion functional
- [ ] Task 4: Hybrid search working
- [ ] Task 5: Complete advanced pipeline
- [ ] Mini project: Production system
- [ ] All techniques tested
- [ ] Improvements measured
- [ ] Code well-documented

**Remember:** Advanced techniques make the difference between a prototype and production system!

**Good luck!** 🚀

