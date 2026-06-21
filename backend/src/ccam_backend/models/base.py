import time
import secrets
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


CROCKFORD_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _encode_base32(value: int, length: int) -> str:
    chars = []
    for _ in range(length):
        chars.append(CROCKFORD_ALPHABET[value & 0x1F])
        value >>= 5
    return "".join(reversed(chars))


def generate_ulid() -> str:
    timestamp_ms = int(time.time() * 1000)
    random_bits = secrets.randbits(80)
    return _encode_base32(timestamp_ms, 10) + _encode_base32(random_bits, 16)


class Base(DeclarativeBase):
    pass


class ULIDMixin:
    id: Mapped[str] = mapped_column(String(26), primary_key=True, default=generate_ulid)


class TimestampMixin:
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
