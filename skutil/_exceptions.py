class SpeculationFailedError(Exception):
    def __init__(self, message):
        super().__init__("Failed to save by speculation, "+message)
