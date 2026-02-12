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

    # 安全解压（防止路径穿越）
    os.makedirs(out_dir, exist_ok=True)
    with tarfile.open(tar_path) as tar:
        tar.extractall(path=out_dir, filter="data")  # Python 3.12+ 安全模式
        # 如果你用的是旧版 Python，用下面这行替代：
        # tar.extractall(path=out_dir)

    print(f"✅ Answers decrypted and extracted to '{out_dir}/'")
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