import typing

from cm.hash.base import HashAlgorithm, Sha512


def get_hash_algorithm(_type: str) -> HashAlgorithm:
    if _type == Sha512.__TYPE__:
        return Sha512()
    raise ValueError


def all_hash_algorithm() -> list[typing.Type[HashAlgorithm]]:
    return HashAlgorithm.__subclasses__()
