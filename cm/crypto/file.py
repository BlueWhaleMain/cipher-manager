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
