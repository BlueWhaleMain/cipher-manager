import json
import random


class CryptAlgorithm:
    __TYPE__: str


def random_bytes(bytes_len: int) -> bytes:
    return bytes([random.randint(0, 255) for _ in range(bytes_len)])


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
        raise ValueError(data)


class CryptoEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, bytes):
            return o.hex()
