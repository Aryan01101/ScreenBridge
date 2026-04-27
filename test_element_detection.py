#!/usr/bin/env python3
"""
Test script to verify element tree detection and structured output.

This script:
1. Captures a screenshot of your current screen
2. Processes it through ScreenProcessor (OCR + Element Tree)
3. Runs it through SentinelLayer (PII redaction + context detection)
4. Prints the structured dictionary that would be sent to LLMs
5. Saves the output to a JSON file for inspection

Usage:
    python test_element_detection.py
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from pprint import pprint

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from screenbridge.capture.manager import CaptureManager
from screenbridge.processor.screen_processor import ScreenProcessor
from screenbridge.sentinel.sentinel_layer import SentinelLayer
from screenbridge.core import Config


async def test_element_detection():
    """Test element tree detection and structured output."""

    print("=" * 80)
    print("ScreenBridge Element Detection Test")
    print("=" * 80)
    print()

    # Create test session directory
    test_session = Path.home() / ".screenbridge" / "test_sessions" / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    test_session.mkdir(parents=True, exist_ok=True)

    print(f"📁 Test session: {test_session}")
    print()

    # Initialize config
    config = Config()

    # Initialize subsystems
    print("🔧 Initializing subsystems...")
    capture_manager = CaptureManager(config=config, session_path=test_session)
    screen_processor = ScreenProcessor(config=config)
    sentinel_layer = SentinelLayer(config=config)

    await capture_manager.initialize()
    await screen_processor.initialize()
    await sentinel_layer.initialize(session_path=test_session)

    print("✅ All subsystems initialized")
    print()

    try:
        # Step 1: Capture screenshot
        print("📸 Capturing screenshot...")
        screenshot_metadata = await capture_manager.capture_screen(monitor=1)
        screenshot_path = Path(screenshot_metadata['screenshot_path'])

        print(f"   Screenshot saved: {screenshot_path}")
        print(f"   Resolution: {screenshot_metadata['resolution']['width']}x{screenshot_metadata['resolution']['height']}")
        print()

        # Step 2: Process screenshot
        print("🔍 Processing screenshot (OCR + Element Tree)...")
        summary = await screen_processor.process_screenshot(screenshot_path)

        print(f"   OCR Method: {summary['metadata']['ocr_method']}")
        print(f"   Text Blocks Found: {summary['metadata']['total_text_blocks']}")
        print(f"   Element Stats: {summary['metadata']['element_stats']}")
        print()

        # Step 3: Run through SentinelLayer
        print("🛡️  Running SentinelLayer checks...")
        sentinel_result = await sentinel_layer.evaluate(summary)

        print(f"   Decision: {sentinel_result['status']}")
        print(f"   Confidence: {sentinel_result['confidence']:.2f}")
        print(f"   Context Type: {sentinel_result['context_type']}")
        print(f"   Reason: {sentinel_result['reason']}")
        if sentinel_result['pii_found']:
            print(f"   PII Redacted: {sentinel_result['pii_found']}")
        print()

        # Step 4: Display Element Tree
        print("=" * 80)
        print("ELEMENT TREE (Flat Dictionary Structure)")
        print("=" * 80)
        print()

        element_tree = sentinel_result['redacted_summary']['element_tree']

        if 'error' in element_tree:
            print(f"❌ Error building element tree: {element_tree['error']}")
            print(f"   Message: {element_tree['message']}")
            print()
            print("⚠️  Make sure Accessibility permissions are enabled:")
            print("   System Preferences > Privacy & Security > Accessibility")
            print("   Add Terminal or your Python interpreter")
        else:
            print(f"Total Elements: {len(element_tree)}")
            print()

            # Print root element
            if "1" in element_tree:
                root = element_tree["1"]
                print("🪟 Root Window:")
                print(f"   ID: {root['id']}")
                print(f"   Type: {root['type']}")
                print(f"   Label: {root['label']}")
                print(f"   State: {root['state']}")
                if 'children' in root:
                    print(f"   Children: {len(root['children'])} elements")
                print()

            # Print sample of interactive elements
            interactive_elements = [
                e for e in element_tree.values()
                if e.get('type') in {'button', 'textfield', 'checkbox', 'link', 'menuitem'}
            ]

            if interactive_elements:
                print(f"🎯 Interactive Elements (showing first 10 of {len(interactive_elements)}):")
                print()

                for elem in interactive_elements[:10]:
                    print(f"   [{elem['id']}] {elem['type'].upper()}")
                    print(f"      Label: {elem['label']}")
                    print(f"      State: {elem['state']}")
                    if elem.get('bbox'):
                        bbox = elem['bbox']
                        print(f"      Position: ({bbox[0]}, {bbox[1]}) to ({bbox[2]}, {bbox[3]})")
                    if elem.get('parent'):
                        print(f"      Parent: {elem['parent']}")
                    print()

        # Step 5: Display OCR Results
        print("=" * 80)
        print("OCR TEXT BLOCKS (First 10)")
        print("=" * 80)
        print()

        text_blocks = sentinel_result['redacted_summary']['text_blocks']
        for i, block in enumerate(text_blocks[:10], 1):
            print(f"{i}. \"{block['text']}\"")
            print(f"   Confidence: {block['confidence']:.1f}%")
            print(f"   Source: {block['source']}")
            if block.get('bbox'):
                bbox = block['bbox']
                print(f"   Position: ({bbox['x']}, {bbox['y']}) - {bbox['width']}x{bbox['height']}")
            print()

        if len(text_blocks) > 10:
            print(f"... and {len(text_blocks) - 10} more text blocks")
            print()

        # Step 6: Display Summary
        print("=" * 80)
        print("HUMAN-READABLE SUMMARY")
        print("=" * 80)
        print()
        print(sentinel_result['redacted_summary']['summary'])
        print()

        # Step 7: Save full output to JSON
        output_file = test_session / "structured_output.json"

        # Prepare output (exclude some verbose fields for readability)
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "screenshot_path": str(screenshot_path),
            "resolution": screenshot_metadata['resolution'],
            "sentinel_decision": {
                "status": sentinel_result['status'],
                "confidence": sentinel_result['confidence'],
                "context_type": sentinel_result['context_type'],
                "reason": sentinel_result['reason'],
                "pii_found": sentinel_result['pii_found']
            },
            "element_tree": element_tree,
            "text_blocks": text_blocks,
            "summary": sentinel_result['redacted_summary']['summary'],
            "metadata": summary['metadata']
        }

        with output_file.open('w') as f:
            json.dump(output_data, f, indent=2)

        print("=" * 80)
        print(f"✅ Full output saved to: {output_file}")
        print("=" * 80)
        print()

        # Display what would be sent to LLM
        print("=" * 80)
        print("WHAT THE LLM WOULD RECEIVE")
        print("=" * 80)
        print()
        print("This is the privacy-safe structured summary (NO raw pixels):")
        print()
        print(json.dumps({
            "element_tree": element_tree,
            "summary": sentinel_result['redacted_summary']['summary'],
            "interactive_elements_count": len(interactive_elements) if not 'error' in element_tree else 0,
            "text_snippets": [b['text'] for b in text_blocks[:5]],
        }, indent=2))
        print()

    finally:
        # Cleanup
        await capture_manager.cleanup()
        await screen_processor.cleanup()
        await sentinel_layer.cleanup()

        print("🧹 Cleanup complete")


if __name__ == "__main__":
    print()
    print("⚠️  IMPORTANT: Make sure you have a window open that you want to test!")
    print()
    print("Starting in 3 seconds...")

    import time
    time.sleep(3)

    asyncio.run(test_element_detection())
