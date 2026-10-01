import os

from flask import Flask, render_template, request

from rag_faiss_vectorstore import (
    DEFAULT_PDF_NAME,
    answer_question,
    extract_data,
    split_text,
    vectorize_and_store,
)

PDF_NAME = os.getenv("PDF_NAME", DEFAULT_PDF_NAME)

app = Flask(__name__)


def build_docstorage():
    text = extract_data(PDF_NAME)
    docs = split_text(text)
    return vectorize_and_store(docs, os.getenv("OPENAI_API_KEY"))


# Process the PDF and build the vectorstore once, at server startup.
docstorage = build_docstorage()


@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    question = None
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if question:
            answer = answer_question(question, os.getenv("OPENAI_API_KEY"), docstorage)
    return render_template("index.html", question=question, answer=answer)

# Railway pings endpoint after a deploy. It only answers once the module has finished
# importing, which means the vectorstore above was built successfully.
@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5001)
