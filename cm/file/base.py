from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, Future
from enum import StrEnum
from tempfile import TemporaryFile
from typing import Any, BinaryIO, AnyStr, Iterable, Literal

import Crypto.Util
from Crypto.Cipher import DES, DES3, AES, PKCS1_OAEP, PKCS1_v1_5
from Crypto.Hash import SHA1, SHA256, SHA512, BLAKE2b
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from pydantic import BaseModel

from cm import CmValueError
from cm.base import erase, fixed_bytes, copy_bytes
from cm.error import CmNotImplementedError, CmRuntimeError
from cm.progress import CmProgress
from common.file import filesize_convert


class CipherName(StrEnum):
    """使用的加密算法"""
    DES = 'DES'
    DES3 = 'DES3'
    AES128 = 'AES-128'
    AES192 = 'AES-192'
    AES256 = 'AES-256'
    PKCS1_OAEP = 'PKCS1-OAEP'
    PKCS1_V1_5 = 'PKCS1-5'

    @property
    def padding(self) -> int:
        if self == self.DES or self == self.DES3:
            return 8
        if self == self.AES128 or self == self.AES192 or self == self.AES256:
            return 16
        return -1


class HashName(StrEnum):
    SHA1 = 'SHA1'
    SHA256 = 'SHA256'
    SHA512 = 'SHA512'
    BLAKE2B = 'BLAKE2b'


class KeyType(StrEnum):
    PASSWORD = 'PASSWORD'
    RSA_KEYSTORE = 'RSA_KEYSTORE'

    @property
    def need_salt_protect(self) -> bool:
        return self == self.PASSWORD

    @property
    def is_file(self) -> bool:
        return self != self.PASSWORD


