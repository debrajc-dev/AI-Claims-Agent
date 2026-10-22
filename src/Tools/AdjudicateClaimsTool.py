import os

from langchain_core.tools.convert import tool
from langchain_openai import ChatOpenAI


SYS_PROMPT = (
    "You are a claims tool. "
    "Check the input claim and answer the user's prompt using only the supplied document context. "
    "If the context does not contain the answer, say that clearly instead of guessing. "
    "If the prompt is not about a claim, ask the user to provide a claim to verify. "
    "Provide a concise answer with detailed reasons why the claim is valid or invalid."
)


@tool
def adjudicate_claims_tool(prompt: str, context: str) -> str:
    """Evaluate a claim using policy context already retrieved for the prompt."""
    model = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    response = model.invoke(
        [
            ("system", SYS_PROMPT),
            ("human", f"Document context:\n{context}\n\nUser prompt:\n{prompt}"),
        ]
    )
    return response.content
