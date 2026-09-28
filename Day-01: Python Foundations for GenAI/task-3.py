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


class DocumentManager:
    def __init__(self) -> None:
        self.documents = {}

    def __str__(self) -> str:
        return (
            "Uses a dictionary to store documents (key: filename, value: document data)"
        )

    def add_document(self, filename, content):
        word_count = len(content.split())
        self.documents = {
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

            if total_documents > 0:
                average = total_words / total_documents
            else:
                average = 0

        return {
            "total_documents": total_documents,
            "total_words": total_words,
            "total_characters": total_characters,
            "average_words_per_document": average,
        }

    def export_to_json(self, output_file):
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(self.documents, file, indent=4, ensure_ascii=False)


obj = DocumentManager()
print(obj)


# Create manager
manager = DocumentManager()

# Add documents
manager.add_document("python.txt", "Python is easy to learn and useful for AI.")

manager.add_document("rag.txt", "RAG retrieves relevant documents for AI.")

manager.add_document("solana.txt", "Solana programs execute instructions.")

# Search
results = manager.search_documents("AI")
print("Search results:", results)

# Statistics
stats = manager.get_all_stats()
print("\nDocument statistics:")

for key, value in stats.items():
    print(f"{key}: {value}")

# Export
manager.export_to_json("documents.json")
print("\nExport complete!")
