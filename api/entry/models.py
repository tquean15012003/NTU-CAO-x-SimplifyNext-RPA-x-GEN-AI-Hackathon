from pydantic import BaseModel

SYSTEM_MESSAGE_PREFIX = (
    """You are an email assistant. You are about to receive an email body and reply to it. Sign your name as "Email Assistant". You have to use the following information to generate an appropriate reply\n"""
)

MODEL = "gpt-3.5-turbo"
# MODEL = "gpt-4"

class CreateEntry(BaseModel):
    title: str
    description: str
    sender: str

