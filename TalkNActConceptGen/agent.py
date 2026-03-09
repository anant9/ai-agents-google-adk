import os
from google.adk.agents import Agent
from ConceptGeneration.tools import generate_nano_banana_images # Importing your custom tool
from ConceptGeneration.instructions import CONCEPT_ARTIST_INSTRUCTION

# 1. Define Sub-Agents with access to your tool
apparel_agent = Agent(
    name="ApparelExpert",
    instruction="""You are a high-end fashion concept designer. 
    Analyze user requests for clothing, textiles, or wearable tech.
    """+CONCEPT_ARTIST_INSTRUCTION,
    tools=[generate_nano_banana_images]
)

soft_drink_agent = Agent(
    name="BeverageExpert",
    instruction="""You are a beverage branding and packaging expert. 
    Focus on bottle shapes, label designs, and liquid aesthetics for soft drinks.
    """+CONCEPT_ARTIST_INSTRUCTION,
    tools=[generate_nano_banana_images]
)

sports_agent = Agent(
    name="SportsExpert",
    instruction="""You are a sports equipment and athletic gear specialist. 
    Create concepts for footwear, equipment, or team jerseys.
    """+CONCEPT_ARTIST_INSTRUCTION,
    tools=[generate_nano_banana_images]
)

# 2. Define the Root Orchestrator
root_agent = Agent(
    name="IndustryConceptOrchestrator",
    model="gemini-2.0-flash",
    instruction="""You are the primary router for a concept generation suite.
    - Route queries about clothes, fashion, or style to ApparelExpert.
    - Route queries about soda, drinks, or beverages to BeverageExpert.
    - Route queries about athletic gear, gym equipment, or sports teams to SportsExpert.
    If a query is ambiguous, ask for clarification before routing.""",
    sub_agents=[apparel_agent, soft_drink_agent, sports_agent]
)

# 3. Execution Wrapper
if __name__ == "__main__":
    # Initialize the engine with the root agent
    #engine = AgentEngine(root_agent)
    #engine.run()
    print("Concept Generation Orchestrator is ready to receive queries.")