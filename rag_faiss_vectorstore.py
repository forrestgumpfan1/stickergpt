import os
import sys
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
#load_dotenv()
load_dotenv(override=True)

PROMPT = ChatPromptTemplate.from_template(
    "Use the following pieces of context to answer the question at the end. "
    "If you don't know the answer, just say that you don't know, don't try to make up an answer.\n\n"
    "{context}\n\n"
    "Question: {question}\n"
    "Helpful Answer:"
) 


def main():
    question = sys.argv[1]
    pdf_name = sys.argv[2]
    api_key = os.getenv("OPENAI_API_KEY")

    text = extract_data(pdf_name)
    docs = split_text(text)

    docstorage = vectorize_and_store(docs, api_key)
    response = answer_question(question, api_key, docstorage)

    print(response)
    # return response

def extract_data(pdf_name):
    loader = PyPDFLoader(pdf_name)
    data = loader.load()
    policy_text = ""
    for doc in data:
        if isinstance(doc, dict) and 'text' in doc:
            policy_text += doc['text']
        elif isinstance(doc, str):
            policy_text += doc
        else:
            policy_text += repr(doc)
    return policy_text

def split_text(text):
    ct_splitter = CharacterTextSplitter(separator='.', chunk_size=1000, chunk_overlap=200)
    docs = ct_splitter.split_text(text)
    return docs

def vectorize_and_store(docs, api_key):
    embedding_function = OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key)
    docstorage = FAISS.from_texts(docs, embedding_function)
    return docstorage

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def answer_question(question, api_key, docstorage):
    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), api_key=api_key)
    qa = (
        {"context": docstorage.as_retriever() | format_docs, "question": RunnablePassthrough()}
        | PROMPT
        | llm
        | StrOutputParser()
    )
    response = qa.invoke(question)
    return response

if __name__ == "__main__":
    main()