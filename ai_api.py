import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

# Configure the Gemini API client
genai.configure(api_key=API_KEY)

def to_bool(value):
    if value == 'true':
        return True
    elif value == 'True':
        return True
    elif value == 'false':
        return False
    elif value == 'False':
        return False
    elif value == 0:
        return False
    elif value == 1:
        return True
    else:
        raise ValueError("Value was not recognized as a valid Boolean.")

def fight(champion, prev_champion):
    prompt = f"Determine who wins in a battle between \"{champion}\" and \"{prev_champion}\". YOU MUST CHOOSE A WINNER. YOU CANNOT RETURN EMPTY ANSWERS. LIST THE WINNING CHAMPION NAME IN THE \"champion\" section EXACTLY AS IT WAS PROVIDED, EVEN IF GRAMMAR AND CAPITALIZATION ARE OFF. YOU MUST RETURN A JSON STRING: {{\"champion\":<either \"{champion}\" or \"{prev_champion}\",\"how_champion_wins\":<short sentence saying how one champion beats the other>}}"
    
    try:
        # Initialize the generative model (you might need to use the specific model name)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Generate content using the model
        response = model.generate_content(prompt)

        # Return the generated text if successful
        if (response):
            result = json.loads(re.sub(r'^[^{]*|[^}]*$', '', response.text))
            return result
        else:
            None
        # return json.loads(re.sub(r'^[^{]*|[^}]*$', '', response.text)) if response else None
    except Exception as e:
        print(f"Error generating text: {e}")
        return None

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
    

# def main():
#     res = fight("Mario ", "gokuuu")
#     print(res)
# main()
