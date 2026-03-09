import os
import uuid
from google import genai
from google.genai import types
from google.adk.tools import ToolContext 

# Note: Making the function async is recommended for artifact saving
async def generate_concept_images(prompt: str, tool_context: ToolContext = None,number_of_images=4) -> str:
    """
    Generates images and registers them as ADK artifacts with proper MIME types.
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    response = client.models.generate_images(
        model='imagen-4.0-generate-001',
        prompt=prompt,
        config=types.GenerateImagesConfig(number_of_images=number_of_images)
        )
    
    save_dir = "concept_outputs"
    os.makedirs(save_dir, exist_ok=True)
    
    for i, generated_image in enumerate(response.generated_images):
        file_name = f"concept_{i+1}_{uuid.uuid4().hex[:8]}.png"
        
        # 1. Local Disk Save
        save_path = os.path.join(save_dir, file_name)
        generated_image.image.save(location=save_path)

        # 2. Artifact Save (UI Detection)
        if tool_context:
            # Wrap bytes in a Part object with a clear mime_type
            image_part = types.Part.from_bytes(
                data=generated_image.image.image_bytes, 
                mime_type="image/png"
            )
            
            # Use await for the artifact service
            await tool_context.save_artifact(
                filename=file_name, 
                artifact=image_part
            )

    return "Concepts generated. Please check the 'Artifacts' tab on the left for more details."

# tools.py
import os
import uuid
from google import genai
from google.genai import types
from google.adk.tools import ToolContext

async def generate_nano_banana_images(prompt: str, tool_context: ToolContext = None) -> str:
    """
    Generates images using the Nano Banana (Gemini 2.5 Flash Image) model.
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # Nano Banana uses generate_content with a specific model ID
    response = client.models.generate_content(
        model='gemini-2.5-flash-image',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"]
        )
    )
    
    save_dir = "nano_outputs"
    os.makedirs(save_dir, exist_ok=True)
    
    # Extract images from the multimodal response parts
    image_count = 0
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            image_count += 1
            file_name = f"nano_{image_count}_{uuid.uuid4().hex[:8]}.png"
            save_path = os.path.join(save_dir, file_name)
            
            # Save to disk
            with open(save_path, "wb") as f:
                f.write(part.inline_data.data)

            # Save as ADK Artifact for UI display
            if tool_context:
                image_part = types.Part.from_bytes(
                    data=part.inline_data.data, 
                    mime_type="image/png"
                )
                await tool_context.save_artifact(file_name, image_part)
                
    return f"Successfully generated {image_count} images using Nano Banana."