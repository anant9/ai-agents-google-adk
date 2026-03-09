from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from ResearchAgent.config import MODEL_NAME
from ResearchAgent.ideation_instructions import IDEATION_AGENT_INSTRUCTION
from ResearchAgent.tools import update_generation_state

ideation_agent = LlmAgent(
    name="IdeationAgent",
    model=MODEL_NAME,
    instruction=IDEATION_AGENT_INSTRUCTION,
    tools=[FunctionTool(update_generation_state)],
    output_key="ideation_concepts",
)
