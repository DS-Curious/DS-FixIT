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
    import time

    print("FIXI: Starting Gemini test...", flush=True)
    start = time.time()

    try:
        response = self.client.interactions.create(
            model="gemini-3.8-flash",
            input="Reply with exactly: Gemini connection successful."
        )

        elapsed = time.time() - start

        print(f"FIXI: Response received in {elapsed:.2f}s", flush=True)

        return response.output_text

    except Exception as e:
        elapsed = time.time() - start
        print(f"FIXI ERROR after {elapsed:.2f}s: {repr(e)}", flush=True)
        raise
