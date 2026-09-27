# Implement a function `chunk_with_overlap(text, chunk_size, overlap)` that:
#
# - Splits text into chunks of `chunk_size` characters
# - Each chunk overlaps with the previous one by `overlap` characters
# - Returns a list of dictionaries, each containing:
#   - `chunk_id`: Sequential number (1, 2, 3...)
#   - `text`: The chunk text
#   - `start_pos`: Starting character position
#   - `end_pos`: Ending character position
#   - `word_count`: Number of words in chunk


def chunk_with_overlap(text: str, chunk_size: int, overlap: int) -> list:
    chunks = []
    chunk_id = 1
    start = 0

    step = chunk_size - overlap
    end = min(start + chunk_size, len(text))

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        word_count = len(chunk_text.split())
        chunk = {
            "chunk_id": chunk_id,
            "text": chunk_text,
            "start_pos": start,
            "end_pos": end,
            "word_count": word_count,
        }
        chunks.append(chunk)

        start += step
        chunk_id += 1

    return chunks


filename = "../RAG assets/sample.txt"
# reading the basic file given its path as argument
with open(filename, "r", encoding="utf-8") as file:
    content = file.read()

print(content)
print(chunk_with_overlap(content, chunk_size=20, overlap=2))
