# Write a function `preprocess_text(text)` that:
#
# - Converts text to lowercase
# - Removes all punctuation (keep spaces)
# - Removes extra whitespace (multiple spaces → single space)
# - Removes leading/trailing whitespace
# - Returns the cleaned text
#
# **Bonus:** Also create a function that removes stop words (common words like "the", "a", "an", "is", etc.)


def preprocess_text(text: str):
    text = text.lower()
    punctuation = ".,!?;:\"'()[]{}-_/\\@#$%^&*+=<>|`~"
    clean_text = ""

    for char in text:
        if char not in punctuation:
            clean_text += char

    # split whitespaces i.e, multiple spaces and single space
    words = clean_text.split()
    clean_text = " ".join(words)

    return clean_text


with open("../RAG assets/test_queries.txt", "r", encoding="utf-8") as file:
    text = file.read()

print("-" * 80, "\n", "original text is: ", text)

res = preprocess_text(text)

print("-" * 80, "\n", "Preprocessed text is: ", res)
