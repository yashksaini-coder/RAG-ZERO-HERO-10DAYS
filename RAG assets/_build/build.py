#!/usr/bin/env python3
"""Regenerate every file under `RAG assets/` from `corpus.py`.

    python3 "RAG assets/_build/build.py"

Deterministic: running it twice produces byte-identical output. It rewrites the
generated files, removes documents that are no longer in the corpus, and then
runs verify.py so a broken asset set cannot be committed silently.
"""

import csv
import json
import os
import shutil
import textwrap
import zlib

import corpus

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCDIR = os.path.join(ROOT, "documents")


def w(relpath, text):
    """Write text with LF endings and a single trailing newline."""
    path = os.path.join(ROOT, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text.rstrip("\n") + "\n")
    return path


def doc_id(index):
    return "doc-%03d" % (index + 1)


# ---------------------------------------------------------------------------
# Minimal PDF writer
#
# No PDF library is available in this environment, so this emits PDF 1.4 by
# hand: base-14 Helvetica (no font embedding needed), Flate-compressed content
# streams, and a real /Info dictionary so Day 4 Task 1 has author and title
# metadata to extract. Every page carries a running header and a "Page N of M"
# footer, which is what Day 4 Task 4's "remove headers/footers" step detects.
# ---------------------------------------------------------------------------

PAGE_W, PAGE_H = 612, 792
MARGIN = 72
LEAD = 15.5


def esc(s):
    s = s.encode("ascii", "replace").decode("ascii")
    return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def page_stream(page_no, total, blocks, header):
    """blocks: list of (style, text). style in {h1, h2, body, bullet}."""
    out = ["BT", "/F2 9 Tf", "0.45 g", "1 0 0 1 %d %d Tm" % (MARGIN, PAGE_H - 46),
           "(%s) Tj" % esc(header), "ET",
           "0.8 G", "0.5 w", "%d %d m %d %d l S" % (MARGIN, PAGE_H - 54,
                                                    PAGE_W - MARGIN, PAGE_H - 54)]
    y = PAGE_H - MARGIN - 12
    for style, text in blocks:
        # `gap` is the space before the block. It must exceed LEAD, or a
        # paragraph break ends up tighter than the line spacing inside a
        # paragraph and the paragraphs read as one run-on block.
        if style == "h1":
            font, size, wrap, gap = "/F2", 19, 46, 34
        elif style == "h2":
            font, size, wrap, gap = "/F2", 13, 62, 28
        elif style == "bullet":
            font, size, wrap, gap = "/F1", 10.5, 84, 17
        else:
            font, size, wrap, gap = "/F1", 10.5, 88, 21
        lines = textwrap.wrap(text, wrap) or [""]
        if style == "bullet":
            lines = ["- " + lines[0]] + ["  " + ln for ln in lines[1:]]
        y -= gap
        out += ["BT", "%s %s Tf" % (font, size), "0 g",
                "1 0 0 1 %d %.1f Tm" % (MARGIN, y), "%.1f TL" % LEAD]
        for i, ln in enumerate(lines):
            out.append("(%s) Tj" % esc(ln))
            if i != len(lines) - 1:
                out.append("T*")
        out.append("ET")
        y -= LEAD * (len(lines) - 1)
    if y < MARGIN - 6:
        # Text below this point renders off the page. pdftotext would still
        # extract it, so the damage would be invisible to a text-only check.
        raise ValueError(
            "page %d overflows: final baseline y=%.0f is below the footer. "
            "Move a document to another page in build_pdf()'s layout." % (page_no, y))

    foot = "Page %d of %d" % (page_no, total)
    out += ["0.8 G", "0.5 w", "%d %d m %d %d l S" % (MARGIN, MARGIN - 18,
                                                     PAGE_W - MARGIN, MARGIN - 18),
            "BT", "/F1 9 Tf", "0.45 g",
            "1 0 0 1 %d %d Tm" % (PAGE_W / 2 - 24, MARGIN - 32),
            "(%s) Tj" % esc(foot), "ET"]
    return "\n".join(out).encode("ascii")


