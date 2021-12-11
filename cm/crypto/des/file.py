from cm.crypto.des.base import DESCryptAlgorithm, DesCfg
from cm.crypto.file import SimpleCipherFile


class CipherDesFile(SimpleCipherFile):
    """ Des密钥文件 """
    # 使用的加密算法
    encrypt_algorithm = DESCryptAlgorithm.__TYPE__
    # 根密码哈希
    rph: str = ''
    # pyDes配置
    des_cfg: DesCfg
