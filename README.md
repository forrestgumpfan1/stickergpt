# StickerGPT

StickerGPT is a question-answering web app for the St. Joseph's Academy (SJA) student handbook, built for the SJA Science Fair. Ask a question in plain English, such as "What is the cell phone policy?", and StickerGPT answers using only what the handbook says.

It uses **retrieval-augmented generation (RAG)**. Instead of relying on what a language model happens to remember, the app first finds the handbook passages most relevant to the question, then asks the model to answer from those passages alone. If the handbook doesn't cover the question, the model is told to say it doesn't know rather than make something up.

## How it works

```
                 at startup                                   per question
┌──────────────┐   ┌──────────┐   ┌────────────┐   ┌──────────────┐   ┌───────────┐   ┌────────┐
│ Handbook PDF │ → │  Split   │ → │  Embed     │ → │ FAISS index  │ → │ Top       │ → │  LLM   │ → answer
│ (pypdf)      │   │  chunks  │   │  (OpenAI)  │   │ (in memory)  │   │ matches   │   │        │
└──────────────┘   └──────────┘   └────────────┘   └──────────────┘   └───────────┘   └────────┘
```

1. **Load.** `PyPDFLoader` reads `SJA_handbook.pdf`.
2. **Split.** The text is cut into chunks of about 1,000 characters on sentence boundaries, with 200 characters of overlap so ideas aren't cut in half.
3. **Embed.** Each chunk is converted to a vector with OpenAI's `text-embedding-3-small` model.
4. **Index.** The vectors are stored in a FAISS index held in memory. This happens once, when the server starts.
5. **Retrieve.** For each question, FAISS finds the chunks whose vectors are closest to the question's vector.
6. **Generate.** The chunks and the question go into a prompt for `gpt-4o-mini`, which writes the answer.

## Project structure

| File | Purpose |
|---|---|
| `app.py` | Flask web app. Builds the index at startup and serves the question page |
| `rag_faiss_vectorstore.py` | The RAG pipeline: load, split, embed, index, and answer. Also runs from the command line |
| `templates/index.html` | The question and answer page |
| `SJA_handbook.pdf` | The source document |
| `requirements.txt` | Python dependencies |

## Setup

Requires Python 3.12, or later, and an OpenAI API key.

```bash
git clone https://github.com/forrestgumpfan1/stickergpt.git
cd stickergpt
pipenv shell        # or your favorite virtual env 
pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```
OPENAI_API_KEY=sk-...
```

The `.env` file is listed in `.gitignore`, so the key never gets committed.

## Running

**Web app**

```bash
python app.py
```

Open http://127.0.0.1:5001. The first startup takes a few seconds while the handbook is embedded.

**Command line**

```bash
python rag_faiss_vectorstore.py "What is the cell phone policy?"
```

Add a second argument to use a different PDF.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | none (required) | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Chat model used to write answers |
| `PDF_NAME` | `SJA_handbook.pdf` | Document to answer questions from |

## Cost

Embedding the 81-page handbook costs a fraction of a cent and happens on each server start. Each question costs a fraction of a cent with `gpt-4o-mini`.

## Limitations

- Answers are only as good as the retrieved passages. A question worded very differently from the handbook's language may pull the wrong sections.
- Tables and multi-column layouts in the PDF may not extract cleanly.
- The index lives in memory, so it is rebuilt on every restart.
- StickerGPT can still make mistakes. The handbook itself is the authority.

## Future ideas

- Support multiple policy documents
- User accounts
- Show which handbook pages each answer came from

## Acknowledgments

Special thanks to my project mentor, Dr. James Davis.
The RAG pipeline is adapted from Dr. Davis' [article on LangChain](https://blog.agilephd.com/posts/llm_langchain_refactor_2026/).
