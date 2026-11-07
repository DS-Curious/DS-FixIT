
from google import genai
from providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def analyse(self, issue):
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
            You are DS-FixIT, a Universal AI Problem Detector.

            Detect the issue, analyse possible causes,
            suggest solutions and prevention methods.

            Issue:
            {issue}
            """
        )

        return response.text
