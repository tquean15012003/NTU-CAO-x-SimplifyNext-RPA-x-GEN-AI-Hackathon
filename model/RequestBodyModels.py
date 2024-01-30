from pydantic import BaseModel

class CreateEntry(BaseModel):
    title: str
    description: str
    sender: str