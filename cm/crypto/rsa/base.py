import rsa

from cm.crypto.base import CryptAlgorithm


class RSACryptAlgorithm(CryptAlgorithm):
    """ 实现所有的RSA加解密逻辑 """
    __TYPE__ = 'RSA'

    def __init__(self, hash_method: str, public_key: rsa.PublicKey, private_key: rsa.PrivateKey = None):
        self.__pub = public_key
        self.__pri = private_key
        self.__hash_method = hash_method

    @property
    def readonly(self) -> bool:
        return self.__pri is None

    def rsa_encrypt(self, data: bytes) -> bytes:
        return rsa.encrypt(data, self.__pub)

    def rsa_decrypt(self, data: bytes) -> bytes:
        return rsa.decrypt(data, self.__pri)

    def sign(self, data: bytes) -> bytes:
        return rsa.sign(data, self.__pri, self.__hash_method)

    def verify(self, message: bytes, signature: bytes) -> bool:
        try:
            return self.__hash_method.upper() == rsa.verify(message, signature, self.__pub).upper()
        except rsa.VerificationError:
            return False
