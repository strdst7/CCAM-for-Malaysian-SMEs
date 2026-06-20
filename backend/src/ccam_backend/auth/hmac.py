import hmac
import hashlib
import base64
from datetime import datetime, timezone


def _epoch_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def sign_request(
    secret: bytes,
    method: str,
    path: str,
    body: bytes,
    timestamp: int | None = None,
) -> tuple[int, str]:
    if timestamp is None:
        timestamp = _epoch_ms()
    payload = f"{method.upper()}\n{path}\n{timestamp}\n".encode() + body
    signature = hmac.new(secret, payload, hashlib.sha256).digest()
    return timestamp, base64.b64encode(signature).decode()


def verify_signature(
    secret: bytes,
    method: str,
    path: str,
    body: bytes,
    timestamp: int,
    signature_b64: str,
    max_skew_ms: int = 300_000,
) -> bool:
    now_ms = _epoch_ms()
    if abs(now_ms - timestamp) > max_skew_ms:
        return False
    expected_b64 = sign_request(secret, method, path, body, timestamp)[1]
    return hmac.compare_digest(expected_b64, signature_b64)
