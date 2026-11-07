from providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self, api_key):
        self.api_key = api_key

    def analyse(self, issue):
        return "Gemini integration pending."
