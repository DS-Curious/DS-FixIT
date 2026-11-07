class AIRouter:
    def __init__(self):
        self.providers = {}
        self.active_provider = None

    def register_provider(self, name, provider):
        self.providers[name] = provider

    def select_provider(self, name):
        if name not in self.providers:
            raise ValueError(f"Provider '{name}' not registered.")

        self.active_provider = name

    def analyse(self, issue):
        if not self.active_provider:
            raise RuntimeError("No AI provider selected.")

        provider = self.providers[self.active_provider]

        return provider.analyse(issue)


ai_router = AIRouter()
