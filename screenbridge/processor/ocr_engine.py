"""OCR engine with Tesseract primary and EasyOCR fallback."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Any, Optional

import pytesseract
from PIL import Image


class OCREngine:
    """Handles text extraction from screenshots.

    Uses Tesseract as primary OCR (fast, good accuracy) with optional
    EasyOCR fallback for low-confidence regions (slower, higher accuracy).
    """

    def __init__(self, config: Any) -> None:
        """Initialize OCR engine.

        Args:
            config: ScreenBridge configuration object
        """
        self.config = config
        self._easyocr_reader: Optional[Any] = None
        self._easyocr_available = False

    async def initialize(self) -> None:
        """Initialize OCR engines."""
        # Try to import EasyOCR (optional dependency)
        try:
            import easyocr
            loop = asyncio.get_event_loop()
            # Initialize EasyOCR in thread pool (model loading is slow)
            self._easyocr_reader = await loop.run_in_executor(
                None,
                lambda: easyocr.Reader(['en'], gpu=False)  # CPU mode for compatibility
            )
            self._easyocr_available = True
        except ImportError:
            # EasyOCR not installed, will use Tesseract only
            self._easyocr_available = False

    async def cleanup(self) -> None:
        """Cleanup OCR resources."""
        self._easyocr_reader = None

    async def extract_text(
        self,
        image_path: Path,
        use_fallback: bool = True
    ) -> dict[str, Any]:
        """Extract text from image with bounding boxes.

        Args:
            image_path: Path to image file
            use_fallback: If True, use EasyOCR for low-confidence regions

        Returns:
            Dict with:
                - text_blocks: List of {text, bbox, confidence}
                - full_text: All extracted text concatenated
                - method: "tesseract" or "hybrid"
        """
        loop = asyncio.get_event_loop()

        # Primary: Tesseract OCR
        def _tesseract_ocr() -> dict[str, Any]:
            img = Image.open(image_path)

            # Get detailed data with bounding boxes and confidence
            data = pytesseract.image_to_data(
                img,
                output_type=pytesseract.Output.DICT
            )

            # Filter out empty/low-confidence detections
            text_blocks = []
            low_confidence_regions = []

            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if not text:
                    continue

                confidence = float(data['conf'][i])
                bbox = {
                    'x': data['left'][i],
                    'y': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                }

                block = {
                    'text': text,
                    'bbox': bbox,
                    'confidence': confidence,
                    'source': 'tesseract'
                }

                text_blocks.append(block)

                # Track low-confidence regions for EasyOCR fallback
                if confidence < 60.0:  # Threshold for "low confidence"
                    low_confidence_regions.append((bbox, i))

            return {
                'text_blocks': text_blocks,
                'low_confidence_regions': low_confidence_regions,
                'image': img
            }

        tesseract_result = await loop.run_in_executor(None, _tesseract_ocr)

        # Secondary: EasyOCR fallback for low-confidence regions
        if (use_fallback and
            self._easyocr_available and
            tesseract_result['low_confidence_regions']):

            easyocr_blocks = await self._easyocr_fallback(
                tesseract_result['image'],
                tesseract_result['low_confidence_regions']
            )

            # Merge results: replace low-confidence Tesseract with EasyOCR
            for easyocr_block in easyocr_blocks:
                tesseract_result['text_blocks'].append(easyocr_block)

            method = "hybrid"
        else:
            method = "tesseract"

        # Generate full text
        full_text = ' '.join([block['text'] for block in tesseract_result['text_blocks']])

        return {
            'text_blocks': tesseract_result['text_blocks'],
            'full_text': full_text,
            'method': method,
            'total_blocks': len(tesseract_result['text_blocks'])
        }

    async def _easyocr_fallback(
        self,
        image: Image.Image,
        low_confidence_regions: list[tuple[dict, int]]
    ) -> list[dict[str, Any]]:
        """Use EasyOCR on low-confidence regions.

        Args:
            image: PIL Image object
            low_confidence_regions: List of (bbox, index) tuples

        Returns:
            List of text blocks from EasyOCR
        """
        if not self._easyocr_reader:
            return []

        loop = asyncio.get_event_loop()
        easyocr_blocks = []

        for bbox, _ in low_confidence_regions:
            # Crop region
            x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
            # Add padding
            padding = 10
            crop_box = (
                max(0, x - padding),
                max(0, y - padding),
                x + w + padding,
                y + h + padding
            )
            cropped = image.crop(crop_box)

            # Run EasyOCR on cropped region
            def _easyocr_read() -> list:
                import numpy as np
                return self._easyocr_reader.readtext(np.array(cropped))

            results = await loop.run_in_executor(None, _easyocr_read)

            for (box, text, confidence) in results:
                # Adjust bounding box back to full image coordinates
                adjusted_bbox = {
                    'x': int(box[0][0]) + crop_box[0],
                    'y': int(box[0][1]) + crop_box[1],
                    'width': int(box[2][0] - box[0][0]),
                    'height': int(box[2][1] - box[0][1])
                }

                easyocr_blocks.append({
                    'text': text,
                    'bbox': adjusted_bbox,
                    'confidence': float(confidence) * 100,  # Convert to percentage
                    'source': 'easyocr'
                })

        return easyocr_blocks

    async def find_text(
        self,
        image_path: Path,
        search_text: str,
        case_sensitive: bool = False
    ) -> list[dict[str, Any]]:
        """Find specific text in image and return bounding boxes.

        Args:
            image_path: Path to image file
            search_text: Text to search for
            case_sensitive: Whether search should be case-sensitive

        Returns:
            List of matching text blocks with bounding boxes
        """
        ocr_result = await self.extract_text(image_path)

        matches = []
        for block in ocr_result['text_blocks']:
            text = block['text']
            if not case_sensitive:
                text = text.lower()
                search_text = search_text.lower()

            if search_text in text:
                matches.append(block)

        return matches
