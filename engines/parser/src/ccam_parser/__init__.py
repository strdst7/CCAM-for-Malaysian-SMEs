"""CCAM Parser Engine — regex-first + DistilBERT NER for Malaysian F&B WhatsApp parsing."""
__version__ = "0.1.0"

from ccam_parser.pipeline import ParserPipeline, parse_message
from ccam_parser.regex_engine import RegexEngine, RegexResult
from ccam_parser.ner_engine import NEREngine
from ccam_parser.models import ParsedItem, ParsedOrder, RegexPattern
from ccam_parser.exceptions import ParserError, RegexParseError, NERError

__all__ = [
    "ParserPipeline", "parse_message",
    "RegexEngine", "RegexResult",
    "NEREngine",
    "ParsedItem", "ParsedOrder", "RegexPattern",
    "ParserError", "RegexParseError", "NERError",
]
