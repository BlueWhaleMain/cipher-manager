from typing import Iterable

from cm.error import CmRuntimeError
from cm.file.base import CipherFile

_TABLE_RECORD_CIPER_FILE_CONTENT_TYPE = "application/cm-table-record"


class TableRecordCipherFile(CipherFile):
    """ 加密表格文件 """
    content_type: str = _TABLE_RECORD_CIPER_FILE_CONTENT_TYPE
    # 记录
    records: list[list[bytes]] = []

    def reader(self) -> Iterable[Iterable[str]]:
        for row in self.records:
            yield self._row_reader(row)

    def _row_reader(self, row: Iterable[bytes]) -> Iterable[str]:
        for col in row:
            yield self._record_value_decrypt(col)

    @property
    def sum(self) -> int:
        _sum = 0
        for row in self.records:
            for col in row:
                if col:
                    _sum += 1
        return _sum

    def get_cell(self, row: int, col: int) -> str | None:
        if row >= len(self.records):
            return None
        records_row = self.records[row]
        if col >= len(records_row):
            return None
        return self._record_value_decrypt(records_row[col])

    def set_cell(self, row: int, col: int, value: str) -> None:
        rows = len(self.records)
        if rows <= row:
            self.records.extend([[] for _ in range(row - rows + 1)])
        records_row = self.records[row]
        cols = len(records_row)
        if cols <= col:
            records_row.extend([b'' for _ in range(col - cols + 1)])
        records_row[col] = self._record_value_encrypt(value)

    def append_row(self, value: list[str]):
        self.append([self._record_value_encrypt(col) if col else b'' for col in value])

    def _record_value_encrypt(self, value: str) -> bytes:
        if not value:
            return b''
        return self._encrypt(value.encode(self.content_encoding))

    def _record_value_decrypt(self, value: bytes) -> str:
        if not value:
            return ''
        try:
            return self._decrypt(value).decode(self.content_encoding)
        except UnicodeDecodeError as e:
            raise CmRuntimeError(f'解密失败：{e.object}') from e


TableRecordCipherFile.CONTENT_TYPE = _TABLE_RECORD_CIPER_FILE_CONTENT_TYPE
