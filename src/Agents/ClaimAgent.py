from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from src.Tools.AdjudicateClaimsTool import adjudicate_claims_tool
from src.Tools.ReadPolicyTool import read_policy_tool


SYS_PROMPT = (
	"You are a claims agent. You must use the tools in this exact order for every claim question: "
	"first call read_policy_tool with the user's original prompt; after it returns, call "
	"adjudicate_claims_tool with the same original prompt and the complete policy context returned "
	"by read_policy_tool as the context argument. Never call adjudicate_claims_tool before "
	"read_policy_tool, never skip either tool, and do not answer the user until adjudication is complete. "
	"Use only the supplied policy context and do not add unsupported claims."
)


def call_agent(prompt: str) -> tuple[str, list[dict]]:
	agent = create_agent(
		model=ChatOpenAI(model="gpt-4o-mini"),
		tools=[read_policy_tool, adjudicate_claims_tool],
		system_prompt=SYS_PROMPT,
	)
	result = agent.invoke(
		{
			"messages": [
				{
					"role": "user",
					"content": prompt,
				}
			]
		}
	)
	source_messages = [
		message
		for message in result["messages"]
		if getattr(message, "artifact", None) is not None
	]
	sources = source_messages[-1].artifact if source_messages else []
	return result["messages"][-1].content, sources
