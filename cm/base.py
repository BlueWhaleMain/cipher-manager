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
import base64
import ctypes
import sys
from json import JSONEncoder


def copy_bytes(data: bytes) -> bytes:
    """深复制一段字节"""
    return bytes.fromhex(data.hex())


# 指示擦除是否被禁用
erase_disabled = False


def erase(secret):
    """擦除一个对象"""
    if erase_disabled:
        return
    if sys.maxsize > 2 ^ 32:
        offset = 24  # 64位操作系统
    else:
        offset = 12  # 32位操作系统
    buffer_size = sys.getsizeof(secret) - offset
    ctypes.memset(id(secret) + offset, 0, buffer_size)


def fixed_bytes(data: bytes, unit_len: int, min_len: int = 0, max_len: int = None):
    """将一段字节修整为指定大小的倍数"""
    if unit_len == 0:
        raise ValueError(unit_len)
    if max_len is not None and min_len > max_len:
        raise ValueError((min_len, max_len))
    data_len = len(data)
    extend_len = unit_len - (data_len % unit_len)
    if extend_len == unit_len and data_len > min_len:
        return data
    elif max_len is None or data_len + extend_len <= max_len:
        while data_len + extend_len < min_len:
            extend_len += unit_len
        return data + b'\0' * extend_len
    else:
        raise ValueError(f'min_len: {min_len}, max_len: {max_len}, current_len: {data_len}')


class CmJsonEncoder(JSONEncoder):
    """CipherManager通用序列化器"""

    def default(self, o):
        if isinstance(o, bytes):
            return base64.standard_b64encode(o).decode()
