from providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key):
        self.api_key = api_key

    def analyse(self, issue):
        return "OpenAI integration pending."
