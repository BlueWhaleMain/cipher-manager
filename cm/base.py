import base64
import ctypes
import sys
from json import JSONEncoder


def copy_bytes(data: bytes) -> bytes:
    return bytes.fromhex(data.hex())


erase_disabled = False


def erase(secret):
    if erase_disabled:
        return
    if sys.maxsize > 2 ^ 32:
        offset = 24  # 64位操作系统
    else:
        offset = 12  # 32位操作系统
    buffer_size = sys.getsizeof(secret) - offset
    ctypes.memset(id(secret) + offset, 0, buffer_size)


def fixed_bytes(data: bytes, unit_len: int, min_len: int = 0, max_len: int = None):
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

    def default(self, o):
        if isinstance(o, bytes):
            return base64.standard_b64encode(o).decode()
