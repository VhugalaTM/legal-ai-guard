# AI Assistance Disclosure

This project was built by me with assistance from an AI assistant (DeepSeek). I am disclosing exactly what was AI-assisted and what was my own work, as required by the competition guide.

## What I did myself

- **Problem selection and framing.** I chose the AI & Cybersecurity challenge and the legal-industry scope based on my own reasoning about which sector has the widest capability gap.
- **All code was typed, run, tested, and debugged by me.** I set up Python 3.11, resolved the dependency conflict, installed libraries, ran every command, and verified every test output. When something failed, I read the error and worked through the fix.
- **All architectural decisions** - the four-layer design (input guard -> governed retrieval -> AI -> output guard -> audit log)  were made in conversation, but I chose to build them in this order and verified each control actually worked.
- **The demo scenarios** - matter isolation, injection blocking, PII redaction I created the test documents and tested the behavior.
- **All legal-industry research direction** (LPC, POPIA, small-firm capability gap) was my choice of jurisdiction and sector, though I used the AI to help me understand the landscape.

## What the AI assisted with

- **Code generation** - the AI provided code for `ingest.py`, `retrieve.py`, `generate.py`, `guard.py`, `audit.py`, and `app.py`. I typed it in, ran it, found bugs, and fixed them
- **Architecture advice** - the AI suggested the four-layer model and the "safe path is the easy path" framing, which I adopted.
- **Drafting assistance** - this README and this disclosure file were drafted with AI help, then reviewed by me.
- **Debugging** - when I hit setup errors (Python 3.15 dependency conflict, Groq model deprecation, circular import), the AI helped me diagnose them. I executed every fix myself.

## What is my own reasoning

- The choice to target **small law firms, not large ones**, because large firms have security teams and would undercut the thesis.
- The decision to test with **two matters containing distinct documents** to prove isolation, rather than relying on a single-document demo.
- The decision to **build all four controls at the layer they fire** (input / retrieval / output) rather than trying to do everything in a single prompt, because prompts can be jailbroken, but data-layer filters cannot.
- The honest disclosure of **limitations** in the README, rather than overclaiming.

## Tools used

- **DeepSeek** - used as described above.
- **Groq API** (`openai/gpt-oss-120b`) - used at runtime for answer generation.
- **Python 3.11, Streamlit, ChromaDB, sentence-transformers, pypdf** - open-source libraries (not AI-generated; standard packages).
- **GitHub** - version control.

## What was not AI-assisted

- No code was copy-pasted from another student's or existing project's repository.
- No pre-built legal AI platform was reused or wrapped. All security controls were written in this project.
- The test documents were either sourced from public sources or created by me; the malicious PDF was created by me specifically to test the injection control.

## Honest caveat

This project is a **prototype**, not a production system. It has not been validated with real law firms. The security controls are real and enforced in code, but the testing has been done by me on synthetic/sample documents. See the Known Limitations section of the README for the full list.