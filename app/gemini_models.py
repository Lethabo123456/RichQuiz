import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load your API key from environment variable or directly set it here
# Load .env from root directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Please set your GEMINI_API_KEY environment variable.")

# Configure the API
genai.configure(api_key=API_KEY)

# Attempt to list available models
try:
    models = genai.list_models()
    print("Available models:")
    for model in models:
        print(model)
except AttributeError:
    print("The method 'list_models()' is not supported in this SDK version.")
except Exception as e:
    print("An error occurred:", e)