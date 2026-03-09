# TalkNActAgenticSystem

Implementation based on `ResearchAgent/ARCHandDESIGN/agent_design.md` and `architecture.md`.

## Implemented units
- `ManagerAgent_MGR01` (workflow lead + context owner)
- `research_unit` (RES-01)
- `ideation_unit` (IDEA-01)
- `visual_unit` (VIS-01)
- `safety_input_audit` / `safety_output_audit` (SAFE-01 boundary guard)
- `quality_unit` (QUAL-01)

## Session context
Single source of truth in `state["session_context"]`:
- `status`: `BRIEFING | EXECUTION | REVIEW`
- `brief`: objective/audience/tone/constraints/locked
- `generation_state`: research insights, artifacts, quality feedback, history

## Flow mapping
- **Flow A (Briefing Loop)**: use `update_brief(..., lock_brief=True)`
- **Flow B (Execution Parallel)**: use `execute_parallel_generation()` then `quality_unit()`
- **Flow C (Refinement)**: use `refine_visual_only(additional_constraints=[...])`

## Enforced behaviors
- Brief lock is rejected unless all required fields are present: `objective`, `audience`, `tone`.
- Manager asks for all missing brief fields together during BRIEFING.
- Pre-model input gating blocks/redirects sensitive unsafe input before generation.
- Use `get_brief_gaps` in chat to inspect what is still missing.

## Usage in ADK UI
Set app to `TalkNActAgenticSystem` and prompt the manager naturally.

Example prompt sequence:
1. "I need launch concepts for a new zero sugar soda"
2. "Audience is Gen Z, tone playful, constraint no red"
3. "Lock brief and generate"
4. "Refine visuals: avoid metallic backgrounds"

## Notes
- `research_unit` attempts document RAG via `ResearchAgent.tools.rag_over_uploaded_doc`.
- `GoogleSearchTool` is exposed to manager for web grounding when needed.
