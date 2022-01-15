import typing

import pydantic

from cm.file import CipherFile


class SimpleCipherFile(CipherFile):
    """ 常规密钥文件 """

    class Record(pydantic.BaseModel):
        """ 记录 """
        key: str
        value: str

    # 使用的哈希算法
    hash_algorithm: str
    # 根密码哈希
    rph: str
    # 盐
    salt: str
    # 记录
    records: typing.List[Record] = []


class PPCipherFile(CipherFile):
    """ 公私钥文件 """

    class Record(pydantic.BaseModel):
        """ 记录 """
        key: str
        value: str
        sign: str

    # 签名使用的哈希算法
    sign_hash_algorithm: str
    # 哈希算法签名
    hash_algorithm_sign: str = ''
    # 记录
    records: typing.List[Record] = []
