"""FastAPI application entry point."""

from dotenv import load_dotenv
from fastapi import FastAPI

from src.Util.LoggingConfig import configure_logging
from src.API.AdjudicateClaimService import router as claims_agent_router
from src.API.InjestPolicyService import router as inject_policy_router

load_dotenv()
configure_logging()

app = FastAPI()
app.include_router(claims_agent_router)
app.include_router(inject_policy_router)
