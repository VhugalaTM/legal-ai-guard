import os
import re
from openai import OpenAI
from dotenv import load_dotenv

from retrieve import retrieve_chunks
from guard import redact_pii

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "openai/gpt-oss-120b"


def build_prompt(question, chunks, metadatas):
    """Build a directive, citation-required prompt."""
    context = ""
    for i, (chunk, meta) in enumerate(zip(chunks, metadatas), 1):
        context += f"\n--- SOURCE {i} (file={meta.get('source')}, chunk={meta.get('chunk_index')}) ---\n"
        context += chunk.strip() + "\n"

    return f"""You are a legal document assistant helping a lawyer review documents.

Below are SOURCES extracted from the client's documents. Use them to answer the QUESTION.

REQUIRED FORMAT:
- Answer in 1-3 sentences.
- After every factual sentence, put the source number in square brackets, like [1] or [2].
- Example answer: "The monthly rent is R5,000 [1]. The deposit is R3,000 [1]."
- Only refuse if NONE of the sources mention anything related to the question. If the sources are relevant but incomplete, answer with what IS there and cite it.
- Never use outside knowledge.

SOURCES:
{context}

QUESTION: {question}

ANSWER:"""


def has_citation(text):
    """Accept [1], [SOURCE 1], [Source 1], (Source 1), source 1, etc."""
    patterns = [
        r"\[\s*source\s*\d+\s*\]",   # [SOURCE 1], [source 1]
        r"\[\s*\d+\s*\]",              # [1]
        r"\(\s*source\s*\d+\s*\)",     # (Source 1)
        r"\bsource\s*\d+\b",           # source 1
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def generate_answer(question, matter):
    """Retrieve chunks for a matter, then answer with citations."""
    chunks, metadatas = retrieve_chunks(question, matter, n_results=3)

    if not chunks:
        return {
            "answer": "No answer found in the provided documents.",
            "citations": [],
            "refused": True,
            "reason": "no_chunks_retrieved"
        }

    prompt = build_prompt(question, chunks, metadatas)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    answer = response.choices[0].message.content.strip()

    # Build citation list
    citations = [
        {"source": meta.get("source"), "chunk_index": meta.get("chunk_index")}
        for meta in metadatas
    ]

    # Citation-required rule: if the answer isn't a refusal but has no citation, refuse
    if answer != "No answer found in the provided documents." and not has_citation(answer):
        return {
            "answer": "No answer found in the provided documents.",
            "citations": citations,
            "refused": True,
            "reason": "no_citation_in_output"
        }

    redacted_answer, redaction_count = redact_pii(answer)
    if redaction_count > 0:
        from audit import log_event
        log_event(
            action="output_pii_redacted",
            matter=matter,
            detail={"count": redaction_count}
        )

    return {
        "answer": redacted_answer,
        "citations": citations,
        "refused": False,
        "reason": None,
        "pii_redactions": redaction_count
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print('Usage: python generate.py "<question>" <matter>')
        sys.exit(1)

    question = sys.argv[1]
    matter = sys.argv[2]

    result = generate_answer(question, matter)

    print(f"\nMatter: {matter}")
    print(f"Question: {question}\n")
    print("ANSWER:")
    print(result["answer"])
    print("\nCITATIONS:")
    for i, c in enumerate(result["citations"], 1):
        print(f"  [SOURCE {i}] {c['source']} (chunk {c['chunk_index']})")

    if result["refused"]:
        print(f"\n[REFUSED] reason: {result['reason']}")