import os
import uuid

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from ResearchAgent.agent import root_agent


APP_NAME = "ResearchAgentDemo"
USER_ID = "demo-user"


def _build_initial_state() -> dict:
    reference_doc_path = os.environ.get("DEMO_REFERENCE_DOC_PATH")
    context = {
        "citation_style": "inline",
        "prefer_web": True,
        "prefer_rag": True,
    }

    if reference_doc_path:
        context["reference_doc_path"] = os.path.abspath(reference_doc_path)

    return {
        "status": "BRIEFING",
        "brief": {"objective": "", "constraints": [], "locked": False},
        "generation_state": {
            "artifacts": {"text_concepts": [], "visual_assets": []},
            "conversation_history": []
        },
        "research_context": context
    }


def _run_prompt(runner: Runner, session_id: str, prompt: str) -> str:
    user_query = types.Content(role="user", parts=[types.Part(text=prompt)])
    final_text = ""

    for event in runner.run(
        user_id=USER_ID,
        session_id=session_id,
        new_message=user_query,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text or ""

    return final_text


import asyncio

async def main() -> None:
    session_service = InMemorySessionService()
    session_id = str(uuid.uuid4())

    initial_state = _build_initial_state()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
        state=initial_state,
    )

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=APP_NAME,
    )


    print(f"Session created: {session_id}")
    print("Initial research_context:", initial_state.get("research_context", {}))

    # Greeting message with system capabilities
    print("\nHi there! I am your Marketing Research Agent. Here’s what I can help you with:")
    print("- Generate marketing campaign ideas and strategies")
    print("- Research and analyze competitors or market trends")
    print("- Create brand messaging and content suggestions")
    print("- Assist with compliance and brand guidelines")
    print("- Visualize campaign concepts and creative briefs")
    print("- And much more!\nHow can I assist you today?\n")

    prompt = (
        "I need a visual concept and marketing tagline for a new energy drink called 'Volt'. "
        "The target audience is gamers, and it should feel electric and high-tech. Please lock the brief "
        "to proceed."
    )

    final_response = _run_prompt(runner, session_id, prompt)
    print("\nFinal response:\n")
    print(final_response)

    updated_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )
    updated_state = updated_session.state

    print("\nUpdated session state:\n")
    print(updated_state)


if __name__ == "__main__":
    asyncio.run(main())
