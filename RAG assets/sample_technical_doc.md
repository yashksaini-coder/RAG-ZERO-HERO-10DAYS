# RAG Practice Handbook

## Overview

Retrieval-Augmented Generation, or RAG, connects a retrieval system with a language model. The retriever finds relevant source passages and the generator uses those passages to formulate an answer.

## Retrieval

Retrieval can be lexical, semantic, or hybrid. Lexical retrieval matches terms. Semantic retrieval compares embeddings. Hybrid retrieval combines both signals.

## Chunking

A document can be split by characters, tokens, sentences, or paragraphs. Overlap can preserve context across boundaries, but excessive overlap increases storage and retrieval redundancy.

## Metadata

Useful metadata includes source, page number, document ID, section, timestamp, and chunk index. Metadata makes debugging and filtering easier.

## Evaluation

A useful evaluation set contains questions whose answers are known. Track whether the correct source was retrieved and whether the generated answer is supported by that source.

## Deployment

A small application can expose indexing and querying through FastAPI and provide a Streamlit interface. Secrets should be supplied through environment variables rather than committed to source control.
