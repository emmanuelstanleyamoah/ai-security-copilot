# RAG design

The knowledge base is the markdown in `knowledge_base/`. Each file is one document: a technique card, a framework note, or a runbook.

## Index

`TfidfKnowledgeBase` fits a TF-IDF vectorizer over those files at startup. Search uses cosine similarity and drops scores under 0.08. The checked-in questions in `tests/test_investigation.py` expect the right file inside the top 3.

## Why lexical first

Technique IDs and product terms are exact strings. Lexical search is strong on `T1566`, `PowerShell`, and `impossible travel`, and it does not download an embedding model. Paraphrases that share no terms will miss. That miss becomes an empty citation list, and the narrative says the knowledge base did not clear the threshold.

## Chroma adapter

`ChromaKnowledgeBase` queries a persisted Chroma collection when `CHROMA_PATH` is set and the `chromadb` package is installed. The hit shape matches the lexical retriever, so the graph does not change. Chunk metadata should keep `source` and `title`.

## Citations

The report lists source file, title, and score. The narrative is not allowed to name a document that was not retrieved. Tests check that a phishing alert cites `mitre-t1566.md`.

## Corpus size

Seven short documents. That is a demo corpus, not a SOC wiki. Add runbooks as markdown and extend the recall test when you do.
