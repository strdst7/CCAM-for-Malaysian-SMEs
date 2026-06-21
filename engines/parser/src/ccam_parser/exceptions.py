"""Exceptions for the parser engine."""

class ParserError(Exception):
    """Base exception for parser engine errors."""

class RegexParseError(ParserError):
    """Raised when regex parsing encounters an unexpected pattern."""

class NERError(ParserError):
    """Raised when ONNX NER inference fails."""
