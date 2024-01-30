from helpers.ChromaDatabase import ChromaDatabase
from dotenv import load_dotenv

class StoreManager:
    def __init__(self):
        load_dotenv()
        self.emails = []
        self.chroma_database = ChromaDatabase()


store_manager = StoreManager()
