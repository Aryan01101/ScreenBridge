"""
Processor module - Screen understanding and element tree construction.

Responsible for:
- OCR text extraction (Tesseract + EasyOCR fallback)
- Element tree building (atomacos on macOS)
- Diff engine for detecting meaningful changes
- Structured summary generation
"""

from screenbridge.processor.screen_processor import ScreenProcessor

__all__ = ["ScreenProcessor"]
