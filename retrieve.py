import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "data/chroma"

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name="legal_docs",
        embedding_function=embedding_fn
    )

def retrieve_chunks(question, matter, n_results=3):
    """
    Retrieve the most relevant chunks for a question,
    ONLY from the given matter.

    This is where matter isolation is enforced at query time.
    """
    collection = get_collection()

    results = collection.query(
        query_texts=[question],
        n_results=n_results,
        where={"matter": matter}       # THE security filter
    )

    # Chroma returns lists-of-lists; we want the inner list
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    return documents, metadatas


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python retrieve.py \"<question>\" <matter>")
        sys.exit(1)

    question = sys.argv[1]
    matter = sys.argv[2]

    docs, metas = retrieve_chunks(question, matter)

    if not docs:
        print(f"No chunks found for matter '{matter}'.")
        sys.exit(0)

    print(f"Found {len(docs)} chunk(s) in matter '{matter}':\n")
    for i, (doc, meta) in enumerate(zip(docs, metas), 1):
        print(f"--- Chunk {i} (source: {meta.get('source')}, index: {meta.get('chunk_index')}) ---")
        print(doc[:300] + ("..." if len(doc) > 300 else ""))
        print()