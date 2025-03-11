import os
import openai
from dotenv import load_dotenv
from schema import *
from templates import *


load_dotenv()  # Loads environment variables from a .env file if present
openai.api_key = os.getenv("OPENAI_API_KEY", "")

class ProfanityClassifierBot:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        # The model to be used for openai ChatCompletion
        self.client = openai.OpenAI()
        self.model_name = model_name

    def classify(self, user_text: str) -> BaseModel:
        prompt = format_profanity_classification_template(user_text)
        response = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": prompt}
            ],
            response_format=BinaryClassificationResponse,
            temperature=0.0
        )
        return response.choices[0].message.parsed

