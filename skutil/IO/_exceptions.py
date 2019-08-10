class SpeculationFailedError(Exception):
    def __init__(self, message):
        super().__init__("Failed to save by speculation, "+message)

class NotDecoratableError(Exception):
    def __init__(self, obj):
        super().__init__(f"{str(obj)} cannot be decorated by checkpoint, it may be a generator or a coroutine.")
