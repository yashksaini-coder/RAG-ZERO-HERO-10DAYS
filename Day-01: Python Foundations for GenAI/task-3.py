# Create a `DocumentManager` class that:
#
# - Can load multiple documents
# - Stores each document with metadata (filename, content, word_count)
# - Has a method to find documents by keyword (searches in content)
# - Has a method to get statistics across all documents
# - Has a method to export all document info to a JSON file
#
# **Requirements:**
#
# - Use a dictionary to store documents (key: filename, value: document data)
# - Implement `add_document(filename, content)`
# - Implement `search_documents(keyword)` → returns list of matching filenames
# - Implement `get_all_stats()` → returns summary statistics
# - Implement `export_to_json(output_file)` → saves all document data

import json
from pathlib import Path


class DocumentManager:
    def __init__(self) -> None:
        self.documents = {}

    def __str__(self) -> str:
        # FIXED: this used to return the requirement text, which said nothing about
        # the object. Reporting the real contents would have exposed the add_document
        # bug the first time it was printed -- a __str__ that shows state is a
        # debugging tool, not a description of the class.
        return f"DocumentManager({len(self.documents)} documents)"

    def add_document(self, filename, content):
        word_count = len(content.split())
        # FIXED: this was `self.documents = {...}`, which rebound the attribute to a
        # brand new one-document dict on every call. Only the last document survived,
        # and it was keyed by "filename"/"content"/"word_count" instead of by the
        # filename -- so search_documents() got a string where it expected a dict and
        # crashed with "TypeError: string indices must be integers".
        # `self.documents[filename] = ...` mutates the existing dict, which is what
        # the requirement "key: filename, value: document data" asks for.
        self.documents[filename] = {
            "filename": filename,
            "content": content,
            "word_count": word_count,
        }

    def search_documents(self, keyword):
        # Search the documents through the keywords passed as input
        matches = []
        keyword = keyword.lower()
        for filename, document in self.documents.items():
            content = document["content"].lower()
            if keyword in content:
                matches.append(filename)
        return matches

    def get_all_stats(self):
        total_documents = len(self.documents)
        total_words = 0
        total_characters = 0

        for document in self.documents.values():
            total_characters += len(document["content"])
            total_words += document["word_count"]

        # FIXED: the average used to be calculated inside the loop above. That made
        # the `else: average = 0` branch unreachable -- when total_documents is 0 the
        # loop body never runs at all -- so get_all_stats() on an empty manager raised
        # "UnboundLocalError: cannot access local variable 'average'" instead of
        # returning zeros. Computing it after the loop handles the empty case.
        average = total_words / total_documents if total_documents > 0 else 0

        return {
            "total_documents": total_documents,
            "total_words": total_words,
            "total_characters": total_characters,
            "average_words_per_document": average,
        }

    def export_to_json(self, output_file):
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(self.documents, file, indent=4, ensure_ascii=False)


# Create manager
manager = DocumentManager()

# CHANGED: the three hand-written strings that used to live here are now the real
# practice corpus in "RAG assets/documents/". Paths are resolved relative to THIS
# file rather than the working directory, so the script behaves the same whether it
# is run from the Day-01 folder or from the repo root.
HERE = Path(__file__).resolve().parent
CORPUS = HERE.parent / "RAG assets" / "documents"

if not CORPUS.is_dir():
    raise SystemExit(f"Corpus directory not found: {CORPUS}")

# Add documents -- one add_document() call per file, which is what
# "can load multiple documents" means for this class.
for path in sorted(CORPUS.glob("*.txt")):
    manager.add_document(path.name, path.read_text(encoding="utf-8"))

# FIXED: the throwaway `obj = DocumentManager(); print(obj)` at the top of this
# section printed an empty manager before anything was added. Printing here shows
# the document count actually growing, which is the useful check.
print(manager)

# Search
results = manager.search_documents("chunk")
print(f"\nDocuments containing 'chunk': {len(results)}")
for filename in results:
    print("  ", filename)

# Note how audio_chunk_module.txt appears above: it is about reading audio frames,
# not about splitting documents. Keyword matching cannot tell the difference, which
# is the whole reason Day 9 introduces reranking.

# search_documents() matches SUBSTRINGS, so short keywords hit words that merely
# contain them. Compare these two counts before deciding how search should behave:
print(f"\nSubstring match for 'ai': {len(manager.search_documents('ai'))} documents")
print("  (matches 'domain', 'available', 'explained', ... not just the word 'AI')")

# Statistics
stats = manager.get_all_stats()
print("\nDocument statistics:")

for key, value in stats.items():
    print(f"{key}: {value}")

# Export
manager.export_to_json(HERE / "documents.json")
print("\nExport complete!")
