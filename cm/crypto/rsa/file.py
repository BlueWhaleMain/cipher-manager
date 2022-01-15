from cm.crypto.file import PPCipherFile
from cm.crypto.rsa.base import RSACryptAlgorithm


class CipherRSAFile(PPCipherFile):
    """ RSA密钥文件 """
    # 使用的加密算法
    encrypt_algorithm = RSACryptAlgorithm.__TYPE__
