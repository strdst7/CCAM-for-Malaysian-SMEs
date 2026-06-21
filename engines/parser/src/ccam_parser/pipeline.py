"""Main parser pipeline — regex first, DistilBERT NER fallback.

Flow:
1. Run RegexEngine on the message
2. If regex confidence >= threshold (default 0.6), return regex result
3. If regex confidence < threshold, run NEREngine
4. If NER confidence > regex confidence, use NER result
5. Otherwise, use regex result with low confidence warning

Each field gets a per-field confidence score and the overall
result has an overall_confidence.
"""

from ccam_parser.regex_engine import RegexEngine
from ccam_parser.ner_engine import NEREngine
from ccam_parser.models import ParsedItem, ParsedOrder


DEFAULT_CONFIDENCE_THRESHOLD = 0.6


class ParserPipeline:
    """Orchestrates regex-first → NER fallback parsing pipeline.

    Usage:
        pipeline = ParserPipeline()
        order = pipeline.parse("2 Nasi Lemak Ayam, RM15")
    """

    def __init__(
        self,
        regex_engine: RegexEngine | None = None,
        ner_engine: NEREngine | None = None,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ):
        self._regex = regex_engine or RegexEngine()
        self._ner = ner_engine or NEREngine()
        self._threshold = confidence_threshold

    def parse(self, message: str) -> ParsedOrder:
        """Parse a raw WhatsApp message into a structured ParsedOrder.

        Uses regex first. Falls back to NER if regex confidence < threshold.
        """
        # ── Phase 1: Regex ──
        regex_result = self._regex.parse(message)
        regex_items = regex_result.items
        regex_confidence = regex_result.confidence

        if regex_confidence >= self._threshold and regex_items:
            # Regex is sufficient — return regex result
            return self._to_parsed_order(regex_result, message, "regex")

        # ── Phase 2: NER fallback ──
        try:
            ner_raw = self._ner.extract(message)
            ner_confidence = ner_raw.get("confidence", 0.0)
            ner_items = ner_raw.get("items", [])

            # If NER found more items or has higher confidence, use NER
            if ner_confidence > regex_confidence and ner_items:
                parsed = self._ner_to_parsed_order(ner_raw, message, confidence=ner_confidence)
                parsed.overall_confidence = ner_confidence
                return parsed

            # NER didn't improve — use regex result with its confidence
            parsed = self._to_parsed_order(regex_result, message, "regex")
            parsed.overall_confidence = regex_confidence
            return parsed

        except Exception:
            # NER failed — return regex result as-is
            parsed = self._to_parsed_order(regex_result, message, "regex")
            parsed.overall_confidence = regex_confidence
            return parsed

    def _to_parsed_order(self, regex_result, message: str, source: str) -> ParsedOrder:
        """Convert RegexResult to ParsedOrder."""
        items = regex_result.items
        per_field = {}

        if items:
            per_field["items"] = min(item.confidence for item in items)
        per_field["customer_name"] = 1.0 if regex_result.customer_name else 0.0
        per_field["pickup_time"] = 1.0 if regex_result.raw_time else 0.0
        per_field["total_price"] = 1.0 if regex_result.total_price_cents is not None else 0.0

        return ParsedOrder(
            items=items,
            customer_name=regex_result.customer_name,
            pickup_time=regex_result.raw_time,
            special_instructions=regex_result.special_instructions,
            total_price_cents=regex_result.total_price_cents,
            raw_text=message,
            per_field_confidence=per_field,
            overall_confidence=regex_result.confidence,
            parser_source=source,
        )

    def _ner_to_parsed_order(self, ner_raw: dict, message: str, confidence: float) -> ParsedOrder:
        """Convert NER result dict to ParsedOrder."""
        items = [
            ParsedItem(
                name=item.get("name", ""),
                quantity=item.get("quantity", 1),
                confidence=item.get("confidence", 0.5),
            )
            for item in ner_raw.get("items", [])
        ]
        return ParsedOrder(
            items=items,
            customer_name=ner_raw.get("customer_name", ""),
            pickup_time=ner_raw.get("raw_time", ""),
            raw_text=message,
            per_field_confidence={
                "items": min((i.confidence for i in items), default=0.0),
                "customer_name": 1.0 if ner_raw.get("customer_name") else 0.0,
                "pickup_time": 1.0 if ner_raw.get("raw_time") else 0.0,
            },
            overall_confidence=confidence,
            parser_source="ner",
        )


# Convenience function for simple use cases
def parse_message(message: str) -> ParsedOrder:
    """Parse a WhatsApp message into a structured ParsedOrder.

    Uses default pipeline with regex-first, NER-fallback approach.
    """
    pipeline = ParserPipeline()
    return pipeline.parse(message)
