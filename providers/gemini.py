from google import genai
from google.genai import types
from providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self, api_key):
        # Initialize client with an extended global HTTP timeout (e.g., 120 seconds)
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=120.0)
        )

    def analyse(self, issue, files=None):
        print("FIXI: Sending request to Gemini...", flush=True)

        # Build input payload including text and optional files
        input_data = [issue]
        if files:
            input_data.extend(files)

        response = self.client.interactions.create(
            model="gemini-3.8-flash",
            input=input_data
        )

        print("FIXI: Gemini response received!", flush=True)

        return response.output_text
