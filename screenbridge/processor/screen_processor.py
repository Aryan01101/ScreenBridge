"""Screen processor for OCR and element tree construction."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Optional

from screenbridge.processor.ocr_engine import OCREngine
from screenbridge.processor.element_tree_builder import ElementTreeBuilder


class ScreenProcessor:
    """Processes screenshots into structured summaries.

    Coordinates OCR extraction, element tree building, and diff generation
    to create privacy-safe structured summaries for LLMs.
    """

    def __init__(self, config: Any) -> None:
        """Initialize screen processor.

        Args:
            config: ScreenBridge configuration object
        """
        self.config = config
        self._ocr_engine: Optional[OCREngine] = None
        self._element_builder: Optional[ElementTreeBuilder] = None
        self._previous_state: Optional[dict[str, Any]] = None

    async def initialize(self) -> None:
        """Initialize OCR engines and element detectors."""
        self._ocr_engine = OCREngine(self.config)
        self._element_builder = ElementTreeBuilder(self.config)

        await self._ocr_engine.initialize()
        await self._element_builder.initialize()

    async def cleanup(self) -> None:
        """Cleanup processor resources."""
        if self._ocr_engine:
            await self._ocr_engine.cleanup()
        if self._element_builder:
            await self._element_builder.cleanup()

    async def process_screenshot(
        self,
        screenshot_path: Path,
        app_name: Optional[str] = None
    ) -> dict[str, Any]:
        """Process screenshot into structured summary.

        This is the core privacy buffer - raw screenshot never leaves this function.
        Only the structured JSON summary is returned.

        Args:
            screenshot_path: Path to screenshot file (will be processed locally)
            app_name: Specific application name, or None for auto-detect

        Returns:
            Structured summary dict with:
                - element_tree: Hierarchical UI elements
                - text_blocks: OCR-extracted text with positions
                - summary: Human-readable description
                - diff: Changes from previous state (if available)
                - metadata: Processing stats
        """
        if not self._ocr_engine or not self._element_builder:
            raise RuntimeError("ScreenProcessor not initialized")

        # Run OCR and element tree building in parallel
        ocr_task = self._ocr_engine.extract_text(screenshot_path)
        tree_task = self._element_builder.build_tree(app_name)

        ocr_result, element_tree = await asyncio.gather(ocr_task, tree_task)

        # Generate human-readable summary
        summary = self._generate_summary(element_tree, ocr_result)

        # Calculate diff if we have previous state
        diff = None
        if self._previous_state:
            diff = await self._calculate_diff(
                self._previous_state,
                {"element_tree": element_tree, "text_blocks": ocr_result['text_blocks']}
            )

        # Build structured output
        current_state = {
            "element_tree": element_tree,
            "text_blocks": ocr_result['text_blocks'],
            "full_text": ocr_result['full_text'],
            "summary": summary,
            "diff": diff,
            "metadata": {
                "ocr_method": ocr_result['method'],
                "total_text_blocks": ocr_result['total_blocks'],
                "element_stats": self._element_builder.get_tree_stats()
            }
        }

        # Store for next diff
        self._previous_state = current_state.copy()

        return current_state

    def _generate_summary(
        self,
        element_tree: dict[str, Any],
        ocr_result: dict[str, Any]
    ) -> str:
        """Generate human-readable summary from element tree and OCR.

        Args:
            element_tree: Element tree dict
            ocr_result: OCR extraction result

        Returns:
            Human-readable summary string
        """
        if "error" in element_tree:
            return f"Screen capture active. Accessibility API unavailable: {element_tree['error']}"

        # Get root window info
        root = element_tree.get("1", {})
        window_label = root.get("label", "Unknown Application")

        # Count interactive elements
        interactive_count = sum(
            1 for e in element_tree.values()
            if e.get("type") in {
                "button", "textfield", "checkbox", "link", "menuitem", "tab"
            }
        )

        # Get focused element if any
        focused = next(
            (e for e in element_tree.values() if e.get("state") == "focused"),
            None
        )

        parts = [f"Application: {window_label}"]

        if interactive_count > 0:
            parts.append(f"{interactive_count} interactive elements detected")

        if focused:
            parts.append(f"Focused: {focused.get('label', focused.get('type'))}")

        # Add key text snippets
        if ocr_result['total_blocks'] > 0:
            # Sample first few high-confidence text blocks
            key_text = [
                block['text'] for block in ocr_result['text_blocks'][:5]
                if block.get('confidence', 0) > 75
            ]
            if key_text:
                parts.append(f"Visible text: {', '.join(key_text)}")

        return ". ".join(parts) + "."

    async def _calculate_diff(
        self,
        previous: dict[str, Any],
        current: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate element-level diff between states.

        Args:
            previous: Previous state dict
            current: Current state dict

        Returns:
            Diff dict with added, removed, changed elements
        """
        loop = asyncio.get_event_loop()

        def _compute_diff() -> dict[str, Any]:
            prev_tree = previous.get("element_tree", {})
            curr_tree = current.get("element_tree", {})

            prev_ids = set(prev_tree.keys())
            curr_ids = set(curr_tree.keys())

            # Element changes
            added_ids = curr_ids - prev_ids
            removed_ids = prev_ids - curr_ids
            common_ids = prev_ids & curr_ids

            # Check for state changes in common elements
            changed = []
            for eid in common_ids:
                prev_elem = prev_tree[eid]
                curr_elem = curr_tree[eid]

                # Check state change
                if prev_elem.get("state") != curr_elem.get("state"):
                    changed.append({
                        "id": eid,
                        "label": curr_elem.get("label"),
                        "change_type": "state",
                        "old_state": prev_elem.get("state"),
                        "new_state": curr_elem.get("state")
                    })

                # Check label change (text content changed)
                if prev_elem.get("label") != curr_elem.get("label"):
                    changed.append({
                        "id": eid,
                        "change_type": "label",
                        "old_label": prev_elem.get("label"),
                        "new_label": curr_elem.get("label")
                    })

            return {
                "added_elements": [
                    {
                        "id": eid,
                        "type": curr_tree[eid].get("type"),
                        "label": curr_tree[eid].get("label")
                    }
                    for eid in added_ids
                ],
                "removed_elements": [
                    {
                        "id": eid,
                        "type": prev_tree[eid].get("type"),
                        "label": prev_tree[eid].get("label")
                    }
                    for eid in removed_ids
                ],
                "changed_elements": changed,
                "has_changes": bool(added_ids or removed_ids or changed)
            }

        return await loop.run_in_executor(None, _compute_diff)

    async def find_element_by_label(self, label: str) -> Optional[dict[str, Any]]:
        """Find element by label text.

        Args:
            label: Text to search for

        Returns:
            Element dict if found, None otherwise
        """
        if not self._element_builder:
            return None

        return await self._element_builder.find_element_by_label(label)

    async def find_text_on_screen(
        self,
        screenshot_path: Path,
        search_text: str
    ) -> list[dict[str, Any]]:
        """Find specific text on screen and return bounding boxes.

        Args:
            screenshot_path: Path to screenshot
            search_text: Text to find

        Returns:
            List of matching text blocks with positions
        """
        if not self._ocr_engine:
            return []

        return await self._ocr_engine.find_text(screenshot_path, search_text)
