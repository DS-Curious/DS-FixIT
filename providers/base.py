class BaseProvider:
    def analyse(self, issue):
        raise NotImplementedError(
            "Provider must implement analyse()."
        )
