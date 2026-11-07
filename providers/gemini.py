
from google import genai
from providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def analyse(self, issue, files=None):
        response = self.client.interactions.create(
            model="gemini-3.8-flash",
            input=issue
        )

        return response.output_text
