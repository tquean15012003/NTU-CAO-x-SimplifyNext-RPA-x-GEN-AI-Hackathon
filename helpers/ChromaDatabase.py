from typing import TypedDict
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader

import os

class Metadata(TypedDict):
    source: str
    page: str
    content: str
    
class CustomDocument(TypedDict):
    title: str # This is for title
    metadata: Metadata

class ChromaDatabase:
    def __init__(self):
        pdf_folder_path = f"{os.getcwd()}/docs"
        documents = []
        for file in os.listdir(pdf_folder_path):
            if file.endswith('.pdf'):
                pdf_path = os.path.join(pdf_folder_path, file)
                loader = PyPDFLoader(pdf_path)
                documents.extend(loader.load())

        processed_documents = []
        for document in documents:
            document.metadata['source'] = document.metadata['source'].split("/")[-1].split(".")[0]
            document.metadata['content'] = document.page_content
            document.page_content = document.metadata['source']
            processed_documents.append(document)
            
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        chunked_documents = text_splitter.split_documents(processed_documents)
        self.dbstore = Chroma.from_documents(chunked_documents, OpenAIEmbeddings())

    def query(self, query: str) -> list[CustomDocument]:
        # return self.chunked_documents
        docs = self.dbstore.similarity_search(query)
        return docs
