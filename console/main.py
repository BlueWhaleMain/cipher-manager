import json
import os
import pickle
import sys

import OpenSSL
import pyDes
import rsa
from Crypto.Cipher import AES

from cm.crypto.aes.base import AesCfg, AESCryptAlgorithm
from cm.crypto.aes.file import CipherAesFile
from cm.crypto.base import random_bytes, CryptoEncoder
from cm.crypto.des.base import DESCryptAlgorithm, DesCfg
from cm.crypto.des.file import CipherDesFile
from cm.crypto.file import SimpleCipherFile, PPCipherFile
from cm.crypto.rsa.base import RSACryptAlgorithm
from cm.crypto.rsa.file import CipherRSAFile
from cm.file import CipherFile
from cm.hash.base import HashAlgorithm, Sha512
from console.base import Console


def get_hash_algorithm(_type: str) -> HashAlgorithm:
    if _type == Sha512.__TYPE__:
        return Sha512()
    raise ValueError


ENCODING = 'UTF-8'


def main():
    crypt_algorithm = None

    def get_or_create_pp_crypt_algorithm(cf: PPCipherFile):
        if crypt_algorithm is not None:
            return crypt_algorithm
        chl_ = ('G', 'I', 'Q')
        cho_ = chl_[console.choice('方式（G=生成，I=导入，Q=退出）', chl_)]
        if cho_ == 'G':
            pk = OpenSSL.crypto.PKey()
            pk.generate_key(OpenSSL.crypto.TYPE_RSA, int(console.get_input('输入密钥长度：')))
            puk = rsa.PublicKey.load_pkcs1_openssl_pem(OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, pk))
            prk = rsa.PrivateKey.load_pkcs1(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_ASN1, pk), 'DER')
            cf.hash_algorithm_sign = rsa.sign(cf.sign_hash_algorithm.encode(cf.encoding), prk,
                                              cf.sign_hash_algorithm).hex()
            pp_fp = console.get_input('输入证书文件路径：')
            pp_pwd = None
            try:
                pp_pwd = console.get_input('输入证书文件密码（没有输入Ctrl+Z）：', mask='*', v_callback=console.verify_input,
                                           v_args=('*',)).encode(cipher_file.encoding)
            except KeyboardInterrupt:
                pass
            with open(pp_fp, 'wb') as pf:
                if pp_pwd:
                    pf.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, pk, 'des-ede3-cbc', pp_pwd))
                else:
                    pf.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, pk))
        elif cho_ == 'I':
            pp_fp = console.get_input('输入证书文件路径：')
            pp_pwd = None
            try:
                pp_pwd = console.get_input('输入证书文件密码（没有输入Ctrl+Z）：', mask='*').encode(cipher_file.encoding)
            except KeyboardInterrupt:
                pass
            pk = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, open(pp_fp, 'rb').read(), pp_pwd)
            puk = rsa.PublicKey.load_pkcs1_openssl_pem(OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, pk))
            prk = None
            try:
                prk = rsa.PrivateKey.load_pkcs1(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_ASN1, pk), 'DER')
            except Exception as ce:
                print(ce)
                print('导入私钥失败，仅验证模式。')
        elif cho_ == 'Q':
            raise RuntimeError('放弃加载密钥。')
        else:
            raise RuntimeError(f'未知操作码：{cho_}。')
        if isinstance(cf, CipherRSAFile):
            ca = RSACryptAlgorithm(Sha512.__TYPE__, puk, prk)
        else:
            raise RuntimeError(f'未知的加密方式：{cf.encrypt_algorithm}')
        if not ca.verify(cf.sign_hash_algorithm.encode(), bytes.fromhex(cf.hash_algorithm_sign)):
            raise RuntimeError('密钥与文件不符、损坏，或者遭到篡改。')
        return ca

    def get_simple_crypt_algorithm(cf: SimpleCipherFile):
        if crypt_algorithm is not None:
            return crypt_algorithm
        rp = console.get_input('输入根密码：', mask='*').encode(cf.encoding)
        if isinstance(cf, CipherDesFile):
            ca = DESCryptAlgorithm(rp, cf.des_cfg)
        elif isinstance(cf, CipherAesFile):
            ca = AESCryptAlgorithm(rp, cf.aes_cfg)
        else:
            raise RuntimeError(f'未知的加密方式：{cf.encrypt_algorithm}。')
        if not bytes.fromhex(cf.rph) == get_hash_algorithm(cf.hash_algorithm).hash(rp + bytes.fromhex(cf.salt)):
            raise RuntimeError('密码错误！')
        return ca

    console = Console()
    if len(sys.argv) > 1:
        cipher_path = sys.argv[1]
    else:
        cipher_path = console.get_input('输入密钥文件路径：')
    cipher_file = None
    if os.path.exists(cipher_path):
        with open(cipher_path, 'rb') as f:
            cipher_file = pickle.load(f)
    else:
        if console.choice('文件不存在，创建一个'):
            chl = ('D', 'A', 'R', 'Q')
            cho = chl[console.choice('类型（D=DES，A=AES，R=RSA，Q=退出）', chl)]
            if cho == 'D':
                salt = random_bytes(32)
                cipher_file = CipherDesFile(encoding=ENCODING, hash_algorithm=Sha512.__TYPE__, salt=salt.hex(),
                                            des_cfg=DesCfg(mode=pyDes.CBC, padmode=pyDes.PAD_PKCS5,
                                                           IV=DESCryptAlgorithm.generate_iv()))
                __root_pwd = console.get_input('输入根密码：', mask='*', v_callback=console.verify_input,
                                               v_args=('*',)).encode(cipher_file.encoding)
                crypt_algorithm = DESCryptAlgorithm(__root_pwd, cipher_file.des_cfg)
                cipher_file.rph = Sha512.hash(__root_pwd + salt).hex()
                del __root_pwd
                with open(cipher_path, 'wb') as f:
                    pickle.dump(cipher_file, f)
                print('DES文件成功创建。')
            elif cho == 'A':
                salt = random_bytes(32)
                cipher_file = CipherAesFile(encoding=ENCODING, hash_algorithm=Sha512.__TYPE__, salt=salt.hex(),
                                            aes_cfg=AesCfg(mode=AES.MODE_CBC, padmode=pyDes.PAD_PKCS5,
                                                           IV=AESCryptAlgorithm.generate_iv(AES.MODE_CBC)))
                __root_pwd = console.get_input('输入根密码：', mask='*', v_callback=console.verify_input,
                                               v_args=('*',)).encode(cipher_file.encoding)
                crypt_algorithm = AESCryptAlgorithm(__root_pwd, cipher_file.aes_cfg)
                cipher_file.rph = Sha512.hash(__root_pwd + salt).hex()
                del __root_pwd
                with open(cipher_path, 'wb') as f:
                    pickle.dump(cipher_file, f)
                print('AES文件成功创建。')
            elif cho == 'R':
                cipher_file = CipherRSAFile(encoding=ENCODING, sign_hash_algorithm=Sha512.__TYPE__)
                crypt_algorithm = get_or_create_pp_crypt_algorithm(cipher_file)
                with open(cipher_path, 'wb') as f:
                    pickle.dump(cipher_file, f)
                print('RSA文件成功创建。')
            elif cho == 'Q':
                exit(0)
            else:
                print(f'未知操作码：{cho}。')
                exit(2)
        else:
            exit(0)
    is_running = True
    changed = False
    while is_running:
        try:
            chl = ('A', 'L', 'G', 'P', 'D', 'W', 'E', 'Q')
            cho = chl[console.choice('操作（A=文件属性，L=密码列表，G=读取密码，P=添加密码，D=删除密码，W=保存密码，E=导出密码，Q=退出）', chl)]
            if cho == 'A':
                print('--属性--')
                if isinstance(cipher_file, CipherFile):
                    print('--文件属性--')
                    print(f'文件编码：{cipher_file.encoding}')
                    print(f'加密类型：{cipher_file.encrypt_algorithm}')
                    if isinstance(cipher_file, SimpleCipherFile):
                        print('--常规密钥文件附加属性--')
                        print(f'使用的哈希算法：{cipher_file.hash_algorithm}')
                        print(f'根密码哈希值：{cipher_file.rph}')
                        print(f'根密码盐值：{cipher_file.salt}')
                        print(f'存储的记录数量：{len(cipher_file.records)}')
                    elif isinstance(cipher_file, PPCipherFile):
                        print('--公私钥文件附加属性--')
                        print(f'签名使用的哈希算法：{cipher_file.sign_hash_algorithm}')
                        print(f'哈希算法签名：{cipher_file.hash_algorithm_sign}')
                        print(f'存储的记录数量：{len(cipher_file.records)}')
                print('没有更多了')
            elif cho == 'L':
                if isinstance(cipher_file, (SimpleCipherFile, PPCipherFile)):
                    print('--密码列表--')
                    for i in range(len(cipher_file.records)):
                        print(i, cipher_file.records[i].key)
                    else:
                        print('没有更多了。')
                else:
                    raise TypeError(type(cipher_file))
            elif cho == 'G':
                if isinstance(cipher_file, SimpleCipherFile):
                    if not cipher_file.records:
                        print('文件为空。')
                        continue
                    __k = console.choice(
                        f'选择读取的条目{[f"{i}={cipher_file.records[i].key}" for i in range(len(cipher_file.records))]}',
                        tuple(range(len(cipher_file.records))))
                    crypt_algorithm = get_simple_crypt_algorithm(cipher_file)
                    if isinstance(cipher_file, CipherDesFile):
                        value = crypt_algorithm.des_decrypt(bytes.fromhex(cipher_file.records[__k].value)).decode(
                            cipher_file.encoding)
                    elif isinstance(cipher_file, CipherAesFile):
                        value = crypt_algorithm.aes_decrypt(bytes.fromhex(cipher_file.records[__k].value)).decode(
                            cipher_file.encoding)
                    else:
                        raise TypeError(type(cipher_file))
                    console.protect_show(f'{value}\r')
                elif isinstance(cipher_file, PPCipherFile):
                    if not cipher_file.records:
                        print('文件为空。')
                        continue
                    __k = console.choice(
                        f'选择读取的条目{[f"{i}={cipher_file.records[i].key}" for i in range(len(cipher_file.records))]}',
                        tuple(range(len(cipher_file.records))))
                    crypt_algorithm = get_or_create_pp_crypt_algorithm(cipher_file)
                    if crypt_algorithm.readonly:
                        raise RuntimeError('没有私钥无法操作')
                    if isinstance(cipher_file, CipherRSAFile):
                        if not crypt_algorithm.verify(
                                (cipher_file.records[__k].key + cipher_file.records[__k].value).encode(
                                    cipher_file.encoding), bytes.fromhex(cipher_file.records[__k].sign)):
                            raise RuntimeError('记录损坏')
                        value = crypt_algorithm.rsa_decrypt(bytes.fromhex(cipher_file.records[__k].value)).decode(
                            cipher_file.encoding)
                    else:
                        raise TypeError(type(cipher_file))
                    console.protect_show(f'{value}\r')
                else:
                    raise TypeError(type(cipher_file))
            elif cho == 'P':
                __key = console.get_input('输入条目名称：')
                __val = console.get_input('密码：', mask='*', v_callback=console.verify_input, v_args=('*',)).encode(
                    cipher_file.encoding)
                if isinstance(cipher_file, SimpleCipherFile):
                    crypt_algorithm = get_simple_crypt_algorithm(cipher_file)
                    if isinstance(cipher_file, CipherDesFile):
                        cipher_file.records.append(
                            cipher_file.Record(key=__key, value=crypt_algorithm.des_encrypt(__val).hex()))
                    elif isinstance(cipher_file, CipherAesFile):
                        cipher_file.records.append(
                            cipher_file.Record(key=__key, value=crypt_algorithm.aes_encrypt(__val).hex()))
                    else:
                        raise TypeError(type(cipher_file))
                elif isinstance(cipher_file, PPCipherFile):
                    crypt_algorithm = get_or_create_pp_crypt_algorithm(cipher_file)
                    if crypt_algorithm.readonly:
                        raise RuntimeError('没有私钥无法操作')
                    if isinstance(cipher_file, CipherRSAFile):
                        __val = crypt_algorithm.rsa_encrypt(__val).hex()
                        cipher_file.records.append(
                            cipher_file.Record(key=__key, value=__val,
                                               sign=crypt_algorithm.sign(
                                                   (__key + __val).encode(cipher_file.encoding)).hex()))
                    else:
                        raise TypeError(type(cipher_file))
                else:
                    raise TypeError(type(cipher_file))
                print('已添加至内存。')
                changed = True
            elif cho == 'D':
                if isinstance(cipher_file, (SimpleCipherFile, PPCipherFile)):
                    __i = console.choice('选择删除的条目：', tuple(range(len(cipher_file.records))))
                    print(f'将删除{cipher_file.records[__i].key}')
                    if console.choice('确定删除：'):
                        cipher_file.records.remove(cipher_file.records[__i])
                        print('已从内存删除。')
                        changed = True
                    else:
                        print('操作已取消。')
                else:
                    raise TypeError(type(cipher_file))
            elif cho == 'W':
                with open(cipher_path, 'wb') as f:
                    pickle.dump(cipher_file, f)
                print('更改保存成功。')
                changed = False
            elif cho == 'E':
                __json_path = console.get_input('输入导出文件路径：')
                with open(__json_path, 'w') as f:
                    json.dump(cipher_file.dict(), f, indent=2, cls=CryptoEncoder)
                print('导出成功。')
            elif cho == 'Q':
                is_running = False
            else:
                print(f'未知操作码：{cho}。')
                break
        except (KeyboardInterrupt, EOFError):
            print('操作中断。')
        except Exception as e:
            print('发生异常。')
            print(console.get_error(e))
    else:
        if changed and console.choice('有操作未保存，保存'):
            with open(cipher_path, 'wb') as f:
                pickle.dump(cipher_file, f)
            print('已保存。')
    input('按Enter退出...')
