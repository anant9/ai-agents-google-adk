from google.adk.agents import Agent
from ConceptGeneration.tools import generate_concept_images, generate_nano_banana_images
from ConceptGeneration.instructions import CONCEPT_ARTIST_INSTRUCTION
#from ConceptGeneration.tools import generate_concept_images
# The framework automatically wraps 'generate_concept_images' as a FunctionTool
root_agent = Agent(
    name="ConceptArtistAgent",
    model="gemini-2.0-flash",
    instruction=CONCEPT_ARTIST_INSTRUCTION,
    tools=[generate_nano_banana_images]
)

if __name__ == "__main__":
    # Test input
    user_idea = "A futuristic market in a rainy Tokyo alley with traditional lanterns"
    
    print(f"Refining concept for: '{user_idea}'...")
    
    # Run the agent
    response = root_agent.run(input=user_idea)
    print("\n--- Agent Execution Summary ---")
    print(response)