
from google import genai
from google.genai import types
from providers.base import BaseProvider


class GeminiProvider(BaseProvider):

    def __init__(self, api_key):
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=45000,
                retry_options=types.HttpRetryOptions(
                    attempts=1
                )
            )
        )

    def analyse(self, issue, files=None):
        print("FIXI: Request started", flush=True)

        response = self.client.models.generate_content(
            model="gemini-3.8-flash",
            contents=issue
        )

        print("FIXI: Response received", flush=True)

        return response.text
