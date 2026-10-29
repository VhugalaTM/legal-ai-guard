import os
import uuid
import chromadb
from pypdf import PdfReader
from guard import detect_injection
from audit import log_event

# Where Chroma stores its database on disk
CHROMA_PATH = "data/chroma"

# The embedding function — local, no API needed
# sentence-transformers's all-MiniLM-L6-v2 is small (~80MB) and works on modest RAM
from chromadb.utils import embedding_functions

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

def get_collection():
    """Return (or create) the Chroma collection."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name="legal_docs",
        embedding_function=embedding_fn
    )

def split_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return [c for c in chunks if c.strip()]

def ingest_pdf(pdf_path, matter):
    """
    Read a PDF and store its chunks in Chroma.
    `matter` is a string like "Mokoena" or "Dlamini" - the security boundary.
    """
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += (page.extract_text() or "") + "\n"

    # --- SECURITY CONTROL: prompt-injection detection ---
    matches = detect_injection(full_text)
    if matches:
        from audit import log_event
        log_event(
            action="ingest_blocked_injection",
            matter=matter,
            detail={
                "file": os.path.basename(pdf_path),
                "matches": matches
            }
        )
        raise ValueError(
            f"SECURITY: prompt-injection pattern detected in "
            f"{os.path.basename(pdf_path)}. Ingest refused."
        )
    # --- END SECURITY CONTROL ---

    chunks = split_text(full_text)
    if not chunks:
        return 0

    collection = get_collection()

    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [
        {
            "matter": matter,
            "source": os.path.basename(pdf_path),
            "chunk_index": i
        }
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        metadatas=metadatas
    )

    return len(chunks)

def delete_matter(matter):
    """Delete all chunks for a given matter."""
    collection = get_collection()
    collection.delete(where={"matter": matter})
    print(f"Deleted all chunks for matter '{matter}'")

if __name__ == "__main__":
    # Quick manual test: put a PDF in data/uploads/ and run this
    import sys
    if len(sys.argv) != 3:
        print("Usage: python ingest.py <path_to_pdf> <matter_name>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    matter_name = sys.argv[2]

    count = ingest_pdf(pdf_path, matter_name)
    print(f"Ingested {count} chunks from {pdf_path} into matter '{matter_name}'")