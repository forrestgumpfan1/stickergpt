import os

from flask import Flask, render_template, request

from rag_faiss_vectorstore import (
    answer_question,
    extract_data,
    split_text,
    vectorize_and_store,
)

PDF_NAME = os.getenv("PDF_NAME", "SJA_handbook.pdf")

app = Flask(__name__)

_docstorage = None


def get_docstorage():
    global _docstorage
    if _docstorage is None:
        text = extract_data(PDF_NAME)
        docs = split_text(text)
        _docstorage = vectorize_and_store(docs, os.getenv("OPENAI_API_KEY"))
    return _docstorage


@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    question = None
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if question:
            docstorage = get_docstorage()
            answer = answer_question(question, os.getenv("OPENAI_API_KEY"), docstorage)
    return render_template("index.html", question=question, answer=answer)


if __name__ == "__main__":
    app.run(debug=True)
