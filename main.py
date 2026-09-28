"""FastAPI application entry point."""

from dotenv import load_dotenv
from fastapi import FastAPI

from adjudicate_claim import router as claims_agent_router
from injest_policy import router as inject_policy_router

load_dotenv()

app = FastAPI()
app.include_router(claims_agent_router)
app.include_router(inject_policy_router)

