class OperationInterruptError(KeyboardInterrupt):
    """
    中断操作异常
    打断消息循环直到被处理
    尽量使用return代替
    """

    def __init__(self, msg: str = '', exc=None):
        self._msg: str = msg
        self._exc = exc

    @property
    def msg(self) -> str:
        return self._msg

    @property
    def exc(self):
        return self._exc
