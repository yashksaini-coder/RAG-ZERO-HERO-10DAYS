#!/usr/bin/env python3
"""Check the generated assets against what the assignments actually require.

    python3 "RAG assets/_build/verify.py"

Exits non-zero on the first failing group. Each check names the assignment it
comes from, so a failure says which day breaks rather than just "assertion
error". Uses only the standard library.
"""

import collections
import csv
import json
import math
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

FAILURES = []
CHECKS = 0


def check(cond, label, detail=""):
    global CHECKS
    CHECKS += 1
    if cond:
        print("  ok    %s" % label)
    else:
        print("  FAIL  %s%s" % (label, ("  -- " + detail) if detail else ""))
        FAILURES.append(label)


def read(rel, mode="r"):
    path = os.path.join(ROOT, rel)
    if mode == "rb":
        return open(path, "rb").read()
    return open(path, encoding="utf-8").read()


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 25]


# ---------------------------------------------------------------------------
# A compact BM25, used to prove that the lexical-trap and vocabulary-mismatch
# documents actually behave the way the README claims. Without this the claim
# is just a comment.
# ---------------------------------------------------------------------------

def tokenize(s):
    return re.findall(r"[a-z0-9]+", s.lower())


def bm25_rank(corpus_tokens, query, k1=1.5, b=0.75):
    n = len(corpus_tokens)
    avgdl = sum(len(t) for t in corpus_tokens.values()) / n
    df = collections.Counter()
    for toks in corpus_tokens.values():
        for t in set(toks):
            df[t] += 1
    scores = {}
    q = tokenize(query)
    for key, toks in corpus_tokens.items():
        tf = collections.Counter(toks)
        dl = len(toks)
        s = 0.0
        for term in q:
            if term not in tf:
                continue
            idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
            s += idf * tf[term] * (k1 + 1) / (tf[term] + k1 * (1 - b + b * dl / avgdl))
        scores[key] = s
    return [k for k, _ in sorted(scores.items(), key=lambda kv: -kv[1])]


