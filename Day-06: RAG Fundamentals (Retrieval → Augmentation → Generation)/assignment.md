# Day 6 — Assignment

## Instructions

Complete these tasks to build your first RAG systems. You'll implement the complete RAG pipeline: Retrieval → Augmentation → Generation. Make sure you have all dependencies:

```bash
pip install openai chromadb numpy
```

**Important:**
- Test with real documents
- Experiment with different K values
- Try various prompt templates
- Document what works best

---

## Tasks

### Task 1: Basic RAG System

Build a complete RAG system `basic_rag.py`:

**Components:**
1. Document storage (ChromaDB)
2. Retrieval function
3. Augmentation function
4. Generation function
5. Complete query pipeline

**Requirements:**
- Create a `BasicRAG` class
- Methods: `add_documents()`, `query()`
- Retrieve top 3 chunks
- Simple prompt template
- Return answer and sources

**Test with:** the `retrieval` topic in `../RAG assets/documents/` — 9 documents on one subject, or filter `../RAG assets/documents_metadata.json` on `topic == "rag"` for 8 more. Use the whole 61-document set once that works.

**Deliverable:** `task1_basic_rag.py`

---

### Task 2: RAG with Source Citations

Enhance your RAG to include citations `rag_with_citations.py`:

**Features:**
1. Store source metadata with documents
2. Include source info in prompt
3. Generate answers with citations
4. Format: "According to [Source]..."

**Requirements:**
- Track document sources
- Include in augmented prompt
- LLM should cite sources in answer
- Return structured results with citations

**Test with:** `../RAG assets/documents_metadata.json`, which carries a distinct `source` path, `title` and `topic` per document — that is what your citations should render. `../RAG assets/evaluation_questions.json` lists the document each question should be answered from, so you can check whether the model cited the right one rather than a plausible-looking one.

**Deliverable:** `task2_rag_citations.py`

---

### Task 3: Similarity Threshold Filtering

Implement similarity-based filtering `filtered_rag.py`:

**Features:**
1. Set similarity threshold
2. Filter retrieved chunks
3. Only use chunks above threshold
4. Handle case when no chunks pass threshold

**Requirements:**
- Configurable threshold (0.0 to 1.0)
- Show similarity scores
- Test with different thresholds
- Compare results

**Test with:** `../RAG assets/test_queries.txt`. The four questions marked `"kind": "unanswerable"` in `../RAG assets/evaluation_questions.json` have no relevant document in the corpus at all, and `offtopic_sourdough` / `offtopic_tomatoes` are deliberately out of domain. Those are what let you see a threshold working: with a sensible threshold the unanswerable questions should leave you with **zero** chunks, which is requirement 4 above.

**Deliverable:** `task3_filtered_rag.py`

---

### Task 4: Multi-Query RAG

Implement query expansion `multi_query_rag.py`:

**Features:**
1. Generate query variations
2. Search with each variation
3. Combine and deduplicate results
4. Use combined results for answer

**Query expansion ideas:**
- Paraphrase the question
- Extract key terms
- Generate related questions

**Requirements:**
- Create 2-3 query variations
- Search with each
- Merge results (remove duplicates)
- Use merged chunks for answer

**Deliverable:** `task4_multi_query_rag.py`

---

### Task 5: RAG Evaluation System

Build an evaluation framework `rag_evaluator.py`:

**Features:**
1. Test dataset (questions + expected answers)
2. Run RAG on test questions
3. Compare generated vs expected answers
4. Calculate metrics (accuracy, similarity)

**Metrics to implement:**
- Exact match
- Semantic similarity (embedding-based)
- Contains key terms
- Answer length comparison

**Requirements:**
- Create test dataset (5-10 Q&A pairs)
- Run evaluation
- Calculate and display metrics
- Identify failure cases

**Deliverable:** `task5_rag_evaluator.py`

---

## One Mini Project

### 🚀 Build a Full RAG System From Scratch

Create a complete RAG application `rag_system.py` that implements all the concepts learned.

**Features:**

1. **Document Management:**
   - Load documents from files (PDF, TXT)
   - Extract and chunk text
   - Generate embeddings
   - Store in vector database
   - Manage multiple document collections

2. **RAG Pipeline:**
   - Complete retrieval system
   - Configurable K value
   - Similarity threshold filtering
   - Query expansion (optional)
   - Augmentation with citations
   - Generation with LLM

