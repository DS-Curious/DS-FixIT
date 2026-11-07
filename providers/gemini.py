from google import genai
from google.genai import types
from providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self, api_key):
        # Configure client with an increased global HTTP timeout (e.g., 120 seconds)
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=120.0)
        )

    def analyse(self, issue, files=None):
        print("FIXI: Sending request to Gemini...", flush=True)

        # Build contents including the text issue and any provided files
        contents = [issue]
        if files:
            contents.extend(files)

        response = self.client.models.generate_content(
            model="gemini-3.8-flash",
            contents=contents
        )

        print("FIXI: Gemini response received!", flush=True)

        return response.text
