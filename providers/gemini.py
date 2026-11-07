from google import genai
from google.genai import types
from providers.base import BaseProvider
import time


class GeminiProvider(BaseProvider):

    def __init__(self, api_key):
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=300000
            )
        )

    def analyse(self, issue, files=None):
        start = time.time()

        print("FIXI: Gemini request started", flush=True)

        try:
            contents = [issue]

            if files:
                contents.extend(files)

            response = self.client.models.generate_content(
                model="gemini-3.8-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    max_output_tokens=2048,
                    temperature=0.2
                )
            )

            print(
                f"FIXI: Completed in {time.time() - start:.2f}s",
                flush=True
            )

            return response.text

        except Exception as e:
            print(
                f"FIXI: Failed after {time.time() - start:.2f}s: {repr(e)}",
                flush=True
            )
            raise
