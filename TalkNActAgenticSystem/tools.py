import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from google.adk.tools import ToolContext

from ResearchAgent.tools import rag_over_uploaded_doc


SESSION_CONTEXT_KEY = "session_context"
REQUIRED_BRIEF_FIELDS = ["objective", "audience", "tone"]
PROHIBITED_PATTERNS = [
    r"\bpassword\b",
    r"\bapi[_\s-]?key\b",
    r"\bssn\b",
    r"\bcredit\s*card\b",
    r"\bhate\b",
    r"\bviolence\b",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_session_context() -> Dict[str, Any]:
    return {
        "session_id": str(uuid.uuid4()),
        "status": "BRIEFING",
        "brief": {
            "objective": "",
            "audience": "",
            "tone": "",
            "constraints": [],
            "locked": False,
        },
        "generation_state": {
            "research_insights": [],
            "artifacts": {
                "text_concepts": [],
                "visual_assets": [],
            },
            "quality_feedback": {},
            "conversation_history": [],
        },
    }


def _get_session_context(tool_context: Optional[ToolContext]) -> Dict[str, Any]:
    if not tool_context:
        return _default_session_context()

    context = tool_context.state.get(SESSION_CONTEXT_KEY)
    if isinstance(context, dict):
        return context

    context = _default_session_context()
    tool_context.state[SESSION_CONTEXT_KEY] = context
    return context


def _save_session_context(tool_context: Optional[ToolContext], session_context: Dict[str, Any]) -> None:
    if tool_context:
        tool_context.state[SESSION_CONTEXT_KEY] = session_context


def _get_brief_missing_fields(brief: Dict[str, Any]) -> List[str]:
    missing = []
    for field in REQUIRED_BRIEF_FIELDS:
        value = str(brief.get(field, "")).strip()
        if not value:
            missing.append(field)
    return missing


def _append_history(session_context: Dict[str, Any], event: str, payload: Dict[str, Any]) -> None:
    history = session_context["generation_state"].get("conversation_history", [])
    history.append({"ts": _utc_now(), "event": event, "payload": payload})
    session_context["generation_state"]["conversation_history"] = history[-60:]


def _model_name() -> str:
    return os.environ.get("GOOGLE_GENAI_MODEL", "gemini-2.5-flash-lite")


def _call_llm(prompt: str) -> str:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "LLM unavailable: GOOGLE_API_KEY not set."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(_model_name())
    response = model.generate_content(prompt)
    return (getattr(response, "text", None) or "").strip() or "No content generated."


def initialize_session_context(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    context = _get_session_context(tool_context)
    _save_session_context(tool_context, context)
    return {"session_context": context}


def get_session_context(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    return {"session_context": _get_session_context(tool_context)}


def get_brief_gaps(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    context = _get_session_context(tool_context)
    brief = context.get("brief", {})
    missing = _get_brief_missing_fields(brief)
    return {
        "brief": brief,
        "missing_fields": missing,
        "ready_to_lock": len(missing) == 0,
        "status": context.get("status", "BRIEFING"),
    }


def reset_session_context(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    context = _default_session_context()
    _append_history(context, "context_reset", {"reason": "new_direction"})
    _save_session_context(tool_context, context)
    return {"message": "Session context reset.", "session_context": context}


def safety_input_audit(user_text: str, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    context = _get_session_context(tool_context)
    lowered = (user_text or "").lower()
    for pattern in PROHIBITED_PATTERNS:
        if re.search(pattern, lowered):
            result = {"status": "BLOCK", "reason": f"Matched policy pattern: {pattern}"}
            _append_history(context, "safety_input_block", result)
            _save_session_context(tool_context, context)
            return result

    result = {"status": "PASS", "reason": "No blocked patterns detected."}
    _append_history(context, "safety_input_pass", {"chars": len(user_text or "")})
    _save_session_context(tool_context, context)
    return result


def safety_output_audit(candidate_output: str, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    context = _get_session_context(tool_context)
    lowered = (candidate_output or "").lower()
    for pattern in PROHIBITED_PATTERNS:
        if re.search(pattern, lowered):
            result = {"status": "BLOCK", "reason": f"Output matched policy pattern: {pattern}"}
            _append_history(context, "safety_output_block", result)
            _save_session_context(tool_context, context)
            return result

    result = {"status": "PASS", "reason": "Output cleared boundary safety check."}
    _append_history(context, "safety_output_pass", {"chars": len(candidate_output or "")})
    _save_session_context(tool_context, context)
    return result


def update_brief(
    objective: Optional[str] = None,
    audience: Optional[str] = None,
    tone: Optional[str] = None,
    constraints: Optional[List[str]] = None,
    lock_brief: bool = False,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    context = _get_session_context(tool_context)
    brief = context["brief"]

    if objective is not None:
        brief["objective"] = objective.strip()
    if audience is not None:
        brief["audience"] = audience.strip()
    if tone is not None:
        brief["tone"] = tone.strip()
    if constraints is not None:
        brief["constraints"] = [item.strip() for item in constraints if str(item).strip()]

    if lock_brief:
        missing = _get_brief_missing_fields(brief)
        if missing:
            brief["locked"] = False
            context["status"] = "BRIEFING"
            _append_history(
                context,
                "brief_lock_rejected",
                {"missing_fields": missing},
            )
            _save_session_context(tool_context, context)
            return {
                "error": "Brief lock rejected. Missing required fields.",
                "missing_fields": missing,
                "brief": brief,
                "status": context["status"],
            }

        brief["locked"] = True
        context["status"] = "EXECUTION"

    _append_history(context, "brief_updated", {"locked": brief.get("locked", False)})
    _save_session_context(tool_context, context)
    return {"brief": brief, "status": context["status"]}


def research_unit(
    query: Optional[str] = None,
    use_rag: bool = True,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    context = _get_session_context(tool_context)
    brief = context["brief"]

    effective_query = query or (
        f"Objective: {brief.get('objective')}; Audience: {brief.get('audience')}; Tone: {brief.get('tone')}"
    )

    insights: List[Dict[str, Any]] = []
    if use_rag:
        rag_result = rag_over_uploaded_doc(query=effective_query)
        if "error" not in rag_result:
            for match in rag_result.get("matches", [])[:5]:
                insights.append(
                    {
                        "source": "rag",
                        "citation": match.get("citation_id"),
                        "text": match.get("text"),
                    }
                )

    if not insights:
        prompt = (
            "Generate concise market research insights for this campaign brief.\n"
            f"Query: {effective_query}\n"
            "Return 5 bullet points."
        )
        llm_text = _call_llm(prompt)
        for line in llm_text.splitlines():
            cleaned = line.strip("-• \t")
            if cleaned:
                insights.append({"source": "llm", "citation": "UNVERIFIED", "text": cleaned})

    context["generation_state"]["research_insights"] = insights[:8]
    _append_history(context, "research_updated", {"insights": len(insights)})
    _save_session_context(tool_context, context)
    return {"research_insights": context["generation_state"]["research_insights"]}


def ideation_unit(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    context = _get_session_context(tool_context)
    brief = context["brief"]
    insights = context["generation_state"].get("research_insights", [])

    prompt = (
        "You are IDEA-01 (Creative Copywriter).\n"
        f"Objective: {brief.get('objective')}\n"
        f"Audience: {brief.get('audience')}\n"
        f"Tone: {brief.get('tone')}\n"
        f"Constraints: {brief.get('constraints')}\n"
        f"Research: {insights}\n"
        "Create 5 concept lines with tagline + supporting claim."
    )
    llm_text = _call_llm(prompt)

    concepts = [line.strip() for line in llm_text.splitlines() if line.strip()][:8]
    context["generation_state"]["artifacts"]["text_concepts"] = concepts
    _append_history(context, "ideation_generated", {"count": len(concepts)})
    _save_session_context(tool_context, context)
    return {"text_concepts": concepts}


def visual_unit(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    context = _get_session_context(tool_context)
    brief = context["brief"]
    concepts = context["generation_state"]["artifacts"].get("text_concepts", [])

    prompt = (
        "You are VIS-01 (Art Director).\n"
        f"Objective: {brief.get('objective')}\n"
        f"Audience: {brief.get('audience')}\n"
        f"Tone: {brief.get('tone')}\n"
        f"Constraints: {brief.get('constraints')}\n"
        f"Text concepts: {concepts}\n"
        "Create 4 visual prompts for moodboard/product render generation."
    )
    llm_text = _call_llm(prompt)

    visuals = [line.strip() for line in llm_text.splitlines() if line.strip()][:8]
    context["generation_state"]["artifacts"]["visual_assets"] = visuals
    _append_history(context, "visual_generated", {"count": len(visuals)})
    _save_session_context(tool_context, context)
    return {"visual_assets": visuals}


def execute_parallel_generation(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    context = _get_session_context(tool_context)
    if not context["brief"].get("locked"):
        return {"error": "Brief is not locked. Complete briefing and lock brief first."}

    context["status"] = "EXECUTION"
    _save_session_context(tool_context, context)

    with ThreadPoolExecutor(max_workers=2) as executor:
        ideation_future = executor.submit(ideation_unit, tool_context)
        visual_future = executor.submit(visual_unit, tool_context)
        ideation_result = ideation_future.result()
        visual_result = visual_future.result()

    context = _get_session_context(tool_context)
    _append_history(context, "parallel_execution_complete", {"ok": True})
    _save_session_context(tool_context, context)

    return {
        "status": context["status"],
        "ideation": ideation_result,
        "visual": visual_result,
    }


def quality_unit(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    context = _get_session_context(tool_context)
    brief = context["brief"]
    artifacts = context["generation_state"].get("artifacts", {})

    text_concepts = artifacts.get("text_concepts", [])
    visual_assets = artifacts.get("visual_assets", [])

    score = 50
    fixes: List[str] = []

    if text_concepts:
        score += 20
    else:
        fixes.append("Generate stronger text concepts.")

    if visual_assets:
        score += 20
    else:
        fixes.append("Generate visual assets aligned to the concepts.")

    objective = (brief.get("objective") or "").strip().lower()
    if objective and not any(objective.split()[0] in item.lower() for item in text_concepts[:3]):
        score -= 10
        fixes.append("Make concepts align more directly with campaign objective.")

    if any("no red" in str(constraint).lower() for constraint in brief.get("constraints", [])):
        red_hits = [item for item in visual_assets if "red" in item.lower()]
        if red_hits:
            score -= 10
            fixes.append("Re-roll visuals to avoid red tones as requested.")

    score = max(0, min(100, score))
    quality_result = {"score": score, "fix_requests": fixes}

    context["generation_state"]["quality_feedback"] = quality_result
    context["status"] = "REVIEW"
    _append_history(context, "quality_evaluated", quality_result)
    _save_session_context(tool_context, context)

    return quality_result


def refine_visual_only(
    additional_constraints: List[str],
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    context = _get_session_context(tool_context)
    brief = context["brief"]

    merged_constraints = list(brief.get("constraints", [])) + [
        item for item in additional_constraints if item and item not in brief.get("constraints", [])
    ]
    brief["constraints"] = merged_constraints

    visual_result = visual_unit(tool_context)
    quality_result = quality_unit(tool_context)

    _append_history(
        context,
        "refine_visual_only",
        {"constraints": additional_constraints, "quality_score": quality_result.get("score")},
    )
    _save_session_context(tool_context, context)

    return {
        "message": "Applied visual-only refinement using continuity logic.",
        "brief": brief,
        "visual": visual_result,
        "quality": quality_result,
    }
