import abc
import hashlib


class HashAlgorithm:
    __TYPE__: str

    @classmethod
    @abc.abstractmethod
    def hash(cls, data: bytes) -> bytes:
        pass


class Sha512(HashAlgorithm):
    __TYPE__ = 'SHA-512'

    @classmethod
    def hash(cls, data: bytes) -> bytes:
        h = hashlib.sha512()
        h.update(data)
        return h.digest()
