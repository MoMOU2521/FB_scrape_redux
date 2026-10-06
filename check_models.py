# check_models.py
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Set API key directly (remove this after testing)
if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("GROQ_API_KEY is not set")

client = Groq()
models = client.models.list()

print("Available models:")
for model in models.data:
    print(f"  {model.id}")
