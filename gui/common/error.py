class InterruptError(KeyboardInterrupt):
    def __init__(self, msg: str = '', exc=None):
        self._msg: str = msg
        self._exc = exc

    @property
    def msg(self) -> str:
        return self._msg

    @property
    def exc(self):
        return self._exc
