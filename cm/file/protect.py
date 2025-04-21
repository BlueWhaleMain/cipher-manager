import base64
import os
import pickle
from binascii import crc32
from typing import Self

from cm.error import CmRuntimeError, CmValueError
from cm.file.base import CipherFile
from cm.progress import CmProgress
from common.file import filesize_convert

_PROTECT_CIPER_FILE_CONTENT_TYPE = "application/cm-protect"
_MAGIC = b'CM'


class ProtectCipherFile(CipherFile):
    content_type: str = _PROTECT_CIPER_FILE_CONTENT_TYPE

    filename: bytes | None = None
    total_size: int | None = None
    crc32: int | None = None
    _filepath: str | None = None

    @classmethod
    def from_cipher_file(cls, cipher_file: CipherFile) -> Self:
        self = cls(**cipher_file.model_dump())
        self.content_type = _PROTECT_CIPER_FILE_CONTENT_TYPE
        self._key = cipher_file._key
        return self

    @classmethod
    def from_protect_file(cls, filepath: str) -> Self:
        with open(filepath, 'rb') as f:
            if f.read(len(_MAGIC)) != _MAGIC:
                raise CmRuntimeError('不正确的文件开头')
            base64_bytes = b''
            while byte := f.read(1):
                if byte == b'\n':
                    break
                base64_bytes += byte
            try:
                header = pickle.loads(base64.standard_b64decode(base64_bytes))
            except Exception as e:
                raise CmRuntimeError('不正确的文件开头') from e
            if 'content_type' not in header or header['content_type'] != _PROTECT_CIPER_FILE_CONTENT_TYPE:
                raise CmRuntimeError('不正确的文件开头')
            self = cls(**header)
            self._filepath = filepath
            return self

    def pack_to(self, raw_filepath: str, dist_filepath: str, progress: CmProgress, chunk_size: int = 2048) -> None:
        self.total_size = os.path.getsize(raw_filepath)
        if self.total_size == 0:
            raise CmValueError('file is empty')
        progress.start_or_sub(self.total_size, '加密中...', filesize_convert, 'File Size')
        self._filepath = raw_filepath
        self.filename = self._encrypt(os.path.basename(raw_filepath).encode('utf-8'))
        with open(raw_filepath, 'rb') as f:
            crc = 0
            while chunk := f.read(chunk_size):
                crc = crc32(chunk, crc)
                progress.step(len(chunk), f'计算校验中...，CRC32：{str(crc)}.')
            self.crc32 = crc
        with open(raw_filepath, 'rb') as file:
            with open(dist_filepath, 'wb') as dist_file:
                dist_file.write(_MAGIC)
                dist_file.write(base64.standard_b64encode(pickle.dumps(self.model_dump())))
                dist_file.write(b'\n')
                if 0 < self._max_crypt_len < chunk_size:
                    chunk_size = self._max_crypt_len
                progress.restart(self.total_size // chunk_size, unit=f'区块（{chunk_size}字节）')
                current_size = 0
                for chunk in self.encrypt_stream(file, chunk_size, progress, self.total_size):
                    current_size += len(chunk)
                    dist_file.write(chunk)
                    progress.step(last_msg=f'加密中...{filesize_convert(current_size)}')
        progress.complete()

    def try_unlock_from_cipher_file(self, cipher_file: CipherFile) -> bool:
        if self.key_type != cipher_file.key_type:
            return False
        if self.key_type.is_file:
            if cipher_file._key is not None:
                self._key = cipher_file._key
            return True
        try:
            self.unlock(cipher_file._key)
            return True
        except CmValueError:
            return False

    def decrypt_filename(self) -> str | None:
        if self.filename is None:
            return None
        try:
            return self._decrypt(self.filename).decode('utf-8')
        except UnicodeDecodeError as e:
            raise CmRuntimeError(f'解密失败：{e.object}') from e

    def unpack_to(self, dist_filepath: str, progress: CmProgress, chunk_size: int = 2048) -> None:
        progress.start_or_sub(title='解密并校验中...')
        with open(self._filepath, 'rb') as f:
            if f.read(len(_MAGIC)) != _MAGIC:
                raise CmRuntimeError('不正确的文件开头')
            while byte := f.read(1):
                if byte == b'\n':
                    break
            with open(dist_filepath, 'wb') as dist_file:
                if self._decrypt_len > 0:
                    chunk_size = self._decrypt_len
                progress.restart(self.total_size // chunk_size, unit=f'区块（{chunk_size}字节）')
                current_size = 0
                crc = 0
                for chunk in self.decrypt_stream(f, chunk_size, progress, self.total_size):
                    if current_size + len(chunk) > self.total_size:
                        chunk = chunk[:self.total_size - current_size]
                    current_size += len(chunk)
                    crc = crc32(chunk, crc)
                    dist_file.write(chunk)
                    progress.step(last_msg=f'解密并校验中...{filesize_convert(current_size)}')
                if crc != self.crc32:
                    raise CmRuntimeError('文件校验失败')

        progress.complete()


ProtectCipherFile.CONTENT_TYPE = _PROTECT_CIPER_FILE_CONTENT_TYPE
