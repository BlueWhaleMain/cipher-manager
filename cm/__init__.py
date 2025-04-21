from cm.error import CmValueError, CmTypeError
from cm.file.base import CipherFile
from cm.file.protect import ProtectCipherFile
from cm.file.table_record import TableRecordCipherFile

__author__ = "BlueWhaleMain"

version_info = (2, 0, '1')

__version__ = ".".join([str(x) for x in version_info])

def file_load(data: dict) -> CipherFile:
    if 'content_type' not in data:
        raise CmTypeError('加载的数据缺少内容类型字段')
    content_type = data['content_type']
    if content_type == TableRecordCipherFile.CONTENT_TYPE:
        return TableRecordCipherFile(**data)
    if content_type == ProtectCipherFile.CONTENT_TYPE:
        return ProtectCipherFile(**data)
    raise CmValueError(f'加载的数据内容类型未知：{content_type}')
