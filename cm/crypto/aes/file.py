from cm.crypto.aes.base import AESCryptAlgorithm, AesCfg
from cm.crypto.file import SimpleCipherFile


class CipherAesFile(SimpleCipherFile):
    """ Aes密钥文件 """
    # 使用的加密算法
    encrypt_algorithm = AESCryptAlgorithm.__TYPE__
    # 根密码哈希
    rph: str = ''
    # crypto.Aes配置
    aes_cfg: AesCfg
