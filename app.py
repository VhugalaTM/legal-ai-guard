import os
import streamlit as st

from ingest import ingest_pdf
from generate import generate_answer
from audit import log_event, read_log

st.set_page_config(page_title="Legal AI Guard", page_icon="", layout="centered")

st.title("Legal AI Guard")
st.caption("Governed AI document assistant for small law firms")

# --- Session state: track the currently selected matter ---
if "matter" not in st.session_state:
    st.session_state.matter = ""

st.header("1. Select a matter")
matter_input = st.text_input(
    "Matter name (e.g. client surname)",
    value=st.session_state.matter,
    placeholder="Mulaudzi"
)
if matter_input.strip():
    st.session_state.matter = matter_input.strip()

current_matter = st.session_state.matter
if current_matter:
    st.info(f"Active matter: **{current_matter}**")
else:
    st.warning("Enter a matter name to begin.")

st.divider()

# --- Upload section ---
st.header("2. Upload documents into this matter")
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None and current_matter:
    if st.button("Ingest into matter"):
        upload_dir = "data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        save_path = os.path.join(upload_dir, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("Reading and indexing the document..."):
            try:
                count = ingest_pdf(save_path, current_matter)
                if count > 0:
                    st.success(f"Ingested {count} chunks into matter '{current_matter}'.")
                else:
                    st.error("No extractable text found in this PDF (it may be scanned).")
            except ValueError as e:
                st.error(f"Upload blocked: {e}")
                st.caption("This event has been logged in the audit trail.")
elif uploaded_file is not None and not current_matter:
    st.warning("Enter a matter name first.")

st.divider()

# --- Ask section ---
st.header("3. Ask a question about this matter's documents")
question = st.text_input("Your question", placeholder="What is the monthly rent?")

if st.button("Ask"):
    if not current_matter:
        st.error("Select a matter first.")
    elif not question.strip():
        st.error("Type a question.")
    else:
        with st.spinner("Searching this matter's documents..."):
            result = generate_answer(question, current_matter)

        if result["refused"]:
            st.warning("No answer found in this matter's documents.")
            st.caption(f"Reason: {result['reason']}")
        else:
            st.markdown("### Answer")
            st.write(result["answer"])

            if result.get("pii_redactions", 0) > 0:
                st.caption(f"{result['pii_redactions']} PII item(s) redacted from this answer.")

            st.markdown("### Sources")
            for i, c in enumerate(result["citations"], 1):
                st.markdown(f"- **[SOURCE {i}]** `{c['source']}` (chunk {c['chunk_index']})")