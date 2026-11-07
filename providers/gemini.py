
from google import genai
from google.genai import types
from providers.base import BaseProvider
import time


class GeminiProvider(BaseProvider):

    def __init__(self, api_key):
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=300000)
        )

    def analyse(self, issue, files=None):
        start = time.time()

        print("FIXI: Preparing request...", flush=True)

        contents = [
            "You are FIXI, an AI problem analysis assistant. "
            "Analyze the user's issue, identify possible causes, "
            "and suggest practical solutions.\n\n"
            f"USER ISSUE:\n{issue or 'Please analyze the uploaded evidence.'}"
        ]

        if files:
            for uploaded_file in files:
                file_bytes = uploaded_file.getvalue()

                contents.append(
                    types.Part.from_bytes(
                        data=file_bytes,
                        mime_type=uploaded_file.type
                        or "application/octet-stream"
                    )
                )

        try:
            print("FIXI: Sending request to Gemini...", flush=True)

            response = self.client.models.generate_content(
                model="gemini-3.8-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    max_output_tokens=2048
                )
            )

            print(
                f"FIXI: Completed in {time.time() - start:.2f}s",
                flush=True
            )

            if not response.text:
                raise RuntimeError("Gemini returned an empty response.")

            return response.text

        except Exception as e:
            print(f"FIXI ERROR: {repr(e)}", flush=True)
            raise
