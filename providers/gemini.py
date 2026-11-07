from google import genai
from google.genai import types
from providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self, api_key):
        # Set timeout to 300,000 milliseconds (5 minutes)
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=300000)
        )

    def analyse(self, issue, files=None):
        print("FIXI: Sending request to Gemini...", flush=True)

        input_data = [issue]
        if files:
            input_data.extend(files)

        response = self.client.interactions.create(
            model="gemini-3.8-flash",
            input=input_data
        )

        print("FIXI: Gemini response received!", flush=True)

        return response.output_text
