from typing import Any, Dict, Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# IMPORTANT: ResearchAgent must NEVER send responses directly to the end user.
# All responses must be routed to request_coordinator_agent, which in turn sends them to compliance/rootagent for validation before reaching the user.

from ResearchAgent.config import (
    ENABLE_RAG_RESEARCH,
    ENABLE_WEB_RESEARCH,
    MODEL_NAME,
)
from ResearchAgent.instructions import RESEARCH_AGENT_INSTRUCTION
from ResearchAgent.tools import rag_over_uploaded_doc


_RAG_GATE_LAST_USER_TEXT_KEY = "research_rag_gate_last_user_text"
_RAG_GATE_CHECKED_KEY = "research_rag_checked_this_turn"
_RUNTIME_MODE_STATE_KEY = "research_runtime_mode"
_WEB_CALLED_KEY = "research_web_called_this_turn"
_CURRENT_USER_TEXT_KEY = "research_current_user_text"
_RAG_DONE_FOR_USER_TEXT_KEY = "research_rag_done_for_user_text"
_WEB_DONE_FOR_USER_TEXT_KEY = "research_web_done_for_user_text"


def _set_runtime_mode(callback_context: CallbackContext, mode: str) -> None:
    callback_context.state[_RUNTIME_MODE_STATE_KEY] = mode


def before_agent_callback_rag_gate(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    callback_context.state[_RAG_GATE_CHECKED_KEY] = False
    callback_context.state[_WEB_CALLED_KEY] = False
    return None


def _latest_user_text(llm_request: LlmRequest) -> str:
    if not llm_request.contents:
        return ""
    for content in reversed(llm_request.contents):
        if getattr(content, "role", "") != "user":
            continue
        parts = getattr(content, "parts", []) or []
        if not parts:
            return ""
        return str(getattr(parts[0], "text", "") or "").strip()
    return ""


def before_model_callback_rag_gate(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    _set_runtime_mode(callback_context, "RAG_AND_WEB")

    latest_user_text = _latest_user_text(llm_request)
    callback_context.state[_CURRENT_USER_TEXT_KEY] = latest_user_text
    previous_user_text = str(
        callback_context.state.get(_RAG_GATE_LAST_USER_TEXT_KEY, "") or ""
    )

    if latest_user_text != previous_user_text:
        callback_context.state[_RAG_GATE_LAST_USER_TEXT_KEY] = latest_user_text
        callback_context.state[_RAG_GATE_CHECKED_KEY] = False
        callback_context.state[_WEB_CALLED_KEY] = False
        callback_context.state[_RAG_DONE_FOR_USER_TEXT_KEY] = ""
        callback_context.state[_WEB_DONE_FOR_USER_TEXT_KEY] = ""

    return None


def before_tool_callback_rag_first(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
    tool_name = str(getattr(tool, "name", "") or "")
    lowered_tool_name = tool_name.lower()
    current_user_text = str(tool_context.state.get(_CURRENT_USER_TEXT_KEY, "") or "")
    rag_done_for_text = str(tool_context.state.get(_RAG_DONE_FOR_USER_TEXT_KEY, "") or "")
    web_done_for_text = str(tool_context.state.get(_WEB_DONE_FOR_USER_TEXT_KEY, "") or "")

    if tool_name == "rag_over_uploaded_doc":
        if web_done_for_text and web_done_for_text == current_user_text:
            return {
                "result": (
                    "RAG_AFTER_WEB_BLOCKED: rag_over_uploaded_doc cannot be called after "
                    "google_search in the same user request. Use the existing doc evidence "
                    "and synthesize with web results."
                )
            }
        tool_context.state[_RAG_GATE_CHECKED_KEY] = True
        tool_context.state[_RAG_DONE_FOR_USER_TEXT_KEY] = current_user_text
        return None

    if "google_search" in lowered_tool_name:
        rag_checked_for_current_text = bool(
            rag_done_for_text and rag_done_for_text == current_user_text
        )
        if not rag_checked_for_current_text:
            return {
                "result": (
                    "RAG_FIRST_REQUIRED: Call rag_over_uploaded_doc before google_search "
                    "for this user request."
                )
            }
        tool_context.state[_WEB_CALLED_KEY] = True
        tool_context.state[_WEB_DONE_FOR_USER_TEXT_KEY] = current_user_text

    return None


def before_model_callback_rag_only(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    _set_runtime_mode(callback_context, "RAG_ONLY")
    return None


def before_model_callback_web_only(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    _set_runtime_mode(callback_context, "WEB_ONLY")
    return None


def before_model_callback_no_tools(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    _set_runtime_mode(callback_context, "TOOLS_DISABLED")
    return None


if ENABLE_RAG_RESEARCH and ENABLE_WEB_RESEARCH:
    google_search_tool = GoogleSearchTool(bypass_multi_tools_limit=True)
    research_agent = LlmAgent(
        name="ResearchAgent",
        model=MODEL_NAME,
        instruction=RESEARCH_AGENT_INSTRUCTION,
        tools=[rag_over_uploaded_doc, google_search_tool],
        output_key="research_response",
        before_agent_callback=before_agent_callback_rag_gate,
        before_model_callback=before_model_callback_rag_gate,
        before_tool_callback=before_tool_callback_rag_first,
    )

elif ENABLE_RAG_RESEARCH and not ENABLE_WEB_RESEARCH:
    research_agent = LlmAgent(
        name="ResearchAgent",
        model=MODEL_NAME,
        instruction=(
            "You are a research assistant in RAG-only mode. "
            "Use rag_over_uploaded_doc for all evidence and do not use web sources. "
            "If the requested fact is not present in the document/reference docs, clearly say so."
        ),
        tools=[rag_over_uploaded_doc],
        output_key="research_response",
        before_model_callback=before_model_callback_rag_only,
    )

elif ENABLE_WEB_RESEARCH and not ENABLE_RAG_RESEARCH:
    google_search_tool = GoogleSearchTool(bypass_multi_tools_limit=True)
    research_agent = LlmAgent(
        name="ResearchAgent",
        model=MODEL_NAME,
        instruction=(
            "You are a research assistant in web-only mode. "
            "Use google_search for evidence and provide citations with URLs."
        ),
        tools=[google_search_tool],
        output_key="research_response",
        before_model_callback=before_model_callback_web_only,
    )

else:
    research_agent = LlmAgent(
        name="ResearchAgent",
        model=MODEL_NAME,
        instruction=(
            "Research tools are disabled by configuration. "
            "Inform the user that ENABLE_WEB_RESEARCH and ENABLE_RAG_RESEARCH are both disabled "
            "and ask them to enable at least one mode."
        ),
        tools=[],
        output_key="research_response",
        before_model_callback=before_model_callback_no_tools,
    )
