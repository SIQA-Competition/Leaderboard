# scripts/decrypt_answers.py
import os
import sys
import base64
import tarfile
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def decrypt_and_extract(password: str, enc_file: str = "answer.tar.gz.enc", out_dir: str = "answer"):
    """从密码解密 answer.tar.gz.enc 并解压到指定目录"""
    SALT = b"siqa_leaderboard_salt_2026"

    # 派生密钥
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))

    # 解密
    with open(enc_file, "rb") as f:
        encrypted_data = f.read()
    decrypted_data = Fernet(key).decrypt(encrypted_data)

    # 写入临时 tar.gz
    tar_path = "answer.tar.gz"
    with open(tar_path, "wb") as f:
        f.write(decrypted_data)

    # 安全解压
    os.makedirs(out_dir, exist_ok=True)

    # 兼容旧版 Python（GitHub Actions 的 Ubuntu 可能是 Python 3.10）
    with tarfile.open(tar_path) as tar:
        try:
            # Python 3.12+
            tar.extractall(path=out_dir, filter="data")
        except TypeError:
            # Python < 3.12 不支持 filter
            tar.extractall(path=out_dir)

    # ✅ 关键：打印实际解压出的所有文件路径
    print(f"✅ Files extracted to '{os.path.abspath(out_dir)}/':")
    found_files = []
    for root, dirs, files in os.walk(out_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, ".")
            print(f"  - {rel_path}")
            found_files.append(rel_path)

    if not found_files:
        print("  ⚠️  No files found! Check your .tar.gz content.")
    else:
        # 特别检查关键文件是否存在
        expected = ["answer/answer-u.json", "answer/answer-s.json"]
        for e in expected:
            if any(f == e for f in found_files):
                print(f"  ✅ Found expected file: {e}")
            else:
                print(f"  ❌ Missing expected file: {e}")

    return out_dir


if __name__ == "__main__":
    password = os.getenv("ANSWERS_DECRYPT_KEY")
    if not password:
        print("❌ Error: Environment variable ANSWERS_DECRYPT_KEY is not set", file=sys.stderr)
        sys.exit(1)

    try:
        decrypt_and_extract(password)
    except Exception as e:
        print(f"❌ Decryption failed: {e}", file=sys.stderr)
        sys.exit(1)