def main():
    print("Verifying assets in %s\n" % ROOT)

    docdir = os.path.join(ROOT, "documents")
    files = sorted(f for f in os.listdir(docdir) if f.endswith(".txt"))
    bodies = {f[:-4]: read("documents/" + f) for f in files}
    meta = json.loads(read("documents_metadata.json"))
    rows = list(csv.DictReader(open(os.path.join(ROOT, "documents.csv"), encoding="utf-8")))
    ev = json.loads(read("evaluation_questions.json"))
    questions = ev["questions"]

    print("Corpus size (Day 5 Tasks 3/4/5, Day 6 Task 1)")
    check(len(files) >= 50, "at least 50 documents (Day 5 Task 4)", "found %d" % len(files))
    check(len(files) >= 30, "at least 30 documents (Day 5 Task 5)", "found %d" % len(files))
    check(len(rows) == len(files) == len(meta),
          "documents/, documents.csv and documents_metadata.json agree on count",
          "%d / %d / %d" % (len(files), len(rows), len(meta)))

    print("\nDocument size (Day 4 Tasks 3/5, Day 5 mini project chunk size 400-500)")
    short = [s for s, t in bodies.items() if len(t) < 500]
    check(not short, "every document exceeds 500 characters so it splits at a 400-500 "
                     "character chunk size", "too short: %s" % ", ".join(short[:5]))
    words = [len(t.split()) for t in bodies.values()]
    check(min(words) >= 80, "every document has at least 80 words", "min %d" % min(words))

    print("\nDocument independence (Day 5 Task 2, Day 6 Task 3)")
    seen, dupes = {}, []
    for slug, text in bodies.items():
        for s in sentences(text):
            key = " ".join(s.lower().split())
            if key in seen:
                dupes.append((seen[key], slug, s[:60]))
            seen[key] = slug
    check(not dupes, "no sentence is shared between two documents",
          "%d shared: %s" % (len(dupes), dupes[:2]))

    print("\nCross-file identity (all days)")
    csv_ids = [r["id"] for r in rows]
    meta_ids = [m["id"] for m in meta]
    check(csv_ids == meta_ids, "documents.csv and documents_metadata.json use the same ids")
    check(len(set(csv_ids)) == len(csv_ids), "document ids are unique")
    known = set(meta_ids)
    missing_src = [m["source"] for m in meta
                   if not os.path.exists(os.path.join(ROOT, m["source"]))]
    check(not missing_src, "every metadata source path exists on disk", str(missing_src[:3]))
    bad_ref = [(q["id"], i) for q in questions for i in q["relevant_ids"] if i not in known]
    check(not bad_ref, "every relevant_id in the evaluation set is a real document",
          str(bad_ref[:3]))
    slug_by_id = {m["id"]: m["slug"] for m in meta}
    mismatch = [q["id"] for q in questions
                if [slug_by_id[i] for i in q["relevant_ids"]] != q["relevant_slugs"]]
    check(not mismatch, "relevant_ids and relevant_slugs agree", str(mismatch[:3]))

    print("\nMetadata shape (Chroma rejects nested values and None)")
    bad = [(m["id"], k) for m in meta for k, v in m.items()
           if not isinstance(v, (str, int, float, bool))]
    check(not bad, "all metadata values are flat scalars", str(bad[:3]))

    print("\nEvaluation set (Day 6, Day 9 'measure improvement')")
    check(len(questions) >= 30, "at least 30 questions", "found %d" % len(questions))
    graded = [q for q in questions if q["relevance_grades"]]
    check(len(graded) >= 30, "at least 30 questions carry relevance grades",
          "found %d" % len(graded))
    unans = [q for q in questions if not q["answerable"]]
    check(len(unans) >= 3, "at least 3 unanswerable questions (Day 6 Task 3)",
          "found %d" % len(unans))
    check(all(not q["relevant_ids"] for q in unans),
          "unanswerable questions have no relevant documents")
    grades = {g for q in questions for g in q["relevance_grades"].values()}
    check(grades <= {1, 2} and 2 in grades, "grades are 1 or 2 and both are used", str(grades))
    covered = {s for q in questions for s in q["relevant_slugs"]}
    uncovered = sorted(set(bodies) - covered - {"offtopic_sourdough", "offtopic_tomatoes"})
    check(not uncovered, "every in-domain document is the answer to some question",
          "uncovered: %s" % uncovered[:5])
    multi = [q for q in questions if len([g for g in q["relevance_grades"].values() if g == 2]) > 1]
    check(len(multi) >= 3, "at least 3 questions need more than one source",
          "found %d" % len(multi))

    print("\nRetrieval fixtures behave as documented (Day 9 Tasks 2/4)")
    toks = {s: tokenize(t) for s, t in bodies.items()}
    traps = [q for q in questions if q["kind"] == "lexical_trap"]
    mism = [q for q in questions if q["kind"] == "vocabulary_mismatch"]
    check(len(traps) >= 1 and len(mism) >= 1, "trap and mismatch questions exist")
    def primaries(q):
        return [s for s, i in zip(q["relevant_slugs"], q["relevant_ids"])
                if q["relevance_grades"][i] == 2]

    # A lexical trap works when a document that does NOT answer the question
    # outranks the one that does, purely on shared keywords.
    trap_hits = [q["id"] for q in traps
                 if bm25_rank(toks, q["question"])[0] not in primaries(q)]
    check(len(trap_hits) == len(traps),
          "BM25 ranks a non-answering document first for every lexical trap",
          "worked for %d of %d" % (len(trap_hits), len(traps)))

    # A vocabulary mismatch works when lexical ranking misses a document that
    # genuinely answers the question, leaving something for semantic search to win.
    mism_hits = [q["id"] for q in mism
                 if any(p not in bm25_rank(toks, q["question"])[:5] for p in primaries(q))]
    check(len(mism_hits) == len(mism),
          "BM25 misses an answering document for every vocabulary-mismatch question "
          "(so semantic search has something to win)",
          "worked for %d of %d" % (len(mism_hits), len(mism)))
    check(any(m["topic"] == "offtopic" for m in meta),
          "out-of-domain documents exist for threshold and filter tests")

    print("\nLong corpus (Day 4 Task 3: 'at least 2000 words')")
    md = read("long_rag_corpus.md")
    txt = read("long_rag_corpus.txt")
    check(len(md.split()) >= 2000, "at least 2000 words", "%d" % len(md.split()))
    inline = [ln for ln in md.split("\n") if "##" in ln and not ln.startswith("#")]
    check(not inline, "no heading is embedded inside a paragraph line",
          "%d broken lines" % len(inline))
    paras = [p for p in md.split("\n\n") if p.strip() and not p.startswith("#")]
    check(len(paras) == len(set(paras)), "no paragraph appears twice",
          "%d duplicates" % (len(paras) - len(set(paras))))
    lens = [len(p.split()) for p in paras]
    spread = max(lens) / min(lens)
    check(spread >= 3,
          "paragraph lengths vary enough that chunking strategies differ (max/min >= 3)",
          "spread %.1f" % spread)
    check("##" not in txt, "the .txt variant has no Markdown syntax left")

    print("\nPDF (Day 4 Task 1, Day 7)")
    pdf_path = os.path.join(ROOT, "sample_rag_manual.pdf")
    raw = open(pdf_path, "rb").read()
    n_pages = len(re.findall(rb"/Type\s*/Page[^s]", raw))
    check(raw.startswith(b"%PDF-"), "valid PDF header")
    check(n_pages >= 8, "at least 8 pages for page-metadata exercises", "%d" % n_pages)
    check(b"/Title" in raw and b"/Author" in raw, "carries Title and Author metadata")
    if shutil.which("pdftotext"):
        out = subprocess.run(["pdftotext", pdf_path, "-"], capture_output=True)
        text = out.stdout.decode("utf-8", "replace")
        check(out.returncode == 0 and len(text.split()) > 800,
              "pdftotext extracts more than 800 words", "%d words" % len(text.split()))
        check(text.count("RAG Practice Manual") >= n_pages - 1,
              "a running header appears on the pages (Day 4 Task 4 header removal)")
        check(len(re.findall(r"Page \d+ of \d+", text)) >= n_pages - 1,
              "a numbered footer appears on the pages")
        check("intentionally repeats the topic" not in text,
              "no filler padding text in the PDF")
    else:
        print("  skip  pdftotext not installed; text extraction not checked")

    print("\nCleaning fixture (Day 4 Task 4: all seven steps)")
    mess = read("messy_text.txt", "rb")
    for label, probe in [
        ("extra whitespace", b"   "),
        ("CRLF line endings", b"\r\n"),
        ("blank-line runs", b"\r\n\r\n\r\n"),
        ("tabs", b"\t"),
        ("smart quotes / dashes", "“".encode("utf-8")),
        ("mojibake", b"\xc3\xa2\xe2\x82\xac"),
        ("control characters", b"\x07"),
        ("non-breaking spaces", b"\xc2\xa0"),
        ("repeated page header/footer", b"Page 3 of 12"),
        ("copyright footer", b"Copyright 2026"),
        ("URL", b"https://"),
        ("email", b"@example.invalid"),
        ("hyphenation across a line break", b"re-\r\n"),
        ("bullet glyphs", "•".encode("utf-8")),
    ]:
        check(probe in mess, "messy_text.txt contains %s" % label)

    print("\nHTML fixtures (Day 4 Task 2)")
    html = read("sample_article.html")
    for label, probe in [("nav to strip", "<nav"), ("ad block to strip", 'class="ad"'),
                         ("sidebar to strip", "<aside"), ("footer to strip", "<footer"),
                         ("script to strip", "<script"), ("comment", "<!--"),
                         ("article container", "<article"), ("author metadata", 'name="author"'),
                         ("publish date", "article:published_time"), ("list", "<ul>"),
                         ("table", "<table>"), ("code block", "<pre><code>"),
                         ("links", "<a href=")]:
        check(probe in html, "sample_article.html has %s" % label)
    bad = read("malformed.html")
    check(bad.count("<p") > bad.count("</p>"), "malformed.html really has unclosed tags")
    check(os.path.getsize(os.path.join(ROOT, "empty.txt")) == 0, "empty.txt is zero bytes")

    print("\nMarkdown fixture (Day 4, Day 8 structure-aware loaders)")
    tech = read("sample_technical_doc.md")
    for label, probe in [("h1", "\n# "), ("h2", "\n## "), ("table", "| --- |"),
                         ("list", "\n- "), ("code fence", "```python"), ("blockquote", "\n> ")]:
        check(probe in "\n" + tech, "sample_technical_doc.md has %s" % label)

    print("\nDay 1 fixture")
    samp = read("sample.txt")
    n_sent = len(re.findall(r"[.!?]", samp))
    check(n_sent >= 5, "sample.txt has at least 5 sentences (Day 1 Task 1)", "%d" % n_sent)
    check(all(c in samp for c in ".!?"),
          "sample.txt uses all three terminators so splitting on . ! ? is exercised")

    print("\n%d checks, %d failures" % (CHECKS, len(FAILURES)))
    if FAILURES:
        print("\nFAILED:")
        for f in FAILURES:
            print("  - " + f)
        sys.exit(1)
    print("All asset requirements satisfied.")


if __name__ == "__main__":
    main()
