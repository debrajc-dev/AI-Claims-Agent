"""Document-grounded question-answering endpoint."""

import os

from fastapi import APIRouter, HTTPException
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from pydantic import BaseModel, Field

from injest_policy import CHROMA_DIRECTORY


router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class AskRequest(BaseModel):
    """Input accepted by the document-grounded question-answering endpoint."""

    prompt: str = Field(..., min_length=1, description="Question to answer from the ingested documents")


@router.post("/VerifyClaim")
def ask(request: AskRequest):
    """Retrieve relevant document chunks and use them to answer a user prompt."""
    if not os.path.isdir(CHROMA_DIRECTORY):
        raise HTTPException(status_code=404, detail="Chroma database not found. Run /ingest first.")

    try:
        embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
        vector_store = Chroma(
            persist_directory=CHROMA_DIRECTORY,
            embedding_function=embeddings,
        )
        documents = vector_store.similarity_search(request.prompt, k=5)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to retrieve context: {exc}") from exc

    if not documents:
        raise HTTPException(status_code=404, detail="No document context found. Run /ingest first.")

    context = "\n\n---\n\n".join(document.page_content for document in documents)
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=(
            "You are a claims agent "
            "Check the input claim and nswer the user's prompt using only the supplied document context. "
            "If the context does not contain the answer, say that clearly instead of guessing." \
            "If the prompt is not about a claim, say please provide a claim to verify. "
            "Provide your answer in a concise and clear manner. " \
            "Given detailed reason why the claim is valid or invalid. " \
        ),
        input=f"Document context:\n{context}\n\nUser prompt:\n{request.prompt}",
    )

    return {
        "prompt": request.prompt,
        "answer": response.output_text,
        "sources": [document.metadata for document in documents],
    }