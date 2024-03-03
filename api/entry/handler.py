import logging
import json

from openai import OpenAI
from fastapi import APIRouter, Request
from langchain_core.documents import Document
from helpers.PIIManager.PIIMasking import PIIMaskingManager


from helpers.StoreManager import store_manager
from api.entry.models import MODEL, SYSTEM_MESSAGE_PREFIX, CreateEntry

router = APIRouter()

client = OpenAI()

logger = logging.getLogger(__name__)


@router.post("/create")
async def create_entry(request: Request):
    body_bytes = await request.body()
    body_bytes=body_bytes.replace(b"\r", b"")
    body_bytes=body_bytes.replace(b"\n", b"")
    body_bytes=body_bytes.replace(b"\t", b"")
    print(body_bytes)
    body_bytes_str = body_bytes.decode("utf-8")
    print(body_bytes_str[697-720])
    email_details_dict = json.loads(body_bytes_str)
    email_details = CreateEntry(**email_details_dict)
    logger.info(f"Create entry called\n{email_details_dict}")
    answer, document = get_response_from_ai(email_details=email_details)
    document_dict = document.dict()
    email_details_dict.update(
        {
            "answer": answer,
            "document": document_dict["page_content"],
            "document_title": document_dict["metadata"]["source"],
        }
    )
    store_manager.emails.append(email_details_dict)
    return email_details_dict


def get_response_from_ai(email_details: CreateEntry) -> tuple[str, Document]:
    relevant_documents = store_manager.chroma_database.query(email_details.description)
    first_relevant_document = relevant_documents[0]
    print(email_details.description)
    logger.info(f"All relevant documents\n{first_relevant_document}")

    system_message = SYSTEM_MESSAGE_PREFIX + first_relevant_document.page_content
    pii_manager = PIIMaskingManager()
    question, deanonymizer_mapping = pii_manager.get_anonymized_text(
        email_details.description
    )
    logger.info(f"Question used: {question}")
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question, },
        ],
        model=MODEL,
    )
    masked_answer = response.choices[0].message.content
    answer = pii_manager.get_deanonymized_text(masked_answer, deanonymizer_mapping)
    logger.info(f"Answer from {MODEL}:\n{answer}")
    answer = answer.replace("\n", "<br>")
    return answer, first_relevant_document


@router.get("")
async def get_entries():
    emails = store_manager.emails.copy()
    logger.info(f"Retrieve all emails\n{emails}")
    return {"data": emails}