def write_pdf(path, pages, info):
    """pages: list of (header, [(style, text), ...])."""
    objs = {}
    total = len(pages)
    n_pages = total
    first_page_obj = 5
    page_ids = [first_page_obj + 2 * i for i in range(n_pages)]

    objs[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    kids = " ".join("%d 0 R" % p for p in page_ids)
    objs[2] = ("<< /Type /Pages /Count %d /Kids [%s] >>" % (n_pages, kids)).encode()
    objs[3] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
    objs[4] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"

    for i, (header, blocks) in enumerate(pages):
        pid, cid = page_ids[i], page_ids[i] + 1
        objs[pid] = (
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] "
            "/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents %d 0 R >>"
            % (PAGE_W, PAGE_H, cid)
        ).encode()
        raw = page_stream(i + 1, total, blocks, header)
        comp = zlib.compress(raw, 9)
        objs[cid] = (b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(comp)
                     + comp + b"\nendstream")

    info_id = max(objs) + 1
    objs[info_id] = ("<< " + " ".join(
        "/%s (%s)" % (k, esc(v)) for k, v in info.items()) + " >>").encode()

    buf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = {}
    for num in sorted(objs):
        offsets[num] = len(buf)
        buf += b"%d 0 obj\n" % num + objs[num] + b"\nendobj\n"
    xref = len(buf)
    top = max(objs) + 1
    buf += b"xref\n0 %d\n" % top
    buf += b"0000000000 65535 f \n"
    for num in range(1, top):
        buf += b"%010d 00000 n \n" % offsets[num]
    buf += (b"trailer\n<< /Size %d /Root 1 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n"
            % (top, info_id, xref))
    with open(path, "wb") as fh:
        fh.write(bytes(buf))
    return path


# ---------------------------------------------------------------------------
# Generated assets
# ---------------------------------------------------------------------------

TOPIC_ORDER = [
    ("python", "Python Foundations"),
    ("ml", "Machine Learning Background"),
    ("embeddings", "Embeddings"),
    ("chunking", "Chunking"),
    ("vector_db", "Vector Databases"),
    ("retrieval", "Retrieval"),
    ("rag", "Retrieval-Augmented Generation"),
    ("evaluation", "Evaluation"),
    ("api", "Serving"),
    ("deployment", "Deployment"),
    ("security", "Security"),
    ("operations", "Operations"),
    ("offtopic", "Unrelated Material"),
]

TOPIC_INTRO = {
    "python": "The language-level material a RAG project leans on.",
    "ml": "Background concepts that explain why the retrieval stack behaves as it does.",
    "embeddings": "Turning text into vectors, and comparing those vectors correctly.",
    "chunking": "Splitting documents into units small enough to retrieve and large enough to mean something.",
    "vector_db": "Storing vectors next to the text and metadata they came from.",
    "retrieval": "Finding the passages that bear on a question.",
    "rag": "Assembling retrieval and generation into a system that answers with evidence.",
    "evaluation": "Measuring whether any of it actually works.",
    "api": "Putting the system behind an interface a person or program can call.",
    "deployment": "Shipping it somewhere other than a laptop.",
    "security": "Keeping credentials and untrusted content from becoming incidents.",
    "operations": "Running it once real traffic arrives.",
    "offtopic": "Deliberately unrelated documents. They exist so that similarity thresholds, "
                "metadata filters and out-of-scope questions have something to exclude.",
}


def by_topic():
    out = []
    for key, heading in TOPIC_ORDER:
        docs = [d for d in corpus.DOCS if d["topic"] == key]
        if docs:
            out.append((key, heading, docs))
    return out


