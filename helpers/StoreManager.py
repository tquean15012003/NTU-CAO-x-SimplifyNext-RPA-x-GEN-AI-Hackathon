from helpers.ChromaDatabase import ChromaDatabase
from dotenv import load_dotenv
import os
class StoreManager:
    def __init__(self):
        load_dotenv()
        os.environ['OPENAI_API_KEY'] = "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"
        self.emails = []
        self.chroma_database = ChromaDatabase()


store_manager = StoreManager()