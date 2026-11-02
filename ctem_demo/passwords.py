"""Password hashing helpers."""

import hashlib


# ---------------------------------------------------------------------------
# CTEM-SAST-03 | CWE-327 / CWE-916 | Weak cryptographic hash for passwords
# TRAINING EXAMPLE: unsalted MD5 is fast and precomputable, so leaked hashes
# can be cracked quickly. Remediation: use a salted, adaptive KDF
# (werkzeug.security.generate_password_hash -> scrypt / PBKDF2).
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    return hash_password(password) == stored_hash
