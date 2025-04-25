#  MIT License
#
#  Copyright (c) 2022-2025 BlueWhaleMain
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
class CmBaseException(BaseException):
    """CipherManager所有异常基类"""


class CmInterrupt(CmBaseException, KeyboardInterrupt):
    """
    CipherManager中断操作异常

    打断消息循环直到被处理

    尽量使用return代替
    """


class CmException(CmBaseException, Exception):
    """CipherManager异常"""


class CmRuntimeError(CmBaseException, RuntimeError):
    """CipherManager运行时错误"""


class CmTypeError(CmException, TypeError):
    """CipherManager类型错误"""


class CmValueError(CmException, ValueError):
    """CipherManager值错误"""


class CmNotImplementedError(CmRuntimeError, NotImplementedError):
    """CipherManager未实现错误"""
