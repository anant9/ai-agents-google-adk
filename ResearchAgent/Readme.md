# Hub-and-Spoke Marketing Agent Architecture

This directory (`ResearchAgent`) implements a Capabillity-Driven Graph using the [Google Agent Development Kit (ADK)](https://github.com/google/adk). 

It employs a dynamic **Hub & Spoke** model where a central manager acts as the "Hub" and delegates specialized tasks to various "Spokes" (worker agents), ultimately synthesizing their outputs into a cohesive final presentation. This is contrary to a rigid, predefined sequential pipeline.

## Core Architecture

### 1. `ComplianceRootAgent` (The Gatekeeper)
Before any real work happens, every user prompt passes through the `ComplianceAgent`. 
* **Responsibility:** Ensure the query adheres to safety, policy, and brand guidelines.
* **Flow:** If approved, it allows the prompt to proceed to the Coordinator. If blocked, it immediately returns a refusal message and halts execution.

### 2. `GeneralRequestCoordinator` (The Hub)
Defined in `manager_agent.py`, this is the heart of the system. It receives the validated user prompt and coordinates the execution of the entire workflow.
* **Mechanism:** It wraps the worker agents as `AgentTool`s in its tools array (e.g. `tools=[AgentTool(research_agent)]`). Critically, the Coordinator is equipped with ADK's `BuiltInPlanner` and `ThinkingConfig(include_thoughts=True)`. This combination is designed to force the LLM into an internal reasoning loop: evaluating the user prompt, formulating a plan, sequentially invoking the `AgentTool`s in a single turn, and keeping control to synthesize the final result without stopping mid-execution.
* **Flow:**
    1. The Coordinator evaluates the prompt based on `REQUEST_COORDINATOR_INSTRUCTION`.
    2. It conditionally calls `ResearchAgent` to gather RAG references or web citations.
    3. Once Research returns text to the context, the Coordinator evaluates the findings in the same turn.
    4. If the user asked for concepts, the Coordinator calls the `IdeationAgent`, passing along the newly gathered context.
    5. Next, if visuals are needed, the Coordinator calls the `VisualAgent`.
    6. Finally, once all required Spokes have completed their nested execution, the Coordinator synthesizes all the textual insights and visual moodboards into a cohesive final presentation for the user.

## Capability Units (The Spokes)

These are specialized worker agents wrapped as tools for the Coordinator. They are designed to do exactly one thing very well and are shielded from the end-user.

### 1. `ResearchAgent` (`research_agent.py` & `instructions.py`)
Responsible for gathering factual grounding.
* **Capabilities:** 
    * **RAG (Retrieval-Augmented Generation):** It can use `rag_over_uploaded_doc` to search through local reference documents.
    * **Web Search:** It can execute live Google Searches using the `google_search` tool.
* **Constraints:** Must always execute RAG *before* falling back to Web Search (enforced via tool callbacks).

### 2. `IdeationAgent` (`ideation_agent.py` & `ideation_instructions.py`)
Responsible for creativity and text generation.
* **Role:** A senior copywriter. It takes the factual output produced by the `ResearchAgent` and crafts engaging marketing copy, taglines, and creative concepts.

### 3. `VisualAgent` (`visual_agent.py` & `visual_instructions.py`)
Responsible for imagery and moodboards.
* **Role:** An Art Director. It takes the creative concepts from the `IdeationAgent` and translates them into comprehensive visual prompts or moodboards.

## Getting Started & Configuration

1. **Environment Variables:** Copy `.env.example` to `.env` and configure your API keys.
    * `GOOGLE_API_KEY`: Required for Gemini model access.
    * `ENABLE_RAG_RESEARCH` / `ENABLE_WEB_RESEARCH`: Toggle flags to enable specific tool usage.
2. **Reference Docs:** Place any text documents (e.g., `brand_guidelines.txt`) into the `reference_docs/` folder. The RAG tool is natively configured to look here if a bare filename is passed.
3. **Execution:** 
    * Run locally via the ADK Developer UI: `adk web`

## Central Reference Docs
- Default folder: `ResearchAgent/reference_docs`
- Supported extensions for auto-pick: `.txt`, `.md`, `.json`, `.csv`, `.log`, `.pdf`
- Runtime discovery is resilient to different working directories and checks multiple candidate paths; when not found, tool output includes `searched_reference_dirs` for debugging.
