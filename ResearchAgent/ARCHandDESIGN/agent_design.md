# Agent Design Specifications: TalkNact Concept Generator

## 1. Agent List

1.  **Manager Agent (MGR-01)** (Formerly Orchestrator)
2.  **Research Unit (RES-01)**
3.  **Ideation Unit (IDEA-01)**
4.  **Visual Unit (VIS-01)**
5.  **Safety Unit (SAFE-01)** (Formerly Compliance)
6.  **Quality Unit (QUAL-01)**

---

## 2. Agent Specifications

### Manager Agent (MGR-01)
*   **Role**: Project Lead & Workflow Router.
*   **Responsibilities**:
    *   **Briefing Mode:** Chat with the user to clarify requirements *before* starting work.
    *   **Task Router:** Dynamically assign work to Research, Ideation, or Visual units based on the locked brief.
    *   **Context Owner:** Maintain the "Single Source of Truth" session state.
    *   **Reviewer:** Aggregate outputs and decide if they meet the brief (Continuity Logic).
*   **Input:** User Chat, Session State.
*   **Output:** Next State (Briefing / Execution / Presentation).

### Research Unit (RES-01)
*   **Role**: Information Gatherer.
*   **Responsibilities**:
    *   Find facts to support the brief (from Docs or Web).
    *   Update `SessionContext.research_insights` for other units to read.
*   **Input:** Search Queries.
*   **Output:** Research Context Updates (No direct output to user).

### Ideation Unit (IDEA-01)
*   **Role**: Creative Copywriter.
*   **Responsibilities**:
    *   Generate text concepts, taglines, and claims.
    *   Read `brief` and `research_insights` from Session Context.
*   **Input:** Briefing Instructions.
*   **Output:** Draft Concepts (Text).

### Visual Unit (VIS-01)
*   **Role**: Art Director.
*   **Responsibilities**:
    *   Create visual assets (Moodboards, Product Renders) matching the text concepts.
    *   Execute in parallel with Ideation where possible.
*   **Input:** Visual Brief.
*   **Output:** Image Assets.

### Safety Unit (SAFE-01)
*   **Role**: Gatekeeper.
*   **Responsibilities**:
    *   **Input Audit:** Check User Chat for policy violations (PII, Abuse) *before* the Manager processes it.
    *   **Output Audit:** Check final Paired Stimulus *before* the Manager shows it to the user.
    *   *Note: Does not check every internal step to save costs.*
*   **Input:** Raw Text/Image.
*   **Output:** Pass / Block.

### Quality Unit (QUAL-01)
*   **Role**: Critic.
*   **Responsibilities**:
    *   Evaluate if the generated output actually meets the Brief's `objective`.
    *   Provide specific "Fix Requests" if quality is low (e.g., "Too boring", "Wrong color").
*   **Input:** Final Draft.
*   **Output:** Score + Feedback.

---

## 3. Interaction Flows

### Flow A: Briefing Loop (Chat)
1.  **User**: "Help me."
2.  **Manager**: "What do you need?"
3.  **User**: "Ideas for X."
4.  **Manager**: "Who is the audience?"
5.  **User**: "Teens."
6.  **Manager**: "OK. Locking Brief." -> **Transitions to Flow B**.

### Flow B: Execution (Parallel)
1.  **Manager** reads Locked Brief.
2.  **Manager** triggers **Ideation** and **Visual** (Parallel).
3.  **Ideation** writes Text to Context.
4.  **Visual** writes Images to Context.
5.  **Manager** waits for both.
6.  **Manager** assembles Final Paired Stimulus.
7.  **Manager** calls **Safety Unit**.
    *   [Pass] -> Show to User.
    *   [Fail] -> Apologize and Retry.

### Flow C: Refinement (Continuity)
1.  **User**: "I don't like the red color."
2.  **Manager** (Reviewer Mode):
    *   Updates `Brief.constraints` (Add "No Red").
    *   Calls **Visual Unit** (Re-roll).
    *   Keeps **Ideation** output (Reuse).
3.  **Manager** presents V2.
