# ScreenBridge Testing Guide

## Quick Test: Element Detection

### Prerequisites

1. **Install dependencies:**
   ```bash
   pip install mss pillow pytesseract atomacos pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz pydantic
   ```

2. **Install Tesseract OCR:**
   ```bash
   brew install tesseract
   ```

3. **Enable Accessibility Permissions:**
   - Open **System Preferences** → **Privacy & Security** → **Accessibility**
   - Click the lock to make changes
   - Add **Terminal** (or your Python interpreter) to the list
   - Grant permission

### Running the Test

1. **Open a window you want to test** (e.g., Safari, VS Code, Finder)

2. **Run the test script:**
   ```bash
   cd /Users/laxus/Desktop/Projects/ScreenBridge
   python test_element_detection.py
   ```

3. **Wait 3 seconds** (script gives you time to focus the window)

4. **Check the output:**
   - Terminal will show element tree structure
   - JSON file saved to `~/.screenbridge/test_sessions/<timestamp>/structured_output.json`
   - Screenshot saved to `~/.screenbridge/test_sessions/<timestamp>/frames/0001.jpg`

### What You'll See

**Console Output:**
```
================================================================================
ScreenBridge Element Detection Test
================================================================================

📁 Test session: /Users/laxus/.screenbridge/test_sessions/2026-04-27_16-30-45

🔧 Initializing subsystems...
✅ All subsystems initialized

📸 Capturing screenshot...
   Screenshot saved: /Users/laxus/.screenbridge/.../0001.jpg
   Resolution: 1920x1080

🔍 Processing screenshot (OCR + Element Tree)...
   OCR Method: tesseract
   Text Blocks Found: 45
   Element Stats: {'total_elements': 87, 'interactive_elements': 23, 'max_depth': 5}

🛡️  Running SentinelLayer checks...
   Decision: SAFE
   Confidence: 1.00
   Context Type: None
   Reason: No sensitive context detected

================================================================================
ELEMENT TREE (Flat Dictionary Structure)
================================================================================

Total Elements: 87

🪟 Root Window:
   ID: 1
   Type: window
   Label: Safari
   State: focused
   Children: 12 elements

🎯 Interactive Elements (showing first 10 of 23):

   [1.1] BUTTON
      Label: Back
      State: enabled
      Position: (10, 50) to (40, 80)
      Parent: 1

   [1.2] BUTTON
      Label: Forward
      State: disabled
      Position: (45, 50) to (75, 80)
      Parent: 1

   [1.3] TEXTFIELD
      Label: google.com
      State: enabled
      Position: (100, 50) to (800, 80)
      Parent: 1

   ...
```

**JSON Output** (`structured_output.json`):
```json
{
  "timestamp": "2026-04-27T16:30:45.123456",
  "element_tree": {
    "1": {
      "id": "1",
      "type": "window",
      "label": "Safari",
      "state": "focused",
      "bbox": [0, 0, 1920, 1080],
      "children": ["1.1", "1.2", "1.3", ...]
    },
    "1.1": {
      "id": "1.1",
      "parent": "1",
      "type": "button",
      "label": "Back",
      "state": "enabled",
      "bbox": [10, 50, 40, 80]
    },
    ...
  },
  "text_blocks": [
    {
      "text": "Google",
      "bbox": {"x": 120, "y": 200, "width": 150, "height": 30},
      "confidence": 95.3,
      "source": "tesseract"
    },
    ...
  ],
  "summary": "Application: Safari. 23 interactive elements detected. Focused: Search field. Visible text: Google, Search, Images, News."
}
```

### Troubleshooting

**Error: "Could not access accessibility API"**
- Enable Accessibility permissions (see Prerequisites #3)
- Restart Terminal after enabling

**Error: "tesseract: command not found"**
- Install Tesseract: `brew install tesseract`

**Error: "No module named 'atomacos'"**
- Install dependencies: `pip install atomacos pyobjc-core pyobjc-framework-Cocoa`

**Empty element tree (0 elements)**
- Some apps don't expose accessibility info (games, some custom UIs)
- Try with Safari, Finder, or VS Code instead

**Low OCR accuracy**
- Try higher resolution screenshot
- Ensure text is clearly visible on screen
- Install EasyOCR for better results: `pip install easyocr torch`

### Testing Different Scenarios

**Test 1: Normal Application (Safari)**
```bash
# Open Safari, navigate to google.com
python test_element_detection.py
# Expected: SAFE, 20-50 elements, text blocks with "Google", "Search", etc.
```

**Test 2: Sensitive Context (Payment Page)**
```bash
# Open Safari, navigate to any checkout page
python test_element_detection.py
# Expected: WARN or HALT, context_type: "financial", keywords detected
```

**Test 3: PII Redaction**
```bash
# Open TextEdit, type your email and credit card number
python test_element_detection.py
# Expected: pii_found: {"email": 1, "credit_card": 1}, text redacted with [REDACTED]:EMAIL
```

**Test 4: Password Manager**
```bash
# Open 1Password, Bitwarden, or LastPass
python test_element_detection.py
# Expected: HALT, context_type: "password_manager"
```

### Next Steps

Once element detection is working:

1. **Review the JSON output** - Verify element IDs are hierarchical ("1", "1.1", "1.2.1")
2. **Check element types** - Look for buttons, textfields, checkboxes, links
3. **Validate OCR accuracy** - Compare extracted text with actual screen text
4. **Test SentinelLayer** - Navigate to payment page, verify HALT decision
5. **Inspect PII redaction** - Type sensitive data, verify it's redacted

### Understanding the Output

**Element Tree Structure:**
```
"1"       → Root window (Safari)
"1.1"     → Back button
"1.2"     → Forward button
"1.3"     → Address bar
"1.3.1"   → Text inside address bar
"1.4"     → Tab bar
"1.4.1"   → First tab
"1.4.2"   → Second tab
```

**This flat dictionary is what LLMs receive** - no raw pixels, just structured semantic data.

**Element fields:**
- `id`: Semantic hierarchical ID
- `type`: UI element type (button, textfield, window, etc.)
- `label`: User-visible text
- `state`: enabled/disabled/focused
- `bbox`: [x1, y1, x2, y2] screen coordinates
- `parent`: Parent element ID
- `children`: List of child element IDs

### Performance Notes

- Screenshot capture: ~50ms
- OCR (Tesseract): ~500ms-2s (depends on resolution)
- Element tree building: ~100-300ms (depends on UI complexity)
- **Total processing time: ~1-3 seconds per frame**

For real-time usage, consider:
- Caching element tree when UI hasn't changed
- Running OCR only on changed regions
- Using EasyOCR only for low-confidence areas

---

**Questions or Issues?**
- Check logs in `~/.screenbridge/test_sessions/`
- Review `sentinel_audit.json` for safety decisions
- Open an issue on GitHub with test output attached
