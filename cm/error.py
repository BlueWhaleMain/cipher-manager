class CmBaseException(BaseException):
    """密码管理器所有异常基类"""


class CmInterrupt(CmBaseException, KeyboardInterrupt):
    """中断操作异常

    打断消息循环直到被处理

    尽量使用return代替"""


class CmException(CmBaseException, Exception):
    pass


class CmRuntimeError(CmBaseException, RuntimeError):
    pass


class CmTypeError(CmException, TypeError):
    pass


class CmValueError(CmException, ValueError):
    pass


class CmNotImplementedError(CmRuntimeError, NotImplementedError):
    pass
