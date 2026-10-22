"""Document-grounded question-answering endpoint."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.Agents.ClaimAgent import call_agent


router = APIRouter()

class AskRequest(BaseModel):
    """Input accepted by the document-grounded question-answering endpoint."""

    prompt: str = Field(..., min_length=1, description="Question to answer from the ingested documents")


@router.post("/VerifyClaim")
def ask(request: AskRequest):
    """Use the claims agent to answer a prompt from retrieved policy context."""
    try:
        answer, sources = call_agent(request.prompt)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail="The claim adjudication service failed.") from exc

    return {
        "answer": answer,
        "sources": sources,
    }
