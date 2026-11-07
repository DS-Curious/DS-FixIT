from google import genai
from google.genai import types
from providers.base import BaseProvider

class GeminiProvider(BaseProvider):
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def analyse(self, issue, files=None):
        print("FIXI: Sending request to Gemini...", flush=True)

        # Build contents list including the issue text and any attached files
        contents = [issue]
        if files:
            contents.extend(files)

        # Increase timeout or configure via HttpOptions if necessary, 
        # and use the models generate_content API for robust payload handling
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",  # Update to a supported model version if needed
            contents=contents,
            config=types.GenerateContentConfig(
                http_options=types.HttpOptions(timeout=120.0) # Extends timeout to 120 seconds
            )
        )

        print("FIXI: Gemini response received!", flush=True)

        return response.text
