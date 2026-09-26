def calculate_document_stats(filename: str) -> dict:
    # - Returns a dictionary with:
    #   - Total characters (including spaces)
    #   - Total words
    #   - Total sentences (split by `.`, `!`, `?`)
    #   - Average words per sentence
    #   - Most common word (and its frequency)
    stats = {
        "total_chars": 0,
        "total_words": 0,
        "total_sentences": 0,
        "avg_words_per_sentence": 0.0,
        "commond_word": 0,
    }

    # reading the basic file given its path as argument
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read()

        words = content.split()
        lines = content.splitlines()

        frequency = {}

        for w in words:
            # remove common punctuation
            w = w.strip(".,!?;:\"'()[]{}").lower()
            if w == "":
                continue
            if w in frequency:
                frequency[w] += 1
            else:
                frequency[w] = 1
        most_common_word = None
        highest_frequency = 0

        for w, count in frequency.items():
            if count > highest_frequency:
                highest_frequency = count
                most_common_word = w

        stats["total_chars"] = len(content)
        stats["total_sentences"] = len(lines)
        stats["total_words"] = len(words)
        stats["avg_words_per_sentence"] = len(words) / len(lines)
        stats["commond_word"] = most_common_word

    return stats


y = "../RAG assets/sample.txt"

res = calculate_document_stats(y)

print("\n========== DOCUMENT STATS ==========")

for key, value in res.items():
    print(f"{key.replace('_', ' ').title():30}: {value}")

print("=====================================")
