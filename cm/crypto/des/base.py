import typing

import pyDes
import pydantic

from cm.crypto.base import CryptAlgorithm, random_bytes, fixed_bytes


class DesCfg(pydantic.BaseModel):
    """ DES配置 """
    mode: int = pyDes.ECB
    IV: typing.Optional[bytes] = None
    pad: typing.Optional[bytes] = None
    padmode: int = pyDes.PAD_NORMAL

    @classmethod
    def from_dict(cls, d: dict):
        if 'IV' in d and isinstance(d['IV'], str):
            d['IV'] = bytes.fromhex(d['IV'])
        if 'pad' in d and isinstance(d['pad'], str):
            d['pad'] = bytes.fromhex(d['pad'])


class DESCryptAlgorithm(CryptAlgorithm):
    """ 实现所有的DES加解密逻辑 """
    __TYPE__ = 'DES'

    __des: typing.Union[pyDes.des, pyDes.triple_des]

    def __init__(self, key: bytes, cfg: DesCfg):
        key = self._extend_key(key)
        key_len = len(key)
        if key_len == 8:
            self.__des = pyDes.des(key, **cfg.dict())
        elif key_len == 16 or key_len == 24:
            self.__des = pyDes.triple_des(key, **cfg.dict())
        else:
            raise ValueError(key)

    def des_encrypt(self, data: bytes) -> bytes:
        return self.__des.encrypt(data)

    def des_decrypt(self, data: bytes) -> bytes:
        return self.__des.decrypt(data)

    @classmethod
    def _extend_key(cls, key: bytes) -> bytes:
        return fixed_bytes(key, 8, 8, 24)

    @classmethod
    def generate_iv(cls) -> bytes:
        return random_bytes(8)
