from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.planners import BuiltInPlanner
from google.genai import types as genai_types
from typing import AsyncGenerator
from google.adk.events import Event

from ResearchAgent.config import MODEL_NAME
from ResearchAgent.compliance_agent import compliance_agent
from ResearchAgent.manager_instructions import REQUEST_COORDINATOR_INSTRUCTION
from ResearchAgent.research_agent import research_agent
from ResearchAgent.ideation_agent import ideation_agent
from ResearchAgent.visual_agent import visual_agent

def track_tool_usage_callback(ctx) -> None:
    # We can inspect ctx.session.events or similar to see tool usage, 
    # but the simplest way to force the LLM to route is structured output 
    # or step-by-step thinking in the system prompt.
    pass

from google.adk.tools import FunctionTool
from ResearchAgent.tools import update_brief

request_coordinator_agent = Agent(
    name="GeneralRequestCoordinator",
    model=MODEL_NAME,
    instruction=REQUEST_COORDINATOR_INSTRUCTION,
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    tools=[AgentTool(research_agent), AgentTool(ideation_agent), AgentTool(visual_agent), FunctionTool(update_brief)],
)

compliance_root_agent = SequentialAgent(
    name="ComplianceRootAgent",
    description="Run compliance validation first, then coordinate final response and optional research delegation.",
    sub_agents=[compliance_agent, request_coordinator_agent],
)

general_root_manager = compliance_root_agent
manager_agent = compliance_root_agent
