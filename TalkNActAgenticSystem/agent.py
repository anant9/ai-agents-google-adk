import os
import re
import copy
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.genai import types

from TalkNActAgenticSystem.instructions import MANAGER_INSTRUCTION
from TalkNActAgenticSystem.tools import (
    execute_parallel_generation,
    get_brief_gaps,
    get_session_context,
    ideation_unit,
    initialize_session_context,
    quality_unit,
    refine_visual_only,
    research_unit,
    reset_session_context,
    safety_input_audit,
    safety_output_audit,
    update_brief,
    visual_unit,
)


try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

MODEL_NAME = os.environ.get("GOOGLE_GENAI_MODEL", "gemini-2.5-flash-lite")
INPUT_BLOCK_PATTERNS = [
    r"\bpassword\b",
    r"\bapi[_\s-]?key\b",
    r"\bssn\b",
    r"\bcredit\s*card\b",
]


def before_manager_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    if "session_context" not in callback_context.state:
        callback_context.state["session_context"] = initialize_session_context().get(
            "session_context", {}
        )
    return None


def before_manager_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    if not llm_request.contents:
        return None

    last_user_idx = -1
    for idx in range(len(llm_request.contents) - 1, -1, -1):
        if llm_request.contents[idx].role == "user":
            last_user_idx = idx
            break

    if last_user_idx == -1 or not llm_request.contents[last_user_idx].parts:
        return None

    user_text = llm_request.contents[last_user_idx].parts[0].text or ""
    lowered = user_text.lower()

    for pattern in INPUT_BLOCK_PATTERNS:
        if re.search(pattern, lowered):
            callback_context.state["input_safety_blocked"] = True
            llm_request.contents[last_user_idx].parts[0].text = (
                "The previous user input contains restricted sensitive content. "
                "Do not process the request. Reply with a concise safety refusal and ask for a safe reformulation."
            )
            return None

    session_context = callback_context.state.get("session_context", {})
    brief = session_context.get("brief", {}) if isinstance(session_context, dict) else {}
    missing_fields = [
        field
        for field in ("objective", "audience", "tone")
        if not str(brief.get(field, "")).strip()
    ]

    if missing_fields:
        llm_request.contents[last_user_idx].parts[0].text = (
            f"{user_text}\n\n"
            "Instruction override: Brief is incomplete. "
            f"Missing fields: {', '.join(missing_fields)}. "
            "Ask for ALL missing fields together in one concise follow-up message so the user can provide them in a single reply. "
            "Do not start generation and do not lock brief in this turn."
        )

    return None


def after_manager_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    session_context = callback_context.state.get("session_context", {})
    if not isinstance(session_context, dict):
        return llm_response

    brief = session_context.get("brief", {})
    missing_fields = [
        field
        for field in ("objective", "audience", "tone")
        if not str(brief.get(field, "")).strip()
    ]

    if not missing_fields:
        return llm_response

    if not llm_response.content or not llm_response.content.parts:
        modified = copy.deepcopy(llm_response)
        question = (
            "Before I generate, I still need these brief details: "
            f"{', '.join(missing_fields)}. "
            "Please share all of them in one message."
        )
        modified.content = types.Content(role="model", parts=[types.Part(text=question)])
        return modified

    current_text = llm_response.content.parts[0].text or ""
    contains_any_field = any(field in current_text.lower() for field in missing_fields)
    if ("?" not in current_text) and not contains_any_field:
        modified = copy.deepcopy(llm_response)
        question = (
            "Before I generate, I still need these brief details: "
            f"{', '.join(missing_fields)}. "
            "Please share all of them in one message."
        )
        modified.content.parts[0].text = question
        return modified

    return llm_response


manager_tools = [
    FunctionTool(safety_input_audit),
    FunctionTool(safety_output_audit),
    FunctionTool(get_session_context),
    FunctionTool(get_brief_gaps),
    FunctionTool(reset_session_context),
    FunctionTool(update_brief),
    FunctionTool(research_unit),
    FunctionTool(ideation_unit),
    FunctionTool(visual_unit),
    FunctionTool(execute_parallel_generation),
    FunctionTool(quality_unit),
    FunctionTool(refine_visual_only),
    GoogleSearchTool(bypass_multi_tools_limit=True),
]


manager_agent = LlmAgent(
    name="ManagerAgent_MGR01",
    model=MODEL_NAME,
    instruction=MANAGER_INSTRUCTION,
    tools=manager_tools,
    before_agent_callback=before_manager_callback,
    before_model_callback=before_manager_model_callback,
    after_model_callback=after_manager_model_callback,
    output_key="manager_output",
)


root_agent = manager_agent
