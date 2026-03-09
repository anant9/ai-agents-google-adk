import uuid

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from TalkNActAgenticSystem.agent import root_agent


APP_NAME = "TalkNActAgenticSystem"
USER_ID = "demo-user"


def _run_message(runner: Runner, session_id: str, text: str) -> str:
    content = types.Content(role="user", parts=[types.Part(text=text)])
    final_text = ""
    for event in runner.run(user_id=USER_ID, session_id=session_id, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text or ""
    return final_text


def main() -> None:
    session_service = InMemorySessionService()
    session_id = str(uuid.uuid4())
    session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
        state={},
    )

    runner = Runner(agent=root_agent, session_service=session_service, app_name=APP_NAME)

    prompts = [
        "I need campaign concepts for a new soda product.",
        "Audience is Gen Z, tone is playful, constraints are no red and no sugar claims beyond facts.",
        "Lock brief, run generation, run quality check, and show me the result.",
    ]

    for prompt in prompts:
        print(f"\nUSER: {prompt}")
        response = _run_message(runner, session_id, prompt)
        print(f"ASSISTANT:\n{response}")

    session = session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    print("\nFinal session_context keys:", list(session.state.keys()))


if __name__ == "__main__":
    main()
