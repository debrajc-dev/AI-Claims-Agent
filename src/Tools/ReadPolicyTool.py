import logging
import os

from fastapi import HTTPException
from langchain_community.vectorstores import Chroma
from langchain_core.tools.convert import tool
from langchain_openai import OpenAIEmbeddings

from src.API.InjestPolicyService import CHROMA_DIRECTORY


logger = logging.getLogger(__name__)


@tool(response_format="content_and_artifact")
def read_policy_tool(prompt: str) -> tuple[str, list[dict]]:
    """Retrieve policy context and source metadata for a claim prompt."""
    if not os.path.isdir(CHROMA_DIRECTORY):
        raise HTTPException(status_code=404, detail="Chroma database not found. Run /SetupPolicy first.")

    try:
        embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info(CHROMA_DIRECTORY)
        vector_store = Chroma(
            persist_directory=CHROMA_DIRECTORY,
            embedding_function=embeddings,
        )
        documents = vector_store.similarity_search(prompt, k=5)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to retrieve policy context: {exc}") from exc

    if not documents:
        raise HTTPException(status_code=404, detail="No policy context found. Run /SetupPolicy first.")

    context = "\n\n---\n\n".join(document.page_content for document in documents)
    sources = [document.metadata for document in documents]
    source_ids = [
        {
            "source": os.path.basename(str(source["source"])) if source.get("source") else None,
            "page": source.get("page"),
        }
        for source in sources
    ]
    logger.info(
        "Retrieved policy context: characters=%d, source_count=%d, sources=%s",
        len(context),
        len(sources),
        source_ids,
    )
    return context, sources
