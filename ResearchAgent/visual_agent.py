from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from ResearchAgent.config import MODEL_NAME
from ResearchAgent.tools import generate_concept_images, update_generation_state
from ResearchAgent.visual_instructions import VISUAL_AGENT_INSTRUCTION

visual_agent = LlmAgent(
    name="VisualAgent",
    model=MODEL_NAME,
    instruction=VISUAL_AGENT_INSTRUCTION,
    tools=[FunctionTool(generate_concept_images), FunctionTool(update_generation_state)],
    output_key="visual_assets",
)
