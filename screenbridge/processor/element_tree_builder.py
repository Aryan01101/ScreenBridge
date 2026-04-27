"""Element tree builder using macOS accessibility APIs."""

from __future__ import annotations

import asyncio
import sys
from typing import Any, Optional

if sys.platform == "darwin":
    import atomacos


class ElementTreeBuilder:
    """Builds hierarchical element tree with semantic IDs.

    Uses macOS Accessibility APIs (atomacos) to create a structured
    representation of all interactive UI elements on screen.

    Element ID format: Hierarchical semantic IDs
    - Root window: "1"
    - Top-level children: "1.1", "1.2", "1.3"
    - Nested children: "1.1.1", "1.2.1", etc.
    """

    def __init__(self, config: Any) -> None:
        """Initialize element tree builder.

        Args:
            config: ScreenBridge configuration object
        """
        self.config = config
        self._current_tree: dict[str, Any] = {}
        self._id_counter = 0

    async def initialize(self) -> None:
        """Initialize accessibility API access."""
        if sys.platform != "darwin":
            raise RuntimeError("ElementTreeBuilder only supports macOS (darwin) currently")

    async def cleanup(self) -> None:
        """Cleanup resources."""
        self._current_tree = {}

    async def build_tree(
        self,
        app_name: Optional[str] = None,
        max_depth: Optional[int] = None
    ) -> dict[str, Any]:
        """Build element tree for active application.

        Args:
            app_name: Specific application name, or None for frontmost app
            max_depth: Maximum tree depth (None = unlimited)

        Returns:
            Flat dict of elements keyed by semantic ID:
            {
                "1": {
                    "id": "1",
                    "type": "window",
                    "label": "VS Code",
                    "children": ["1.1", "1.2"],
                    "state": "focused",
                    "bbox": [0, 0, 1920, 1080]
                },
                "1.1": {
                    "id": "1.1",
                    "parent": "1",
                    "type": "button",
                    "label": "Run",
                    ...
                }
            }
        """
        loop = asyncio.get_event_loop()

        # Get frontmost application in thread pool
        def _get_app() -> Any:
            if app_name:
                return atomacos.getAppRefByBundleId(app_name)
            else:
                # Get system-wide accessibility object
                return atomacos.NativeUIElement()

        try:
            app_ref = await loop.run_in_executor(None, _get_app)
        except Exception as e:
            # Accessibility not enabled or app not found
            return {
                "error": str(e),
                "message": "Could not access accessibility API. Enable in System Preferences > Privacy & Security > Accessibility"
            }

        # Build tree recursively
        self._current_tree = {}
        self._id_counter = 0

        root_id = "1"
        max_depth_setting = max_depth or getattr(self.config, "max_depth", None)

        def _build_recursive(
            element: Any,
            parent_id: Optional[str],
            depth: int
        ) -> Optional[str]:
            """Recursively build element tree.

            Returns:
                Element ID if successful, None if skipped
            """
            # Check depth limit
            if max_depth_setting and depth > max_depth_setting:
                return None

            try:
                # Generate semantic ID
                if parent_id is None:
                    element_id = root_id
                else:
                    self._id_counter += 1
                    child_index = len([k for k in self._current_tree.keys()
                                      if k.startswith(f"{parent_id}.")])
                    element_id = f"{parent_id}.{child_index + 1}"

                # Extract element attributes
                role = getattr(element, 'AXRole', 'unknown')
                title = getattr(element, 'AXTitle', '')
                value = getattr(element, 'AXValue', '')
                description = getattr(element, 'AXDescription', '')

                # Determine label (prefer title, fallback to description/value)
                label = title or description or value or f"<{role}>"

                # Get position and size
                try:
                    position = getattr(element, 'AXPosition', None)
                    size = getattr(element, 'AXSize', None)
                    if position and size:
                        bbox = [
                            int(position[0]),
                            int(position[1]),
                            int(position[0] + size[0]),
                            int(position[1] + size[1])
                        ]
                    else:
                        bbox = None
                except:
                    bbox = None

                # Get state
                focused = getattr(element, 'AXFocused', False)
                enabled = getattr(element, 'AXEnabled', True)

                if focused:
                    state = "focused"
                elif not enabled:
                    state = "disabled"
                else:
                    state = "enabled"

                # Store element data
                element_data = {
                    "id": element_id,
                    "type": role.replace("AX", "").lower() if role.startswith("AX") else role,
                    "label": str(label)[:100],  # Truncate long labels
                    "state": state,
                    "bbox": bbox,
                }

                if parent_id:
                    element_data["parent"] = parent_id

                # Get children
                try:
                    children_elements = getattr(element, 'AXChildren', [])
                    if children_elements:
                        child_ids = []
                        for child in children_elements:
                            child_id = _build_recursive(child, element_id, depth + 1)
                            if child_id:
                                child_ids.append(child_id)

                        if child_ids:
                            element_data["children"] = child_ids
                except:
                    pass  # No children or inaccessible

                self._current_tree[element_id] = element_data
                return element_id

            except Exception:
                # Skip inaccessible elements
                return None

        # Build tree from root
        await loop.run_in_executor(None, lambda: _build_recursive(app_ref, None, 0))

        return self._current_tree

    async def find_element_by_label(
        self,
        label: str,
        case_sensitive: bool = False
    ) -> Optional[dict[str, Any]]:
        """Find element by label text.

        Args:
            label: Text to search for in element labels
            case_sensitive: Whether search should be case-sensitive

        Returns:
            Element dict if found, None otherwise
        """
        search_label = label if case_sensitive else label.lower()

        for element_id, element_data in self._current_tree.items():
            element_label = element_data.get("label", "")
            if not case_sensitive:
                element_label = element_label.lower()

            if search_label in element_label:
                return element_data

        return None

    async def get_element_by_id(self, element_id: str) -> Optional[dict[str, Any]]:
        """Get element by its semantic ID.

        Args:
            element_id: Semantic ID (e.g., "1.2.3")

        Returns:
            Element dict if found, None otherwise
        """
        return self._current_tree.get(element_id)

    async def get_interactive_elements(self) -> list[dict[str, Any]]:
        """Get only interactive elements (buttons, inputs, links, etc.).

        Returns:
            List of interactive element dicts
        """
        interactive_types = {
            "button", "textfield", "textarea", "checkbox", "radiobutton",
            "combobox", "link", "menuitem", "tab", "slider", "switch"
        }

        return [
            element for element in self._current_tree.values()
            if element.get("type") in interactive_types
        ]

    def get_current_tree(self) -> dict[str, Any]:
        """Get the current element tree.

        Returns:
            Current tree dict
        """
        return self._current_tree

    def get_tree_stats(self) -> dict[str, int]:
        """Get statistics about current tree.

        Returns:
            Dict with total_elements, interactive_elements, max_depth
        """
        total = len(self._current_tree)

        interactive_types = {
            "button", "textfield", "textarea", "checkbox", "radiobutton",
            "combobox", "link", "menuitem", "tab", "slider", "switch"
        }
        interactive = sum(
            1 for e in self._current_tree.values()
            if e.get("type") in interactive_types
        )

        max_depth = max(
            (len(eid.split('.')) for eid in self._current_tree.keys()),
            default=0
        )

        return {
            "total_elements": total,
            "interactive_elements": interactive,
            "max_depth": max_depth
        }
