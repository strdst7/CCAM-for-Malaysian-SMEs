"""Regex-first parser engine for Malaysian F&B WhatsApp messages.

Covers 80%+ of common patterns:
- Item + quantity patterns: "2 Nasi Lemak Ayam", "Nasi Lemak x2"
- Price patterns: "RM15", "RM 15.00", "15.00"
- Time patterns: "ambik pukul 2", "pickup 2pm", "2 petang"
- Common dishes: Nasi Lemak, Teh Tarik, Roti Canai, Mee Goreng, etc.
- Malay/English mixed language patterns
"""
import re
from dataclasses import dataclass, field

from ccam_parser.models import ParsedItem


# ── Pattern definitions ──────────────────────────────────────────
# Each group of patterns targets a specific field.
# Patterns are ordered by specificity (more specific first).

ITEM_PATTERNS = [
    # "2 Nasi Lemak Ayam" or "2x Nasi Lemak" — comma-separated or before price/EOS
    re.compile(r"(?P<qty>\d+)\s*x?\s*(?P<item>[A-Za-z\s/]+?)(?=\s*(?:RM|\d+\.\d{2}|[,;]|$))", re.IGNORECASE),
    # "Nasi Lemak x 2" or "Nasi Lemak 2x"
    re.compile(r"(?P<item>[A-Za-z\s/]+?)\s*x\s*(?P<qty>\d+)", re.IGNORECASE),
    # "Nasi Lemak (2)" 
    re.compile(r"(?P<item>[A-Za-z\s/]+?)\s*\((?P<qty>\d+)\)", re.IGNORECASE),
    # "Nasi Lemak" — standalone item name (implicit qty=1), at start or after separator
    re.compile(r"(?:^|[,;]\s*)(?P<item>[A-Za-z][A-Za-z\s/]+?)(?=\s*(?:RM|\d+\.\d{2}|[,;]|$))", re.IGNORECASE),
]

PRICE_PATTERNS = [
    # "RM15.00", "RM 15", "rm15"
    re.compile(r"RM\s*(?P<price>\d+(?:\.\d{1,2})?)", re.IGNORECASE),
    # "15.00" when it looks like a price (after item context)
    re.compile(r"(?<=\s)(?P<price>\d+\.\d{2})(?=\s|$)"),
    # "total RM15"
    re.compile(r"(?:total|jumlah)\s*:?\s*RM\s*(?P<price>\d+(?:\.\d{1,2})?)", re.IGNORECASE),
]

TIME_PATTERNS = [
    # "pukul 2", "pukul 2:30", "2pm", "2 pm"
    re.compile(r"(?:pukul|ambil|pickup|at)\s*(?P<hour>\d{1,2})(?::(?P<min>\d{2}))?\s*(?P<ampm>pm|am|ptg|pagi)?", re.IGNORECASE),
    # "2 petang", "2 pagi"
    re.compile(r"(?P<hour>\d{1,2})\s*(?P<ampm>petang|pagi|malam|tengahari)", re.IGNORECASE),
    # HH:MM standalone
    re.compile(r"\b(?P<hour>\d{1,2}):(?P<min>\d{2})\b"),
]

CUSTOMER_PATTERNS = [
    # "nama: Ali", "name: Ali", "atas nama Ali"
    re.compile(r"(?:nama|name|atas\s*nama)\s*:?\s*(?P<name>[A-Za-z\s]+)", re.IGNORECASE),
    # "dari Ali" at start
    re.compile(r"^dari\s+(?P<name>[A-Za-z\s]+)", re.IGNORECASE),
]

ITEM_NAME_CLEANUP = re.compile(r"[,\s]+$")

# Known non-food keywords to filter out from item names
NON_FOOD_KEYWORDS = {"rm", "total", "jumlah", "nama", "name", "catatan", "notes",
                     "pukul", "ambil", "pickup", "at", "dari", "dan", "&", "or"}