3. **Interactive Interface:**
   ```
   === RAG System ===
   1. Add documents
   2. Ask a question
   3. View indexed documents
   4. Configure settings
   5. Evaluate system
   6. Export results
   7. Exit
   ```

4. **Settings Configuration:**
   - K value (number of chunks)
   - Similarity threshold
   - LLM model selection
   - Temperature
   - Max tokens
   - Enable/disable query expansion

5. **Advanced Features:**
   - Multiple collections
   - Metadata filtering
   - Search history
   - Answer quality scoring
   - Source highlighting
   - Export conversations

6. **Evaluation Tools:**
   - Test with sample questions
   - Compare different configurations
   - Performance metrics
   - Quality assessment

**Requirements:**
- Use classes for organization
- Support multiple file formats
- Implement all RAG components
- Add comprehensive error handling
- Create user-friendly CLI
- Store configurations
- Generate detailed reports

**Example Usage:**
```bash
python rag_system.py

=== RAG System ===
Choose: 1

Enter document path: ../RAG assets/documents
Processing...
✓ Indexed 61 documents
✓ Created 161 chunks

Choose: 2

Question: What is supervised learning?
[Searching...]

Answer:
Supervised learning fits a model to pairs of inputs and known correct outputs...

Sources:
1. [0.89] documents/ml_supervised.txt | topic: ml
2. [0.85] documents/ml_overfitting.txt | topic: ml
3. [0.82] documents/eval_retrieval_metrics.txt | topic: evaluation

[1] Ask another question
[2] View full sources
[3] Main menu
```

**Deliverables:**
- `rag_system.py` - Main application
- `config.json` - Configuration template
- `requirements.txt` - Dependencies
- `README_rag.md` - Usage guide
- Sample test dataset
- Example outputs

---

## Expected Output Section

### Task 1 Expected Output:
```python
from pathlib import Path

docs = sorted(Path("../RAG assets/documents").glob("*.txt"))

rag = BasicRAG()
rag.add_documents([p.read_text() for p in docs])

result = rag.query("Why does indentation matter in Python?")   # q53
# Output:
{
    "answer": "Indentation is syntax in Python: it marks the body of a block...",
    "sources": [
        "Python uses indentation rather than braces to mark the body of a function...",
        "A consistent four-space indent is the community convention..."
    ]
}
```

### Task 2 Expected Output:
```python
result = rag_with_citations.query("What is retrieval-augmented generation?")   # q01
# Output:
{
    "answer": "According to documents/rag_intro.txt, RAG puts a lookup step in front of a language model...",
    "sources": [
        {"text": "...", "id": "doc-038", "source": "documents/rag_intro.txt", "topic": "rag"},
        {"text": "...", "id": "doc-039", "source": "documents/rag_pipeline.txt", "topic": "rag"}
    ]
}

`evaluation_questions.json` lists `doc-038` as the answering document for q01, so
you can assert the citation rather than read it.
```

### Task 3 Expected Output:
```
Query: "What is supervised learning?"
Threshold: 0.7

Retrieved 5 chunks, 3 above threshold (0.7)
Using top 3 chunks for answer...

Answer: [Generated answer using filtered chunks]

Query: "How do I get a mortgage pre-approval in Ireland?"   # q61, unanswerable
Threshold: 0.7

Retrieved 5 chunks, 0 above threshold (0.7)
No chunk passed the threshold. Declining to answer.
```

### Mini Project Expected Output:

The RAG system should provide:
- Fast document indexing
- Accurate retrieval
- Clear, cited answers
- Configurable settings
- Professional interface

**Example session:**
```
=== RAG System ===
Choose: 2

Question: Why is attention expensive on long inputs?

[Retrieving relevant chunks...]
[Generating answer...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Answer:
Attention compares every pair of positions, so its cost grows with the square of the sequence length...

Sources (Top 3):
1. [0.91] documents/ml_transformers.txt | topic: ml
2. [0.87] documents/ml_tokenization.txt | topic: ml
3. [0.84] documents/rag_context_window.txt | topic: rag

Similarity scores shown in brackets
```

---

## Submission Checklist

- [ ] Task 1: Basic RAG working
- [ ] Task 2: Citations implemented
- [ ] Task 3: Filtering functional
- [ ] Task 4: Multi-query working
- [ ] Task 5: Evaluation system complete
- [ ] Mini project: Full RAG system
- [ ] All components tested
- [ ] Code is well-documented
- [ ] Error handling implemented

**Remember:** RAG combines retrieval and generation - both parts are important!

**Good luck!** 🚀

