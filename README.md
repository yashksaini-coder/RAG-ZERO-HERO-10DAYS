# 🚀 10-Day RAG Beginner Roadmap

Welcome to your comprehensive learning journey into **Retrieval-Augmented Generation (RAG)**! This repository is designed for absolute beginners who want to master RAG from the ground up in just 10 days.

## 📖 Description

This roadmap takes you from Python fundamentals all the way to building and deploying a complete RAG application. Each day builds upon the previous one, ensuring you have a solid foundation before moving to more advanced concepts. By the end of 10 days, you'll have hands-on experience with:

- Python programming for AI applications
- Large Language Models (LLMs) and their capabilities
- Prompt engineering techniques
- Data extraction and chunking strategies
- Vector embeddings and databases
- Building RAG systems from scratch
- Using frameworks like LangChain and LlamaIndex
- Advanced RAG techniques
- Deploying production-ready RAG applications

## 🎯 How to Use This Repository:

1. **Study Day-by-Day**: Follow the roadmap sequentially, starting with Day 1
2. **Read the Notes**: Open each day's folder and read the `README.md` file thoroughly
3. **Complete Assignments**: Work through the `assignment.md` file for hands-on practice.
   Each task names the file in `RAG assets/` it expects, so you can start coding
   immediately rather than building test data first.
4. **Practice Regularly**: Code along with the examples and complete all practice tasks
5. **Build Projects**: Each day includes a mini-project to reinforce your learning

### Recommended Study Schedule:

- **Time per day**: 2-4 hours
- **Read notes**: 30-60 minutes
- **Complete assignments**: 1-2 hours
- **Mini project**: 30-60 minutes

## 🛠️ Technical Requirements:

### Python Version
- **Python 3.8 or higher** (Python 3.10+ recommended)

### Required Libraries

You'll install these progressively throughout the roadmap:

```bash
# Core libraries
pip install openai
pip install langchain
pip install llama-index
pip install chromadb
pip install sentence-transformers
pip install pypdf
pip install beautifulsoup4
pip install requests
pip install fastapi
pip install streamlit
pip install uvicorn
```

### API Keys

You'll need API keys for certain days:

- **OpenAI API Key** (for Days 2, 3, 6, 7, 8, 9, 10)
  - Sign up at [platform.openai.com](https://platform.openai.com)
  - Get your API key from the API keys section
  - Store it securely (use environment variables)

### Environment Setup

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_api_key_here
```

## 📚 Roadmap Overview

| Day | Topic | Focus Area |
|-----|-------|------------|
| **Day 1** | Python Foundations for GenAI | Python basics, data structures, file handling, APIs |
| **Day 2** | Generative AI & LLM Basics | Understanding LLMs, OpenAI API, model capabilities |
| **Day 3** | Prompt Engineering Essentials | Crafting effective prompts, few-shot learning, chain-of-thought |
| **Day 4** | Chunking & Data Extraction | PDF parsing, web scraping, document processing |
| **Day 5** | Embeddings & Vector Databases | Vector embeddings, similarity search, ChromaDB |
| **Day 6** | RAG Fundamentals | Retrieval → Augmentation → Generation pipeline |
| **Day 7** | Implement RAG From Scratch | Building RAG system with pure Python |
| **Day 8** | RAG Using LangChain or LlamaIndex | Using popular RAG frameworks |
| **Day 9** | Advanced RAG | Reranking, query rewriting, fusion techniques |
| **Day 10** | Build & Deploy RAG Application | FastAPI/Streamlit deployment, production considerations |

## 🗂️ Repository Structure

```
rag-roadmap/
│
├── Day01/
│   ├── README.md
│   └── assignment.md
│
├── Day02/
│   ├── README.md
│   └── assignment.md
│
├── Day03/
│   ├── README.md
│   └── assignment.md
│
├── Day04/
│   ├── README.md
│   └── assignment.md
│
├── Day05/
│   ├── README.md
│   └── assignment.md
│
├── Day06/
│   ├── README.md
│   └── assignment.md
│
├── Day07/
│   ├── README.md
│   └── assignment.md
│
├── Day08/
│   ├── README.md
│   └── assignment.md
│
├── Day09/
│   ├── README.md
│   └── assignment.md
│
├── Day10/
│   ├── README.md
│   └── assignment.md
│
├── RAG assets/              (practice data used by every day)
│   ├── documents/           61 topic documents
│   ├── documents.csv
│   ├── documents_metadata.json
│   ├── evaluation_questions.json   63 questions with relevance labels
│   ├── test_queries.txt
│   ├── sample.txt
│   ├── sample_rag_manual.pdf       10-page PDF
│   ├── sample_article.html
│   ├── sample_technical_doc.md
│   ├── long_rag_corpus.md / .txt
│   ├── messy_text.txt, malformed.html, empty.txt   (edge cases)
│   ├── _build/              generator and verifier
│   └── README.md
│
├── RAG Projects/
│   └── readme.md
│
└── README.md   (this file)
```

## 📦 Practice Data

Every assignment works against the fixtures in `RAG assets/`, so you never have to
invent test data and results are comparable from one day to the next. Each
assignment names the exact file it expects.

| You need | Use |
| --- | --- |
| A short text file | `RAG assets/sample.txt` |
| A multi-page PDF | `RAG assets/sample_rag_manual.pdf` |
| A web page to scrape | `RAG assets/sample_article.html` |
| A long document to chunk | `RAG assets/long_rag_corpus.md` |
| A document corpus | `RAG assets/documents/` (61 files) |
| Search queries | `RAG assets/test_queries.txt` |
| Scoring retrieval | `RAG assets/evaluation_questions.json` |
| Error-handling cases | `RAG assets/empty.txt`, `malformed.html`, `messy_text.txt` |

`evaluation_questions.json` records which documents answer each question, so from
Day 6 onwards you can measure retrieval instead of eyeballing it. The corpus also
contains deliberate traps — a document stuffed with the word *chunk* that is
actually about audio, and documents that answer a question without using its
words — so the Day 9 comparisons of BM25 against semantic search show a real
difference.

The assets are generated. `RAG assets/_build/corpus.py` is the source and
`build.py` writes the rest from it; `verify.py` checks them against what the
assignments require:

```bash
python3 "RAG assets/_build/verify.py"    # 72 checks
python3 "RAG assets/_build/build.py"     # regenerate, then verify
```

See `RAG assets/README.md` for the full description.

## 💡 Learning Tips

1. **Don't Skip Days**: Each day builds on previous concepts
2. **Code Along**: Type out the examples yourself, don't just read
3. **Experiment**: Modify examples to see what happens
4. **Ask Questions**: If something is unclear, research it
5. **Take Notes**: Write down key concepts in your own words
6. **Build Projects**: The mini-projects are crucial for understanding

## 🎓 Prerequisites

- Basic understanding of programming concepts (variables, functions, loops)
- Familiarity with command line/terminal
- Willingness to learn and experiment
- No prior AI/ML experience required!

## 📝 Notes

- All code examples are beginner-friendly
- Solutions are not provided for assignments (learning by doing!)
- You can work at your own pace, but try to complete one day per day
- Feel free to revisit previous days if needed

## 🙏 Credits

Created by **Chandra Sekhar**

---

**Ready to start?** Navigate to `Day01/` and begin your RAG journey! 🚀

