import logging

from openai import OpenAI
from fastapi import APIRouter
from langchain_core.documents import Document
from helpers.PIIManager.PIIMasking import PIIMaskingManager

from helpers.StoreManager import store_manager
from api.entry.models import MODEL, SYSTEM_MESSAGE_PREFIX, CreateEntry

router = APIRouter()

client = OpenAI()

logger = logging.getLogger(__name__)


@router.post("/create")
async def create_entry(email_details: CreateEntry):
    email_details_dict = email_details.model_dump()
    logger.info(f"Create entry called\n{email_details_dict}")
    answer, document = get_response_from_ai(email_details=email_details)
    email_details_dict.update({"answer": answer, "document": document.dict()})
    store_manager.emails.append(email_details_dict)
    return {"status": "success"}


def get_response_from_ai(email_details: CreateEntry) -> tuple[str, Document]:
    relevant_documents = store_manager.chroma_database.query(email_details.description)
    first_relevant_document = relevant_documents[0]
    logger.info(f"All relevant documents\n{first_relevant_document}")

    system_message = SYSTEM_MESSAGE_PREFIX + first_relevant_document.metadata["content"]
    pii_manager = PIIMaskingManager()
    question, deanonymizer_mapping = pii_manager.get_anonymized_text(email_details.description)
    logger.info(f"Question used: {question}")
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question},
        ],
        model=MODEL,
    )
    masked_answer = response.choices[0].message.content
    answer = pii_manager.get_deanonymized_text(masked_answer, deanonymizer_mapping)
    logger.info(f"Answer from {MODEL}:\n{answer}")
    return answer, first_relevant_document


@router.get("")
async def get_entries():
    emails = store_manager.emails.copy()
    logger.info(f"Retrieve all emails\n{emails}")
    return {"data": emails}