@dataclass
class RegexResult:
    """Result from regex parsing phase."""
    items: list[ParsedItem] = field(default_factory=list)
    raw_time: str = ""
    customer_name: str = ""
    special_instructions: str = ""
    total_price_cents: int | None = None
    confidence: float = 1.0
    matched_patterns: int = 0
    total_patterns_attempted: int = 0


class RegexEngine:
    """Regex-first parser for Malaysian F&B WhatsApp messages."""

    def parse(self, message: str) -> RegexResult:
        """Parse a raw WhatsApp message using regex patterns.

        Returns a RegexResult with extracted fields and confidence score.
        Returns empty fields (confidence=0) if no patterns match.
        """
        result = RegexResult()
        if not message or not message.strip():
            return result

        cleaned = message.strip()

        # ── Extract items ──
        items = self._extract_items(cleaned)
        result.items = items
        if items:
            result.matched_patterns += 1
        result.total_patterns_attempted += len(ITEM_PATTERNS)

        # ── Extract price ──
        for pat in PRICE_PATTERNS:
            match = pat.search(cleaned)
            if match:
                price_str = match.group("price")
                try:
                    price_float = float(price_str)
                    result.total_price_cents = int(round(price_float * 100))
                    result.matched_patterns += 1
                    break
                except ValueError:
                    continue
        result.total_patterns_attempted += len(PRICE_PATTERNS)

        # ── Extract time ──
        for pat in TIME_PATTERNS:
            match = pat.search(cleaned)
            if match:
                hour = match.group("hour")
                minute = match.group("min") if "min" in match.groupdict() and match.group("min") else "00"
                ampm = match.group("ampm") if "ampm" in match.groupdict() and match.group("ampm") else ""
                time_str = f"{hour}:{minute}"
                if ampm:
                    time_str += f" {ampm.lower()}"
                result.raw_time = time_str
                result.matched_patterns += 1
                break
        result.total_patterns_attempted += len(TIME_PATTERNS)

        # ── Extract customer ──
        for pat in CUSTOMER_PATTERNS:
            match = pat.search(cleaned)
            if match:
                name = match.group("name").strip()
                result.customer_name = name
                result.matched_patterns += 1
                break
        result.total_patterns_attempted += len(CUSTOMER_PATTERNS)

        # ── Special instructions ──
        # Look for lines after "catatan"/"notes" keyword
        notes_match = re.search(r"(?:catatan|notes?)\s*:?\s*(?P<notes>.+?)$", cleaned, re.IGNORECASE | re.MULTILINE)
        if notes_match:
            result.special_instructions = notes_match.group("notes").strip()

        # ── Compute confidence ──
        result.confidence = self._compute_confidence(result)

        return result

    def _extract_items(self, text: str) -> list[ParsedItem]:
        """Extract food line items from text using item patterns."""
        items = []
        seen = set()

        for pattern in ITEM_PATTERNS:
            for match in pattern.finditer(text):
                item_name = match.group("item").strip()
                item_name = ITEM_NAME_CLEANUP.sub("", item_name)
                gd = match.groupdict()
                qty_str = gd.get("qty")
                try:
                    qty = int(qty_str) if qty_str is not None else 1
                except ValueError:
                    qty = 1

                # Skip single-word non-food keywords (RM, total, etc.)
                name_lower = item_name.lower().strip()
                if name_lower in NON_FOOD_KEYWORDS:
                    continue

                # Dedup by lowercase name
                key = name_lower
                if key in seen:
                    continue
                seen.add(key)

                items.append(ParsedItem(
                    name=item_name,
                    quantity=qty,
                    confidence=0.9,  # regex match gives high confidence
                ))

        return items

    def _compute_confidence(self, result: RegexResult) -> float:
        """Compute overall confidence based on pattern match quality.

        Confidence is 0.0-1.0 based on how many patterns matched.
        Having items + at least one of (price, time, customer) = high confidence.
        """
        if not result.items:
            return 0.0

        base = 0.5  # items alone = 0.5
        bonus = 0.0

        if result.total_price_cents is not None:
            bonus += 0.2
        if result.raw_time:
            bonus += 0.15
        if result.customer_name:
            bonus += 0.15

        return min(1.0, base + bonus)
