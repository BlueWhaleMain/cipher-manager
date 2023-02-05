import typing

from cm.crypto.aes.file import CipherAesFile
from cm.crypto.des.file import CipherDesFile
from cm.crypto.rsa.file import CipherRSAFile
from cm.file import CipherFile


class CipherFileSupport:
    """ 密钥文件支持 """

    @classmethod
    def parse_file(cls, filepath) -> tuple[typing.Optional[CipherFile], list[BaseException]]:
        """
        尝试解析文件
        :param filepath: 序列化的文件（例如JSON）
        :return: 密钥文件对象（可能为空），异常列表
        """
        cipher_file = None
        errors = []
        try:
            cipher_file = CipherDesFile.parse_file(filepath)
        except BaseException as e:
            errors.append(e)
        try:
            cipher_file = CipherAesFile.parse_file(filepath)
        except BaseException as e:
            errors.append(e)
        try:
            cipher_file = CipherRSAFile.parse_file(filepath)
        except BaseException as e:
            errors.append(e)
        return cipher_file, errors
