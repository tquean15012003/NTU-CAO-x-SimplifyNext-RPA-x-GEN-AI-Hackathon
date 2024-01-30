import logging
from openai import OpenAI

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from model.RequestBodyModels import CreateEntry

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

emails = []

SAMPLE_DOCUMENT = """TITLE: "CSC Graduation Requirements
Description: Student needs to have at least 135 AUs to graduate"
"""

SYSTEM_MESSAGE = (
    """You are an email assistant. You are about to receive an email body and reply to it. You have to use the following information to generate an appropriate reply\n"""
    + SAMPLE_DOCUMENT
)

client = OpenAI()

@app.post("/create")
async def create_entry(email_details: CreateEntry):
    print(email_details)
    email_details_dict = email_details.model_dump()
    answer = get_response_from_ai(email_details=email_details)
    email_details_dict.update({"answer": answer, "document": SAMPLE_DOCUMENT})
    emails.append(email_details_dict)
    return {"status": "success"}


def get_response_from_ai(email_details: CreateEntry):
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": email_details.description},
        ],
        model="gpt-3.5-turbo",
    )
    print(response)
    return response.choices[0].message.content


@app.get("/")
async def get_entries():
    return {"data": emails}