class CipherFile(BaseModel):
    content_type: str
    content_encoding: str
    cipher_name: CipherName
    cipher_args: dict[str, Any] = {}
    iter_count: int = 1
    key_type: KeyType = KeyType.PASSWORD
    key_hash: bytes | None = None
    key_hash_name: HashName
    key_hash_args: dict[str, Any] = {}
    key_hash_iter_count: int | None = 1
    password_salt: bytes | None = None
    password_salt_len: int | None = 16

    _key: Any | None = None
    _max_crypt_len: int = 0
    _decrypt_len: int = 0
    _cant_decrypt: bool = False

    def __del__(self):
        self.lock()

    @property
    def locked(self):
        return self._key is None

    def lock(self):
        if self._key is not None:
            erase(self._key)
            self._key = None

    def unlock(self, key: AnyStr = None, passphrase: str = None):
        if self.key_type == KeyType.PASSWORD:
            if isinstance(key, str):
                self._key = key.encode('utf-8')
            elif isinstance(key, bytes):
                self._key = copy_bytes(key)
            try:
                self._cipher()
            except ValueError as e:
                raise CmValueError(e) from e
        elif self.key_type == KeyType.RSA_KEYSTORE:
            try:
                self._key = RSA.importKey(key, passphrase)
            except ValueError as e:
                raise CmValueError(e) from e
        else:
            raise CmNotImplementedError(f"unknown key_type: {self.key_type}")

    def set_key(self, key: AnyStr | None) -> bool:
        if self.key_hash is not None:
            return False
        if self.password_salt is None and self.key_type.need_salt_protect:
            self.password_salt = get_random_bytes(self.password_salt_len)
        if isinstance(key, str):
            key = key.encode('utf-8')
        elif isinstance(key, bytes):
            key = copy_bytes(key)
        else:
            return False
        self.key_hash = self._gen_key_hash(key)
        return True

    def validate_key(self, key: AnyStr | None) -> bool:
        if isinstance(key, str):
            key = key.encode('utf-8')
        elif isinstance(key, bytes):
            key = copy_bytes(key)
        else:
            return self.key_hash is None
        if self.cipher_name == CipherName.DES and len(key) > 8:
            return False
        elif self.cipher_name == CipherName.DES3 and len(key) > 24:
            return False
        elif self.cipher_name == CipherName.AES128 and len(key) > 16:
            return False
        elif self.cipher_name == CipherName.AES192 and len(key) > 24:
            return False
        elif self.cipher_name == CipherName.AES256 and len(key) > 32:
            return False
        return self.key_hash == self._gen_key_hash(key)

    def encrypt_stream(self, stream: BinaryIO, chunk_size: int, progress: CmProgress,
                       total: int = 0, concurrent_count: int = 1) -> Iterable[bytes]:
        if 0 < self._max_crypt_len < chunk_size:
            raise CmValueError('chunk_size too large')
        return self._iter_crypt_stream('encrypt', stream, chunk_size, progress, total, concurrent_count)

    def decrypt_stream(self, stream: BinaryIO, chunk_size: int, progress: CmProgress,
                       total: int = 0, concurrent_count: int = 1) -> Iterable[bytes]:
        if self._cant_decrypt:
            raise CmRuntimeError('cannot decrypt')
        if 0 < self._decrypt_len < chunk_size:
            raise CmValueError('chunk_size too large')
        return self._iter_crypt_stream('decrypt', stream, chunk_size, progress, total, concurrent_count)

    def _iter_crypt_stream(self, mode: Literal['encrypt', 'decrypt'], stream: BinaryIO, chunk_size: int,
                           progress: CmProgress, total: int = 0, concurrent_count: int = 1) -> Iterable[bytes]:
        title = '加密' if mode == 'encrypt' else '解密'
        raw_stream = stream
        if self.iter_count > 1:
            iter_count = self.iter_count - 1
            iter_progress = progress.start_or_sub(iter_count)
            for i in range(iter_count):
                temp_stream = TemporaryFile('w+b')
                crypt_progress = iter_progress.start_or_sub(total // chunk_size,
                                                            f'{title}迭代中，还剩{iter_count - i}步',
                                                            unit=f'区块（{chunk_size}字节）')
                current_size = 0
                cipher = self._cipher()
                for chunk in self._crypt_stream(getattr(cipher, mode), stream, chunk_size, concurrent_count):
                    current_size += chunk_size
                    temp_stream.write(chunk)
                    crypt_progress.step(last_msg=f'{title}中...{filesize_convert(current_size)}'
                                                 f' / {filesize_convert(total)}')
                crypt_progress.complete()
                if stream != raw_stream:
                    stream.close()
                stream = temp_stream
                stream.seek(0)
                iter_progress.step()
            iter_progress.complete()
        cipher = self._cipher()
        for chunk in self._crypt_stream(getattr(cipher, mode), stream, chunk_size, concurrent_count):
            yield chunk
        if stream != raw_stream:
            stream.close()

    def _crypt_stream(self, func: Callable[[bytes], bytes], stream: BinaryIO, chunk_size: int,
                      concurrent_count: int = 1) -> Iterable[bytes]:
        if concurrent_count > 1:
            if self.cipher_name.padding > 0:
                raise CmValueError('padding cipher not support concurrent')
            with ThreadPoolExecutor(max_workers=concurrent_count) as executor:
                futures: list[Future] = []
                while chunk := stream.read(chunk_size):
                    while len(futures) >= concurrent_count:
                        yield futures.pop(0).result()
                    futures.append(executor.submit(func, chunk))
                while futures:
                    yield futures.pop(0).result()
            return
        while chunk := stream.read(chunk_size):
            if self.cipher_name.padding > 0:
                chunk = fixed_bytes(chunk, self.cipher_name.padding)
            yield func(chunk)

    def _encrypt(self, data: bytes) -> bytes:
        self._cipher()
        if self.cipher_name.padding > 0:
            data = fixed_bytes(data, self.cipher_name.padding)
        for _ in range(self.iter_count):
            try:
                data = self._cipher().encrypt(data)
            except ValueError as e:
                raise CmValueError(e) from e
        return data

    def _decrypt(self, data: bytes) -> bytes:
        self._cipher()
        if self._cant_decrypt:
            raise CmRuntimeError('cannot decrypt')
        for _ in range(self.iter_count):
            try:
                data = self._cipher().decrypt(data)
            except ValueError as e:
                raise CmValueError(e) from e
        return data.rstrip(b'\x00') if self.cipher_name.padding > 0 else data

    def _cipher(self):
        if self._key is None:
            raise RuntimeError(f'_key is None')
        self._max_crypt_len = 0
        self._decrypt_len = 0
        self._cant_decrypt = False

        if self.cipher_name == CipherName.DES:
            return DES.new(fixed_bytes(self._key, 8, 8, 8), **self.cipher_args)
        elif self.cipher_name == CipherName.DES3:
            return DES3.new(fixed_bytes(self._key, 8, 16, 24), **self.cipher_args)
        elif self.cipher_name == CipherName.AES128:
            return AES.new(fixed_bytes(self._key, 8, 16, 16), **self.cipher_args)
        elif self.cipher_name == CipherName.AES192:
            return AES.new(fixed_bytes(self._key, 8, 24, 24), **self.cipher_args)
        elif self.cipher_name == CipherName.AES256:
            return AES.new(fixed_bytes(self._key, 8, 32, 32), **self.cipher_args)
        elif self.cipher_name == CipherName.PKCS1_OAEP:
            if self.key_type == KeyType.RSA_KEYSTORE:
                mod_bits = Crypto.Util.number.size(self._key.n)
                k = Crypto.Util.number.ceil_div(mod_bits, 8)
                if 'hashAlgo' in self.cipher_args:
                    hash_algo = self.cipher_args['hashAlgo']
                else:
                    hash_algo = SHA1
                self._max_crypt_len = k - 2 * hash_algo.digest_size - 2
                self._decrypt_len = k
                self._cant_decrypt = (k < hash_algo.digest_size + 2)
            return PKCS1_OAEP.new(self._key, **self.cipher_args)
        elif self.cipher_name == CipherName.PKCS1_V1_5:
            if self.key_type == KeyType.RSA_KEYSTORE:
                k = self._key.size_in_bytes()
                self._max_crypt_len = k - 11
                self._decrypt_len = k
            return PKCS1_v1_5.new(self._key, **self.cipher_args)
        else:
            raise CmNotImplementedError(f'unknown cipher name: {self.cipher_name}')

    def _gen_key_hash(self, key: AnyStr) -> bytes:
        if isinstance(key, str):
            data_to_hash = key.encode('utf-8')
        else:
            data_to_hash = copy_bytes(key)
        erase(key)
        if self.key_type.need_salt_protect:
            data_to_hash = data_to_hash + self.password_salt
        for i in range(self.key_hash_iter_count):
            data_to_hash = self._key_hash(data_to_hash).digest()
        return data_to_hash

    def _key_hash(self, data=None):
        if self.key_hash_name == HashName.SHA1:
            return SHA1.new(data)
        elif self.key_hash_name == HashName.SHA256:
            return SHA256.new(data)
        elif self.key_hash_name == HashName.SHA512:
            return SHA512.new(data, **self.key_hash_args)
        elif self.key_hash_name == HashName.BLAKE2B:
            return BLAKE2b.new(data=data, **self.key_hash_args)
        else:
            raise CmNotImplementedError(f'unknown key_hash_name: {self.key_hash_name}')
