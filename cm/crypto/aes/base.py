import typing

import pydantic
from Crypto.Cipher import AES

from cm.crypto.base import CryptAlgorithm, random_bytes, fixed_bytes
from common.enum import DescriptionIntEnum


class AESModeEnum(DescriptionIntEnum):
    """ AES模式枚举 """
    ECB = AES.MODE_ECB, 'MODE_ECB'
    CBC = AES.MODE_CBC, 'MODE_CBC'
    CFB = AES.MODE_CFB, 'MODE_CFB'
    OFB = AES.MODE_OFB, 'MODE_OFB'
    CTR = AES.MODE_CTR, 'MODE_CTR'
    OPENPGP = AES.MODE_OPENPGP, 'MODE_OPENPGP'
    CCM = AES.MODE_CCM, 'MODE_CCM'
    EAX = AES.MODE_EAX, 'MODE_EAX'
    SIV = AES.MODE_SIV, 'MODE_SIV'
    GCM = AES.MODE_GCM, 'MODE_GCM'
    OCB = AES.MODE_OCB, 'MODE_OCB'


class AesCfg(pydantic.BaseModel):
    """ crypto.Aes配置 """
    mode: AESModeEnum = AESModeEnum.ECB
    iv: typing.Optional[bytes] = None
    IV: typing.Optional[bytes] = None
    nonce: typing.Optional[bytes] = None
    segment_size: typing.Optional[int] = None
    mac_len: typing.Optional[int] = None
    assoc_len: typing.Optional[int] = None
    initial_value: typing.Optional[typing.Union[int, bytes]] = None
    counter: typing.Optional[typing.Dict] = None
    use_aesni: typing.Optional[bool] = None

    @classmethod
    def from_dict(cls, d: dict):
        if 'iv' in d and isinstance(d['iv'], str):
            d['iv'] = bytes.fromhex(d['iv'])
        if 'IV' in d and isinstance(d['IV'], str):
            d['IV'] = bytes.fromhex(d['IV'])
        if 'nonce' in d and isinstance(d['nonce'], str):
            d['nonce'] = bytes.fromhex(d['nonce'])
        if 'initial_value' in d and isinstance(d['initial_value'], str):
            d['initial_value'] = bytes.fromhex(d['initial_value'])


class AESCryptAlgorithm(CryptAlgorithm):
    """ 实现所有的AES加解密逻辑 """
    __TYPE__ = 'AES'

    def __init__(self, key: typing.Union[bytes, bytearray, memoryview], cfg: AesCfg):
        self.__key = key
        self.__cfg = cfg

    def aes_encrypt(self, data: bytes) -> bytes:
        if self.__cfg.mode == AESModeEnum.CBC:
            data = fixed_bytes(data, 16, 16)
        return AES.new(self._extend_key(self.__key), **self.__cfg.dict(exclude_none=True)).encrypt(data)

    def aes_decrypt(self, data: bytes) -> bytes:
        return AES.new(self._extend_key(self.__key), **self.__cfg.dict(exclude_none=True)).decrypt(data)

    def _extend_key(self, key: bytes) -> bytes:
        if self.__cfg.mode == AESModeEnum.SIV:
            return fixed_bytes(key, 16, 32, 64)
        else:
            return fixed_bytes(key, 8, 16, 32)

    @classmethod
    def generate_iv(cls, mode: int) -> bytes:
        if mode in [AESModeEnum.CBC, AESModeEnum.CFB, AESModeEnum.OFB]:
            return random_bytes(16)
        # MODE_OPENPGP
        raise TypeError(mode)
