"""Password hashing helpers."""

import hashlib
import hmac
import secrets


# ---------------------------------------------------------------------------
# CTEM-SAST-03 | CWE-327 / CWE-916 | Weak cryptographic hash for passwords
# Passwords use a salted, adaptive PBKDF2-HMAC-SHA256 KDF.
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    iterations = 600_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iteration_text, salt_hex, digest_hex = stored_hash.split("$", 3)
        iterations = int(iteration_text)
        salt = bytes.fromhex(salt_hex)
        expected_digest = bytes.fromhex(digest_hex)
    except (AttributeError, ValueError):
        return False

    if algorithm != "pbkdf2_sha256" or iterations != 600_000 or len(salt) != 16:
        return False

    actual_digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(actual_digest, expected_digest)
