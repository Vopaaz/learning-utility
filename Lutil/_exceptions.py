class SpeculationFailedError(Exception):
    def __init__(self, message):
        super().__init__("Failed to save by speculation, "+message)


class NotDecoratableError(Exception):
    def __init__(self, obj):
        super().__init__(
            f"{str(obj)} cannot be decorated by checkpoint, it may be a generator or a coroutine.")


class NotInlineCheckableError(Exception):
    def __init__(self, obj):
        super().__init__(
            f"{str(obj)} cannot be used for 'watch' parameter in InlineCheckpoint.")


class DuplicateSettingWarning(UserWarning):
    def __init__(self, name, obj):
        self.name = name
        self.obj = obj

    def __str__(self):
        return f"A {self.name} path is set after the first initialization of {self.obj.__class__}."


class ComplexParamsIdentifyWarning(UserWarning):
    def __init__(self, explain):
        self.explain = explain

    def __str__(self):
        return f"{self.explain}, it may cause mistake when detecting whether there is checkpoint for this call."


class InlineEnvironmentWarning(UserWarning):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return '''InlineCheckpoint is only functional in '__main__' to auto-cache a variable, while you are trying to use it inside a function or method.
The 'produce' will not be cached and the computation will always happen.
Please refer to https://learning-utility.readthedocs.io/en/latest/ for alternative solutions.'''


class SkipWithBlock(Exception):
    pass