def build_documents():
    """One .txt per document, plus removal of anything no longer in the corpus."""
    os.makedirs(DOCDIR, exist_ok=True)
    keep = set()
    for i, d in enumerate(corpus.DOCS):
        name = d["slug"] + ".txt"
        keep.add(name)
        body = "%s\n\n%s\n" % (d["title"], d["body"])
        with open(os.path.join(DOCDIR, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    removed = []
    for name in sorted(os.listdir(DOCDIR)):
        if name.endswith(".txt") and name not in keep:
            os.remove(os.path.join(DOCDIR, name))
            removed.append(name)
    return len(keep), removed


def build_csv():
    path = os.path.join(ROOT, "documents.csv")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh, lineterminator="\n")
        wr.writerow(["id", "slug", "topic", "doc_type", "difficulty", "title",
                     "word_count", "text"])
        for i, d in enumerate(corpus.DOCS):
            flat = " ".join(d["body"].split())
            wr.writerow([doc_id(i), d["slug"], d["topic"], d["doc_type"],
                         d["difficulty"], d["title"], len(flat.split()), flat])


def build_metadata():
    """Flat scalar metadata only: Chroma and most stores reject nested values
    and None, so every field here is a string or an int."""
    rows = []
    for i, d in enumerate(corpus.DOCS):
        flat = " ".join(d["body"].split())
        rows.append({
            "id": doc_id(i),
            "slug": d["slug"],
            "source": "documents/%s.txt" % d["slug"],
            "title": d["title"],
            "topic": d["topic"],
            "doc_type": d["doc_type"],
            "difficulty": d["difficulty"],
            "paragraphs": len(d["body"].split("\n\n")),
            "word_count": len(flat.split()),
            "char_count": len(flat),
            "text": flat,
        })
    w("documents_metadata.json", json.dumps(rows, indent=2, ensure_ascii=False))


def build_eval():
    slug_to_id = {d["slug"]: doc_id(i) for i, d in enumerate(corpus.DOCS)}
    items = []
    for q in corpus.QUERIES:
        rel = sorted(q["relevant"].items(), key=lambda kv: (-kv[1], kv[0]))
        items.append({
            "id": q["id"],
            "question": q["question"],
            "kind": q["kind"],
            "reference_answer": q["reference_answer"],
            "key_facts": q["key_facts"],
            "relevant_ids": [slug_to_id[s] for s, _ in rel],
            "relevant_slugs": [s for s, _ in rel],
            "relevance_grades": {slug_to_id[s]: g for s, g in rel},
            "answerable": q["kind"] != "unanswerable",
        })
    payload = {
        "schema": {
            "relevance_grades": "document id -> 2 (answers the question) or 1 (supporting context); "
                                "unlisted documents are not relevant",
            "kind": "simple | multi_source | vocabulary_mismatch | lexical_trap | unanswerable",
            "answerable": "false means a correct system declines instead of answering",
        },
        "questions": items,
    }
    w("evaluation_questions.json", json.dumps(payload, indent=2, ensure_ascii=False))


def build_queries():
    lines = ["# One query per line, blank lines and # comments ignored.",
             "# Graded relevance for each of these lives in evaluation_questions.json.", ""]
    for label, kind in [("Ordinary lookups", "simple"),
                        ("Needing more than one source", "multi_source"),
                        ("Vocabulary mismatch (lexical search alone will miss these)",
                         "vocabulary_mismatch"),
                        ("Lexical traps (an unrelated document shares the keywords)",
                         "lexical_trap"),
                        ("Unanswerable from this corpus (a correct system declines)",
                         "unanswerable")]:
        qs = [q for q in corpus.QUERIES if q["kind"] == kind]
        lines.append("# --- %s (%d) ---" % (label, len(qs)))
        lines += [q["question"] for q in qs]
        lines.append("")
    w("test_queries.txt", "\n".join(lines))


def build_long_corpus():
    """One continuous document, as proper Markdown.

    The previous version of this file had the section headings concatenated onto
    the end of the preceding paragraph, so Markdown-aware chunking mis-attributed
    every section. Blocks are joined with a blank line here and nothing else, so a
    heading is always the first thing on its own line.
    """
    blocks = [
        "# RAG Practice Corpus",
        "A single long document assembled from the same material as `documents/`, for "
        "chunking experiments that need one continuous text. Paragraph lengths vary "
        "deliberately, so fixed-size, sentence-aware and paragraph-aware chunking give "
        "visibly different results on it.",
    ]
    for key, heading, docs in by_topic():
        blocks.append("## " + heading)
        blocks.append(TOPIC_INTRO[key])
        for d in docs:
            blocks.append("### " + d["title"])
            for para in d["body"].split("\n\n"):
                blocks.append(" ".join(para.split()))
    w("long_rag_corpus.md", "\n\n".join(blocks))

    plain = [b.lstrip("#").strip() if b.startswith("#") else b for b in blocks]
    w("long_rag_corpus.txt", "\n\n".join(plain))


def build_technical_doc():
    blocks = ["# RAG Practice Handbook", "",
              "A short structured Markdown fixture: nested headings, a list, a table and a "
              "fenced code block, for loaders that claim to preserve document structure.", ""]
    picks = ["rag_intro", "chunk_overlap", "emb_cosine", "ret_hybrid",
             "rag_citations", "eval_retrieval_metrics"]
    index = {d["slug"]: d for d in corpus.DOCS}
    for slug in picks:
        d = index[slug]
        blocks.append("## " + d["title"])
        blocks.append("")
        for para in d["body"].split("\n\n"):
            blocks.append(" ".join(para.split()))
            blocks.append("")
    blocks += [
        "## Checklist", "",
        "- Extract text and keep the source path with it",
        "- Clean whitespace, headers, footers and encoding damage",
        "- Split with a strategy chosen for the material",
        "- Store vectors and flat scalar metadata together",
        "- Measure recall against a labelled question set", "",
        "## Default settings", "",
        "| Setting | Default | Notes |",
        "| --- | --- | --- |",
        "| chunk_size | 500 characters | sweep 300-800 on your own corpus |",
        "| chunk_overlap | 75 characters | must be smaller than chunk_size |",
        "| top_k | 5 | over-fetch to 20 first when reranking |",
        "| score_threshold | 0.35 | calibrate per embedding model |", "",
        "## Minimal loop", "",
        "```python",
        "chunks = chunk_with_overlap(text, chunk_size=500, overlap=75)",
        "store.add(chunks, metadata={\"source\": path})",
        "hits = store.search(question, top_k=5)",
        "answer = generate(question, hits)",
        "```", "",
        "> Note: every number above is a starting point, not a recommendation.",
    ]
    w("sample_technical_doc.md", "\n".join(blocks))


def build_article_html():
    index = {d["slug"]: d for d in corpus.DOCS}
    body = index["rag_intro"]["body"].split("\n\n")
    more = index["rag_pipeline"]["body"].split("\n\n")
    html = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Understanding Retrieval-Augmented Generation | Practice Site</title>
<meta name="author" content="Dana Practice">
<meta name="description" content="A plain-language introduction to retrieval-augmented generation.">
<meta property="article:published_time" content="2026-03-14T09:30:00Z">
<meta property="og:title" content="Understanding Retrieval-Augmented Generation">
<link rel="canonical" href="https://example.invalid/articles/understanding-rag">
<style>nav {{ display: flex; }} .ad {{ color: #999; }}</style>
</head>
<body>
<!-- Everything outside <article> is chrome and should not survive extraction. -->
<header>
<nav><a href="/">Home</a> | <a href="/docs">Docs</a> | <a href="/pricing">Pricing</a> | <a href="/login">Log in</a></nav>
</header>
<div class="ad">Sponsored: this advertisement must not appear in the extracted text.</div>
<main>
<article>
<h1>Understanding Retrieval-Augmented Generation</h1>
<p class="byline">By <span class="author">Dana Practice</span> &middot;
<time datetime="2026-03-14">14 March 2026</time> &middot; 6 min read</p>
<p>{p0}</p>
<p>{p1}</p>
<h2>The two pipelines</h2>
<p>{p2}</p>
<ul>
<li>Load and clean the source material</li>
<li>Split it into passages</li>
<li>Encode the passages and store them with their metadata</li>
</ul>
<h2>What a query costs</h2>
<table>
<thead><tr><th>Stage</th><th>Typical latency</th></tr></thead>
<tbody>
<tr><td>Encode the question</td><td>20&ndash;60 ms</td></tr>
<tr><td>Search the store</td><td>5&ndash;40 ms</td></tr>
<tr><td>Generate the answer</td><td>1&ndash;6 s</td></tr>
</tbody>
</table>
<h2>A minimal call</h2>
<pre><code>hits = store.search(question, top_k=5)
answer = generate(question, hits)</code></pre>
<p>Further reading is collected on the <a href="/docs/retrieval">retrieval page</a>
and in the <a href="https://example.invalid/papers">paper index</a>.</p>
</article>
</main>
<aside class="related">
<h3>Related</h3>
<ul><li><a href="/articles/chunking">Chunking strategies</a></li>
<li><a href="/articles/rerank">Reranking</a></li></ul>
</aside>
<footer>Copyright 2026 Practice Site &middot; <a href="/privacy">Privacy</a></footer>
<script>console.log("analytics payload that must be stripped");</script>
<noscript>Enable JavaScript for the interactive demo.</noscript>
</body>
</html>"""
    html = html.format(p0=" ".join(body[0].split()),
                       p1=" ".join(body[1].split()),
                       p2=" ".join(more[0].split()))
    w("sample_article.html", html)

    w("malformed.html", """<!doctype html>
<html><body>
<h1>Broken fixture
<p>This document never closes its tags. A parser in strict mode fails here; a
lenient parser recovers and returns this sentence.
<div><span>Unclosed nesting
<ul><li>First item<li>Second item
<p>&amp; a stray entity: &nbsp; &notarealentity;
</body>""")


def build_messy_text():
    """Covers all seven cleaning steps Day 4 Task 4 asks for, plus hyphenation.

    Written as bytes so the CRLF line endings, the mojibake and the control
    characters survive exactly; a normal text write would normalise them.
    """
    lines = [
        b"RAG Practice Manual                                   Page 3 of 12\r\n",
        b"\r\n",
        b"   Retrieval   augmented   generation   combines  two   stages.\r\n",
        b"\r\n",
        b"\r\n",
        b"\r\n",
        b"This line has trailing spaces.      \r\n",
        b"A word may be split across a line break as re-\r\n",
        b"trieval, and must be rejoined before chunking.\r\n",
        b"\r\n",
        "Smart punctuation: “quoted” ‘single’ — em dash – en dash… ellipsis.\r\n".encode("utf-8"),
        b"Mojibake from a double decode: it\xc3\xa2\xe2\x82\xac\xe2\x84\xa2s here, and \xc3\xa2\xe2\x82\xac\xc5\x93quoted\xc3\xa2\xe2\x82\xac\xc2\x9d too.\r\n",
        b"Control characters: bell\x07 and vertical tab\x0b and a null-ish \x1a marker.\r\n",
        "Bullets: • first · second ▪ third\r\n".encode("utf-8"),
        b"Contact practice@example.invalid or see https://example.invalid/docs?q=rag&p=2\r\n",
        b"Non-breaking\xc2\xa0spaces\xc2\xa0between\xc2\xa0words.\r\n",
        b"\r\n",
        b"RAG Practice Manual                                   Page 4 of 12\r\n",
        b"\r\n",
        b"Tabs\tseparate\tthese\tcolumns.\r\n",
        b"A line ending in a soft hyphen com-\r\n",
        b"pletes on the next line.\r\n",
        b"\r\n",
        b"Copyright 2026 Practice Site. All rights reserved.\r\n",
    ]
    with open(os.path.join(ROOT, "messy_text.txt"), "wb") as fh:
        fh.write(b"".join(lines))


def build_small_fixtures():
    # Day 1 Task 1 names sample.txt explicitly and requires at least 5 sentences.
    w("sample.txt", """Retrieval-augmented generation answers a question using text the system looked up first.
The lookup step searches a collection and returns the passages most likely to bear on the question.
Those passages are placed into the prompt alongside the question itself.
The model then writes an answer that is supposed to rest on the supplied passages rather than on memory.
Because the passages carry identifiers, each sentence of the answer can be traced back to a source.
Is that always reliable? No: a model asked a question the passages do not cover may still answer confidently.
That failure is the reason evaluation sets include questions the collection cannot answer!""")

    with open(os.path.join(ROOT, "empty.txt"), "w", encoding="utf-8") as fh:
        fh.write("")


def build_pdf():
    index = {d["slug"]: d for d in corpus.DOCS}
    layout = [
        ("Introduction", ["rag_intro"]),
        ("The Pipelines", ["rag_pipeline"]),
        ("Chunking", ["chunk_fixed", "chunk_overlap"]),
        ("Embeddings", ["emb_what", "emb_cosine"]),
        ("Vector Stores", ["vdb_concepts", "vdb_chromadb"]),
        ("Retrieval", ["ret_bm25", "ret_semantic"]),
        ("Hybrid Search and Reranking", ["ret_hybrid", "ret_rerank"]),
        ("Prompting and Grounding", ["rag_prompting", "rag_grounding"]),
        ("Evaluation", ["eval_retrieval_metrics", "eval_dataset_design"]),
        ("Operations and Security", ["sec_api_keys", "ops_observability"]),
    ]
    header = "RAG Practice Manual"
    pages = []
    for i, (section, slugs) in enumerate(layout):
        blocks = []
        if i == 0:
            blocks.append(("h1", "RAG Practice Manual"))
            blocks.append(("body", "A synthetic multi-page manual for extraction, page "
                                   "metadata, cleaning and chunking exercises. Every page "
                                   "carries a running header and a numbered footer so that "
                                   "header and footer removal has something to detect."))
        blocks.append(("h2", "%d. %s" % (i + 1, section)))
        for slug in slugs:
            d = index[slug]
            if len(slugs) > 1:
                blocks.append(("h2", d["title"]))
            for para in d["body"].split("\n\n"):
                blocks.append(("body", " ".join(para.split())))
        pages.append((header, blocks))
    info = {
        "Title": "RAG Practice Manual",
        "Author": "RAG 10 Days Practice Assets",
        "Subject": "Synthetic fixture for PDF extraction and chunking exercises",
        "Keywords": "RAG, retrieval, chunking, embeddings, evaluation",
        "Creator": "RAG assets/_build/build.py",
        "Producer": "RAG assets/_build/build.py",
        "CreationDate": "D:20260314093000Z",
    }
    write_pdf(os.path.join(ROOT, "sample_rag_manual.pdf"), pages, info)
    return len(pages)


def build_readme(n_docs, n_pages):
    kinds = {}
    for q in corpus.QUERIES:
        kinds[q["kind"]] = kinds.get(q["kind"], 0) + 1
    topics = ", ".join("%s (%d)" % (h.lower(), len(d)) for _k, h, d in by_topic())
    corpus_words = sum(len(d["body"].split()) for d in corpus.DOCS)
    text = """# RAG Practice Assets

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
| `documents/` | {n_docs} topic documents, one per file, {corpus_words} words total | Days 5-9 |
| `documents.csv` | the same corpus as a table | Days 5-8 |
| `documents_metadata.json` | the same corpus with flat scalar metadata for filtering | Days 4-6, 9 |
| `evaluation_questions.json` | {n_q} questions with **graded relevance labels** | Days 6, 9 |
| `test_queries.txt` | the same questions as plain lines | Days 5-9 |
| `sample_rag_manual.pdf` | {n_pages}-page PDF with title/author metadata, running header and numbered footer | Day 4, 7 |
| `long_rag_corpus.md` / `.txt` | one continuous document, {corpus_words}+ words, varied paragraph lengths | Day 4 |
| `sample_technical_doc.md` | structured Markdown: nested headings, list, table, code fence | Day 4, 8 |
| `sample_article.html` | article with nav, ad, sidebar, footer, script, table, list, links and meta tags | Day 4 |
| `sample.txt` | short multi-sentence file | Day 1 |
| `messy_text.txt` | whitespace, CRLF, smart quotes, mojibake, control characters, headers/footers, hyphenation, URLs and emails | Day 4 |
| `malformed.html` | unclosed tags and a stray entity | Day 4 |
| `empty.txt` | zero bytes | error handling |

Topics in `documents/`: {topics}.

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
"relevance_grades": {{ "doc-037": 2, "doc-041": 1 }}
```

`2` means the document answers the question, `1` means it is useful supporting context,
and anything unlisted is not relevant. Those grades are what make recall@k, precision@k,
MRR and nDCG computable, and they are the only way the Day 9 tasks that say
"measure improvement" can report a number.

Question kinds: {kinds}.

The `unanswerable` questions have no relevant documents by design. A correct system
declines to answer them; Day 6 Task 3 needs exactly this case to test what happens when
nothing passes the similarity threshold.

## Suggested progression

| Day | Use |
| --- | --- |
| 1 | `sample.txt`, then `documents/` as a directory to batch-process |
| 4 | `sample_rag_manual.pdf`, `sample_article.html`, `sample_technical_doc.md` for extraction; `messy_text.txt` for the cleaning pipeline; `long_rag_corpus.md` for comparing chunking strategies; `malformed.html` and `empty.txt` for error handling |
| 5 | Embed `documents/` ({n_docs} documents, over the 50 the assignment asks for), search with `test_queries.txt`, filter on the fields in `documents_metadata.json` |
| 6 | `documents/` as the knowledge base, `evaluation_questions.json` to score retrieval and answers, the `unanswerable` questions to test thresholds |
| 7-8 | The same corpus, so a from-scratch implementation and a framework one can be compared on equal footing |
| 9 | `test_queries.txt` with the trap and mismatch questions, scored against `relevance_grades` |
| 10 | Serve the same corpus behind the API and UI |
"""
    w("README.md", text.format(
        n_docs=n_docs, n_pages=n_pages, n_q=len(corpus.QUERIES),
        corpus_words=corpus_words, topics=topics,
        kinds=", ".join("%s (%d)" % (k, v) for k, v in sorted(kinds.items()))))


def main():
    n_docs, removed = build_documents()
    build_csv()
    build_metadata()
    build_eval()
    build_queries()
    build_long_corpus()
    build_technical_doc()
    build_article_html()
    build_messy_text()
    build_small_fixtures()
    n_pages = build_pdf()
    build_readme(n_docs, n_pages)

    print("documents written : %d" % n_docs)
    if removed:
        print("stale removed     : %d (%s)" % (len(removed), ", ".join(removed)))
    print("queries written   : %d" % len(corpus.QUERIES))
    print("pdf pages         : %d" % n_pages)
    print()
    import verify
    verify.main()


if __name__ == "__main__":
    main()
