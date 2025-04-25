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
from typing import Iterable

from cm.error import CmRuntimeError
from cm.file.base import CipherFile

# 加密表格文件内容类型
_TABLE_RECORD_CIPER_FILE_CONTENT_TYPE = "application/cm-table-record"


class TableRecordCipherFile(CipherFile):
    """
    加密表格文件

    Attributes:
        records: 字节表格
    """
    content_type: str = _TABLE_RECORD_CIPER_FILE_CONTENT_TYPE
    records: list[list[bytes]] = []

    def reader(self) -> Iterable[Iterable[str]]:
        """
        解密读取器

        Returns:
            可遍历的字节表格

        Raises:
            CmRuntimeError: 解密失败

        只会在遍历时读取
        """
        for row in self.records:
            yield self._row_reader(row)

    def _row_reader(self, row: Iterable[bytes]) -> Iterable[str]:
        """行内读取器"""
        for col in row:
            yield self._record_value_decrypt(col)

    @property
    def sum(self) -> int:
        """
        Returns:
            包含数据的单元格数量
        """
        _sum = 0
        for row in self.records:
            for col in row:
                if col:
                    _sum += 1
        return _sum

    def get_cell(self, row: int, col: int) -> str | None:
        """
        获取一个单元格解密后的内容

        Args:
            row: 行号
            col: 列号

        Returns:
            单元格内容

        Raises:
            CmRuntimeError: 解密失败

        行号列号均从0开始
        """
        if row >= len(self.records):
            return None
        records_row = self.records[row]
        if col >= len(records_row):
            return None
        return self._record_value_decrypt(records_row[col])

    def set_cell(self, row: int, col: int, value: str) -> None:
        """
        设置一个单元格的值并加密

        Args:
            row: 行号
            col: 列号
            value: 内容

        行号列号均从0开始
        """
        rows = len(self.records)
        if rows <= row:
            self.records.extend([[] for _ in range(row - rows + 1)])
        records_row = self.records[row]
        cols = len(records_row)
        if cols <= col:
            records_row.extend([b'' for _ in range(col - cols + 1)])
        records_row[col] = self._record_value_encrypt(value)

    def append_row(self, value: list[str]) -> None:
        """
        追加一行
        Args:
            value: 明文行数据
        """
        self.append([self._record_value_encrypt(col) if col else b'' for col in value])

    def _record_value_encrypt(self, value: str) -> bytes:
        """加密单个值"""
        if not value:
            return b''
        return self._encrypt(value.encode(self.content_encoding))

    def _record_value_decrypt(self, value: bytes) -> str:
        """解密单个值"""
        if not value:
            return ''
        try:
            return self._decrypt(value).decode(self.content_encoding)
        except UnicodeDecodeError as e:
            raise CmRuntimeError(f'解密失败：{e.object}') from e


TableRecordCipherFile.CONTENT_TYPE = _TABLE_RECORD_CIPER_FILE_CONTENT_TYPE
