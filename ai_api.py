import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

# Configure the Gemini API client
genai.configure(api_key=API_KEY)

def generate_text(prompt):
    """
    Generates text using the Google Gemini API based on the provided prompt.

    Args:
        prompt (str): The text prompt to generate a response for.

    Returns:
        str: The generated text response from the AI model.
    """
    try:
        # Initialize the generative model (you might need to use the specific model name)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Generate content using the model
        response = model.generate_content(prompt)

        # Return the generated text if successful
        return response.text if response else None
    except Exception as e:
        print(f"Error generating text: {e}")
        return None
