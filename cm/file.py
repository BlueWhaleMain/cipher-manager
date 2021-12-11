import pydantic


class CipherFile(pydantic.BaseModel):
    # 使用的编码
    encoding: str
    # 使用的加密算法
    encrypt_algorithm: str
