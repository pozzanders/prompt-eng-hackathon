import os
import openai
from dotenv import load_dotenv
from typing import List, Dict, Any

from schema import GuardRailResponse
from guardrails import InputGuardRail, OutputGuardRail
from example_guardrails import *

load_dotenv()  # Loads environment variables from a .env file if present
openai.api_key = os.getenv("OPENAI_API_KEY", "")

class ChatBotBackend:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        # System message can be used as an initial instruction for the model
        self.system_message = {
            "role": "system",
            "content": "You are a helpful assistant."
        }

        # This list will store the conversation:
        # Each item in 'history' is a dict:
        # { "role": str, "content": str, "guardrail": GuardRailResponse }
        self.history: List[Dict[str, Any]] = []

        # The model to be used for openai ChatCompletion
        self.client = openai.OpenAI()
        self.model_name = model_name

        # Guardrail instances
        self.input_guardrail = InputGuardRail()
        self.output_guardrail = OutputGuardRail()

    def get_history(self) -> List[Dict[str, str]]:
        """
        Builds a list of messages for the LLM based on:
          1) The system message
          2) The conversation history
             If guardrail.exclude == True, we skip the message.
             If guardrail.triggered == True, we use guardrail.new_text,
             otherwise we use the original content.
        """
        messages = [self.system_message]

        for item in self.history:
            if item["guardrail"].exclude:
                continue
            if item["guardrail"].triggered:
                # If triggered, the model sees the guardrail's 'new_text'
                messages.append({
                    "role": item["role"],
                    "content": item["guardrail"].new_text
                })
            else:
                # Otherwise, the model sees the original content
                messages.append({
                    "role": item["role"],
                    "content": item["content"]
                })
        return messages

    def generate(self, user_text: str) -> None:
        """
        - Checks user_text with the input guardrail.
        - Builds full chat history to pass to the LLM.
        - Calls the LLM to get a response.
        - Checks the LLM's response with the output guardrail.
        - Appends both user and assistant messages to the conversation history.
        """

        # Check user text via input guardrail
        input_check = self.input_guardrail.check(user_text)

        # Check if we should exclude the input from the history to the LLM
        if input_check.exclude:
            # Add the user message to history
            # We always store the original user input in "content"
            # along with the guardrail response
            self.history.append({
                "role": "user",
                "content": user_text,
                "guardrail": input_check
            })
            return

        # The text that the LLM will actually see from the user
        effective_user_text = input_check.new_text if input_check.triggered else user_text

        # Build the messages to send to the model
        messages = self.get_history()
        messages.append({"role": "user", "content": effective_user_text})

        # Call the OpenAI ChatCompletion endpoint
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7 # TODO
        )

        # Extract the model's output text
        assistant_text = response.choices[0].message.content

        # Check the assistant text via output guardrail
        output_check = self.output_guardrail.check(assistant_text)

        # Add the user message to history
        # We always store the original user input in "content"
        # along with the guardrail response
        self.history.append({
            "role": "user",
            "content": user_text,
            "guardrail": input_check
        })

        # Add the assistant message to history
        # We store the original LLM output in "content"
        # plus the guardrail response
        self.history.append({
            "role": "assistant",
            "content": assistant_text,
            "guardrail": output_check
        })

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Returns the raw conversation history for UI display.
        Each item has "role", "content", and "guardrail".
        """
        return self.history
