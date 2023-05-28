import hashlib
import typing

from cm.hash.base import HashAlgorithm, Sha512


def wrap_hash_algorithm(h) -> typing.Type[HashAlgorithm]:
    class _WrappedHashAlgorithm(HashAlgorithm):
        __TYPE__ = h.name.upper()

        @classmethod
        def hash(cls, data: bytes) -> bytes:
            h.update(data)
            return h.digest()

    return _WrappedHashAlgorithm


_internal_algorithm = [wrap_hash_algorithm(hashlib.new(x)) for x in hashlib.algorithms_available]


def get_hash_algorithm(_type: str) -> HashAlgorithm:
    # 历史兼容代码
    if _type == Sha512.__TYPE__:
        return Sha512()
    try:
        return wrap_hash_algorithm(hashlib.new(_type))()
    except ValueError:
        pass
    raise ValueError


def all_hash_algorithm() -> list[typing.Type[HashAlgorithm]]:
    return HashAlgorithm.__subclasses__() + _internal_algorithm
