#!/usr/bin/env python3
"""
CRX3 打包器：用固定 RSA 私钥签名扩展，计算确定性 Extension ID。

流程：
  1. 把扩展源码目录打包成 zip
  2. 计算 zip 的 SHA-256
  3. 用 openssl dgst -sha256 -sign 签名 zip
  4. 从 .pem 提取 DER 公钥
  5. 按 protobuf 编码 CrxFileHeader（sha256_with_rsa 形式）
  6. 写出 CRX3：magic + version + header_len + header + archive
  7. 由公钥 SHA-256 前 16 字节按 a-p 字母表编码出 Extension ID

用法：
  python3 pack_crx.py --src extension --key dist/keys/seetab.pem \
                      --out dist/crx-internal/seetab.crx
"""

import argparse
import hashlib
import os
import struct
import subprocess
import sys
import tempfile
import zipfile
import io


MAGIC = b'Cr24'
VERSION = 3

# 与 build_ext.sh 中的 COMMON_FILES 保持一致
COMMON_FILES = [
    'newtab.html', 'newtab.css', 'newtab.js',
    'options.html', 'options.css', 'options.js',
    'background.js',
    'i18n.js', 'pinyin.js',
    'icons/',
]


# === Protobuf 编码（手工实现，避免依赖 protobuf 库）===

def encode_varint(n):
    """LEB128 编码。"""
    out = bytearray()
    while n > 0x7F:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    out.append(n & 0x7F)
    return bytes(out)


def field_varint(field_num, value):
    """varint 字段。"""
    tag = (field_num << 3) | 0
    return encode_varint(tag) + encode_varint(value)


def field_bytes(field_num, value):
    """length-delimited 字段。"""
    tag = (field_num << 3) | 2
    return encode_varint(tag) + encode_varint(len(value)) + value


# === 工具 ===

def zip_extension(src_dir):
    """将扩展源码打包到内存中的 zip，与 build_ext.sh 的文件列表一致。"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        # manifest.json 必须包含
        zf.write(os.path.join(src_dir, 'manifest.json'), 'manifest.json')
        for rel in COMMON_FILES:
            full = os.path.join(src_dir, rel)
            if os.path.isdir(full):
                for root, _dirs, files in os.walk(full):
                    for fname in files:
                        fpath = os.path.join(root, fname)
                        arcname = os.path.relpath(fpath, src_dir)
                        zf.write(fpath, arcname)
            elif os.path.isfile(full):
                zf.write(full, rel)
    return buf.getvalue()


def get_public_key_der(pem_path):
    """用 openssl 从 .pem 提取 DER SubjectPublicKeyInfo。"""
    with tempfile.NamedTemporaryFile(suffix='.der', delete=False) as f:
        der_path = f.name
    try:
        subprocess.run(
            ['openssl', 'rsa', '-in', pem_path,
             '-pubout', '-outform', 'DER', '-out', der_path],
            check=True, stderr=subprocess.DEVNULL
        )
        with open(der_path, 'rb') as f:
            return f.read()
    finally:
        if os.path.exists(der_path):
            os.unlink(der_path)


def sign_data(pem_path, data):
    """用 openssl dgst -sha256 -sign 对任意数据签名（PKCS#1 v1.5 + SHA-256）。"""
    with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as f:
        f.write(data)
        data_path = f.name
    sig_path = data_path + '.sig'
    try:
        subprocess.run(
            ['openssl', 'dgst', '-sha256', '-sign', pem_path,
             '-out', sig_path, data_path],
            check=True, stderr=subprocess.DEVNULL
        )
        with open(sig_path, 'rb') as f:
            return f.read()
    finally:
        for p in (data_path, sig_path):
            if os.path.exists(p):
                os.unlink(p)


def compute_extension_id(public_key_der):
    """由公钥 DER 计算 Extension ID：SHA-256 前 16 字节按 a-p 编码。"""
    digest = hashlib.sha256(public_key_der).digest()
    alphabet = 'abcdefghijklmnop'
    chars = []
    for b in digest[:16]:
        chars.append(alphabet[b >> 4])
        chars.append(alphabet[b & 0x0F])
    return ''.join(chars)


def build_signed_data(ext_id, public_key_der):
    """构造 SignedData protobuf 并序列化为字节。

    SignedData {
      optional string crx_id = 1;          // 字段 1（32 字符 a-p 编码）
      optional bytes crx_public_key = 2;   // 字段 2（公钥 DER）
    }
    """
    return field_bytes(1, ext_id.encode('ascii')) + field_bytes(2, public_key_der)


def build_crx3_header(sha256_hash, public_key_der, ext_id, signature, signed_data_bytes):
    """构造 CrxFileHeader protobuf（asymmetric_key + signed_asymmetric_key_data）。

    现代 Chrome 要求此格式，否则报 CRX_REQUIRED_PROOF_MISSING。

    CrxFileHeader {
      optional Sha256WithRsa sha256_with_rsa = 1;             // 跳过（legacy）
      optional AsymmetricKey asymmetric_key = 2;               // 字段 2
      optional bytes sha256_hash = 10000;                       // 字段 10000
      optional SignedData signed_asymmetric_key_data = 10001;  // 字段 10001
    }
    AsymmetricKey {
      optional bytes public_key = 1;   // 字段 1
      optional bytes signature = 2;     // 字段 2
    }
    """
    asymmetric_key = field_bytes(1, public_key_der) + field_bytes(2, signature)
    return (
        field_bytes(2, asymmetric_key) +
        field_bytes(10000, sha256_hash) +
        field_bytes(10001, signed_data_bytes)
    )


def write_crx3(out_path, header, archive):
    """写出 CRX3 文件：magic + version + header_len + header + archive。"""
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    with open(out_path, 'wb') as f:
        f.write(MAGIC)
        f.write(struct.pack('<I', VERSION))
        f.write(struct.pack('<I', len(header)))
        f.write(header)
        f.write(archive)


def main():
    parser = argparse.ArgumentParser(description='CRX3 打包器')
    parser.add_argument('--src', required=True, help='扩展源码目录')
    parser.add_argument('--key', required=True, help='RSA 私钥 .pem 路径')
    parser.add_argument('--out', required=True, help='输出 .crx 路径')
    parser.add_argument('--id-only', action='store_true',
                        help='只计算并输出 Extension ID（不写 .crx）')
    args = parser.parse_args()

    if not os.path.isfile(args.key):
        sys.exit(f'错误: 私钥不存在: {args.key}')

    public_key_der = get_public_key_der(args.key)
    ext_id = compute_extension_id(public_key_der)

    if args.id_only:
        print(ext_id)
        return

    # 打包 zip
    archive = zip_extension(args.src)
    sha256_hash = hashlib.sha256(archive).digest()

    # 构造 SignedData（crx_id + crx_public_key），用私钥对其签名
    signed_data_bytes = build_signed_data(ext_id, public_key_der)
    signature = sign_data(args.key, signed_data_bytes)

    # 构造 CrxFileHeader（asymmetric_key + sha256_hash + signed_asymmetric_key_data）
    header = build_crx3_header(sha256_hash, public_key_der, ext_id,
                                 signature, signed_data_bytes)
    write_crx3(args.out, header, archive)

    print(f'==> 已写出 CRX3: {args.out}', file=sys.stderr)
    print(f'==> Extension ID: {ext_id}', file=sys.stderr)
    print(f'==> Archive: {len(archive)} bytes, Header: {len(header)} bytes, '
          f'Signature: {len(signature)} bytes', file=sys.stderr)


if __name__ == '__main__':
    main()
