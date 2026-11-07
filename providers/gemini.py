
from google import genai
from google.genai import types
from providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def analyse(self, issue, files=None):
        contents = [issue]

        for file in files or []:
            contents.append(
                types.Part.from_bytes(
                    data=file.getvalue(),
                    mime_type=file.type
                )
            )

        response = self.client.models.generate_content(
            model="gemini-3.8-flash",
            contents=contents
        )

        return response.text
