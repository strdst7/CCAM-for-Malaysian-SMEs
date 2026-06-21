"""Data models for message parsing results."""
from dataclasses import dataclass, field


@dataclass
class ParsedItem:
    """A single line item extracted from a message."""
    name: str                            # e.g., "Nasi Lemak Ayam"
    quantity: int = 1
    unit_price_cents: int | None = None  # e.g., 1500 for RM15.00
    notes: str = ""
    confidence: float = 1.0              # per-item confidence 0.0-1.0


@dataclass
class ParsedOrder:
    """Complete structured order extracted from a WhatsApp message."""
    items: list[ParsedItem] = field(default_factory=list)
    customer_name: str = ""
    pickup_time: str = ""                # raw time string
    special_instructions: str = ""
    total_price_cents: int | None = None # if mentioned in message
    raw_text: str = ""                   # original message for audit
    per_field_confidence: dict[str, float] = field(default_factory=dict)
    overall_confidence: float = 1.0      # 0.0-1.0
    parser_source: str = ""              # "regex" or "ner"


@dataclass
class RegexPattern:
    """A compiled regex pattern for extracting a specific field."""
    field: str
    pattern: str
    priority: int = 0
    post_process: str = ""               # optional transform name
