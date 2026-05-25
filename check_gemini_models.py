from google import genai
import os

# Load API key
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=API_KEY)

print("\nAvailable Gemini Models:\n")

models = client.models.list()

for model in models:
    print("MODEL NAME:", model.name)

    if hasattr(model, "supported_generation_methods"):
        print("SUPPORTED METHODS:", model.supported_generation_methods)

    print("-" * 50)