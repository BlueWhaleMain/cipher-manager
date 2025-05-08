#  MIT License
#
#  Copyright (c) 2022-2025 BlueWhaleMain
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
"""
Cipher Manager 旨在提供安全的、性能良好的、可深度定制的密码管理方案。

目前包含的功能列表：

* 加密存储
"""
from cm.error import CmValueError, CmTypeError
from cm.file.base import CipherFile
from cm.file.protect import ProtectCipherFile
from cm.file.table_record import TableRecordCipherFile

__author__ = "BlueWhaleMain"

version_info = (2, 0, '3')

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
