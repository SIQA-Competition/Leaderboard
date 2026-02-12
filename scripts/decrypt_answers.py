# scripts/decrypt_answers.py
import os
import sys
import base64
import tarfile
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def decrypt_and_extract(password: str, enc_file: str = "answer.tar.gz.enc", out_dir: str = "answer"):
    """从密码解密 answer.tar.gz.enc 并解压到指定目录（扁平化 answer/ 内容）"""
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

    tar_path = "answer.tar.gz"
    with open(tar_path, "wb") as f:
        f.write(decrypted_data)

    # 创建目标目录
    os.makedirs(out_dir, exist_ok=True)

    # === 关键修复：解压时去掉内部的 'answer/' 前缀 ===
    with tarfile.open(tar_path) as tar:
        members = []
        for member in tar.getmembers():
            # 只处理以 'answer/' 开头的文件（忽略可能的其他内容）
            if member.name.startswith("answer/") and member.name != "answer/":
                # 去掉 'answer/' 前缀，使内容直接放入 out_dir
                member.name = member.name[len("answer/"):]
                members.append(member)
            # 忽略顶层 'answer' 目录本身

        # 兼容旧版 Python（不支持 filter）
        try:
            tar.extractall(path=out_dir, members=members, filter="data")
        except TypeError:
            tar.extractall(path=out_dir, members=members)

    # 打印结果
    print(f"✅ Files extracted to '{os.path.abspath(out_dir)}/':")
    found_files = []
    for root, _, files in os.walk(out_dir):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), ".")
            print(f"  - {rel_path}")
            found_files.append(rel_path)

    expected = ["answer/answer-u.json", "answer/answer-s.json"]
    for e in expected:
        if e in found_files:
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