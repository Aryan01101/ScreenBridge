# ScreenBridge PRD

**Type:** Product Requirements Document
**Version:** 1.0
**Date:** April 2026
**Status:** Active - Phase 1 Development (40% Complete)

> "The open, privacy-first middleware that gives any LLM eyes and hands on your desktop — with a built-in safety layer that stops the moment it sees something sensitive."

---

## 🚧 Development Status (Updated: April 27, 2026)

**Current Phase:** Phase 1 - Core Engine
**Progress:** 40% Complete (13/32 tasks)
**GitHub:** [https://github.com/Aryan01101/ScreenBridge](https://github.com/Aryan01101/ScreenBridge)
**Latest Commit:** `b001dac` - SentinelLayer implementation complete

### ✅ Completed Modules

#### 1. ScreenReader Module (Vision Layer) - 100% Complete
- ✅ Screenshot capture with `mss` (async, JPEG compression)
- ✅ Tesseract OCR with bounding boxes
- ✅ EasyOCR fallback for low-confidence regions
- ✅ Element tree builder using `atomacos` (macOS Accessibility API)
- ✅ Hierarchical element IDs (1, 1.1, 1.2.3) for robust targeting
- ✅ Element-level diff engine with state change tracking
- ✅ Session-based JPEG storage with metadata
- ✅ Privacy buffer: Raw screenshots never leave ScreenProcessor

**Key Achievement:** ScreenBridge can now see and understand desktop UIs without sending pixels to cloud.

#### 2. SentinelLayer Module (Safety Guardian) - 100% Complete
- ✅ PII redaction (email, credit cards, phone, SSN, API keys)
- ✅ Context detection (financial, healthcare, auth, password managers)
- ✅ Hybrid detection: URL patterns + OCR keywords + UI elements
- ✅ HALT/WARN/SAFE decision pipeline with confidence thresholds
- ✅ JSON audit logging per session
- ✅ Configurable sensitivity levels (paranoid/balanced/relaxed)
- ✅ Luhn algorithm for credit card validation
- ✅ Confidence scoring per detection type

**Key Achievement:** PII is redacted before any summary reaches an LLM, and sensitive screens trigger HALTs.

### 🔄 In Progress

- 🔄 Canonical tool format definition for LLM communication
- 🔄 Testing infrastructure and validation scripts

### ⏳ Remaining for Phase 1 (19 tasks)

**LLM Integration (4 tasks):**
- LLM connectors: Claude, OpenAI, Gemini, Ollama
- Canonical tool format translation
- Agentic loop manager
- MCP server adapter

**Action Execution (5 tasks):**
- Element-based actions (click_element, type_into_element)
- Coordinate fallback (click, type, scroll, hotkey)
- Auto-upgrade layer (coordinates → elements)
- CLI confirmation prompts
- Rate limiting (2/sec, 50/task, backoff)

**Infrastructure (10 tasks):**
- Security manager (audit logging, confirmations)
- Storage manager (retention policies, disk monitoring)
- High-level async API integration
- Debug mode (logs, bounding boxes, slow-mo)
- Test suite (unit + integration with Playwright)
- Comprehensive documentation

### 📊 Progress Tracking

```
Phase 1 Progress: ████████░░░░░░░░░░░░ 40%

Completed:
├── Project scaffolding ✓
├── ScreenReader module ✓
│   ├── Screenshot capture ✓
│   ├── OCR (Tesseract + EasyOCR) ✓
│   ├── Element tree builder ✓
│   └── Diff engine ✓
└── SentinelLayer module ✓
    ├── PII redaction ✓
    ├── Context detection ✓
    ├── HALT/WARN/SAFE pipeline ✓
    └── Audit logging ✓

Remaining:
├── LLM connectors ⏳
├── Action executor ⏳
├── Agentic loop ⏳
├── Security manager ⏳
├── Storage manager ⏳
├── MCP server ⏳
└── Testing & docs ⏳
```

### 🎯 Next Milestone

**Target:** End-to-end demo working
**Goal:** `bridge.run("Click Spotify icon")` executes successfully
**ETA:** ~10-15 hours of development

**Critical path:**
1. Implement Claude connector (LLM communication)
2. Build ActionExecutor (element-based click/type)
3. Wire agentic loop (capture → process → sentinel → LLM → execute)
4. Add user confirmations for destructive actions

---

## Table of Contents

1. [Vision & Core Concept](#1-vision--core-concept)
2. [How ScreenBridge Works](#2-how-screenbridge-works)
3. [Technical Architecture](#3-technical-architecture)
4. [Technology Stack](#4-technology-stack)
5. [Module Structure & Developer API](#5-module-structure--developer-api)
6. [Use Cases & Utilities](#6-use-cases--utilities)
7. [Market Analysis & Competitive Landscape](#7-market-analysis--competitive-landscape)
8. [Business Model](#8-business-model)
9. [Development Roadmap](#9-development-roadmap)
10. [Research Prompt](#10-research-prompt)
11. [Summary & Strategic Positioning](#11-summary--strategic-positioning)

---

## 1. Vision & Core Concept

### 1.1 What Is ScreenBridge?

ScreenBridge is an open-source, privacy-first middleware SDK that acts as the universal translation layer between any Large Language Model (LLM) and a user's desktop screen. It gives any LLM — Claude, GPT-4, Gemini, or a local model — the ability to see what is on screen, understand it, and take actions, without ever exposing raw screen data to the cloud.

ScreenBridge is not an AI assistant. It is not tied to any specific LLM. It is infrastructure — the layer that products like Lumina and enterprise automation tools are built on top of.

**Core Philosophy:** Raw screenshots stay on the user's machine. Only structured summaries — what is on screen, not how it looks — are ever sent to an LLM. The LLM sees meaning, not pixels.

### 1.2 The Problem It Solves

Despite rapid AI advancement, there is no open, cross-platform, LLM-agnostic way to give an AI the ability to interact with a desktop. Existing solutions are either:

- **Platform-locked:** Mac-only, Windows-only, or Chrome-only
- **LLM-locked:** Tied to Anthropic, OpenAI, or a specific vendor
- **Privacy-unsafe:** Send raw screenshots directly to cloud APIs
- **Not extensible:** Closed tools with no SDK for developers to build on
- **Missing safety layers:** No automatic detection of sensitive screen contexts

### 1.3 The Separation of Concerns

ScreenBridge is deliberately separated from Lumina, the AI companion product that uses it.

| Layer | Product | Responsibility |
|---|---|---|
| Infrastructure | ScreenBridge | Screen capture, summarisation, action execution, safety detection, LLM communication |
| Application | Lumina | Teaching, guiding, companionship, user experience |
| Application | Any 3rd party | Any product built on ScreenBridge's SDK |

Lumina is ScreenBridge's flagship consumer, not its identity. This mirrors how Stripe is infrastructure that thousands of products use — Stripe is not itself a shop.

---

## 2. How ScreenBridge Works

### 2.1 The Agentic Loop

ScreenBridge's core mechanic is a continuous perception-action loop. The LLM never controls the screen directly — it calls tools that ScreenBridge exposes, which in turn interact with the desktop.

**Example loop — "Order me a standing desk from Officeworks":**

```
Round 1:
  ScreenBridge captures screen
  Summarises: "User is on Chrome. New tab page visible."
  Sends summary to LLM
  LLM responds: "Navigate to officeworks.com.au"
  ScreenBridge executes: opens URL

Round 2:
  Summarises: "Officeworks homepage. Search bar visible top centre."
  LLM responds: "Click search bar, type 'standing desk'"
  ScreenBridge executes

Round 3:
  Summarises: "Search results. 12 products listed."
  LLM responds: "Click the first result"
  ScreenBridge executes

Round 4:
  Summarises: "Product page. Price $349. Add to Cart button visible."
  LLM responds: "Click Add to Cart"
  ScreenBridge executes

Round 5: HALT — Sensitive Context Detected
  Summarises: "Checkout page. Credit card fields visible."
  SentinelLayer fires: FINANCIAL CONTEXT
  ScreenBridge does NOT send to LLM
  Returns to user: "Payment page reached. Please complete this step yourself."
```

### 2.2 The Privacy Buffer — The Core Innovation

Instead of sending raw screenshots to the cloud, ScreenBridge processes screen data locally and sends only a structured JSON summary.

**What gets sent to the LLM instead of a raw image:**

```json
{
  "timestamp": "2026-04-01T10:42:00",
  "active_window": "Visual Studio Code",
  "element_tree": {
    "1": {
      "id": "1",
      "type": "window",
      "label": "Visual Studio Code",
      "children": ["1.1", "1.2", "1.3"]
    },
    "1.1": {
      "id": "1.1",
      "parent": "1",
      "type": "text_editor",
      "content": "def hello_world():",
      "region": [120, 200, 800, 600],
      "state": "focused"
    },
    "1.2": {
      "id": "1.2",
      "parent": "1",
      "type": "button",
      "label": "Run",
      "region": [10, 50, 60, 70],
      "state": "enabled"
    },
    "1.3": {
      "id": "1.3",
      "parent": "1",
      "type": "terminal",
      "content": "$ python main.py",
      "region": [120, 620, 800, 900],
      "state": "visible"
    }
  },
  "text_blocks": ["def hello_world():", "    print('Hello')", "Run", "File", "Edit"],
  "summary": "VS Code open with a Python file (element 1.1). Run button available (element 1.2). Terminal visible below (element 1.3). No errors detected.",
  "sensitivity": "SAFE"
}
```

### 2.3 The SentinelLayer — Safety Detection

The SentinelLayer runs entirely locally, before any data reaches an LLM. It classifies the screen context and issues HALT, WARN, or SAFE decisions. It is a local rule engine combined with lightweight on-device pattern matching.

| Sensitive Context | Detection Method | Action |
|---|---|---|
| Financial pages (checkout, banking, crypto) | URL patterns + keyword OCR | HALT — stop loop, notify user |
| Healthcare / medical records | Keyword OCR + field labels | HALT — stop loop, notify user |
| Authentication screens (login, 2FA) | Field type detection + keywords | HALT — stop loop, notify user |
| Personal documents (passport, tax, ID) | Document structure + keywords | HALT — stop loop, notify user |
| Password manager screens | App name + field detection | HALT — stop loop, notify user |
| Personal emails / DMs | App context + content signals | WARN — ask user to confirm |

### 2.4 Privacy Tiers

| Tier | What Goes to LLM | Use Case |
|---|---|---|
| Full | Raw screenshot | Maximum accuracy, user fully trusts cloud |
| Summarised (Default) | Structured JSON only | Best balance of privacy and accuracy |
| Redacted | JSON with PII automatically stripped | Finance, healthcare, regulated enterprise |
| Offline | Nothing — local LLM only (Ollama) | Air-gapped, fully private deployments |

---

## 3. Technical Architecture

### 3.1 The Four Core Modules

#### Module 1 — ScreenReader (Vision Layer)

The perception engine. Responsible for capturing the screen and transforming raw pixels into structured, LLM-readable information.

- Screen capture via `mss` (cross-platform, fast)
- OCR via EasyOCR + Tesseract (extracts all visible text and positions)
- Element detection via OpenCV + ONNX (buttons, inputs, menus, dialogs)
- UI tree access via pywinauto (Windows), pyobjc/appscript (macOS), AT-SPI (Linux)
- Diff engine: compares consecutive frames, sends only what changed
- Raw screenshots stored locally only — never sent to cloud

#### Module 2 — SentinelLayer (Safety)

The privacy and safety guardian. Runs entirely on-device with no cloud dependency.

- Local rule engine with configurable sensitivity categories
- Lightweight local classification model for ambiguous contexts
- PII redaction pass (emails, credit cards, phone numbers, passwords)
- Full audit log of every detection event
- Enterprise-configurable: organisations can add custom rules

#### Module 3 — LLMBridge (Connector Layer)

The LLM-agnostic communication layer. Handles all communication with external AI models.

- Connectors for: Claude (Anthropic SDK), GPT-4 (OpenAI SDK), Gemini (Google SDK), local models via Ollama
- MCP (Model Context Protocol) server implementation for native Claude Desktop integration
- OpenAI-compatible tool-calling wrapper for GPT-based integrations
- Manages agentic loop state: step count, goal tracking, history, termination conditions
- Formats structured summaries into optimal LLM prompts

#### Module 4 — ActionExecutor

The hands. Executes actions on screen as instructed by the LLM.

- Element-based actions (primary): `click_element(element_id)`, `type_into_element(element_id, text)`
- Coordinate-based actions (fallback): `click(x, y)`, `type(text)`, `scroll(direction, amount)`, `hotkey(*keys)`
- Auto-upgrade layer: old coordinate calls internally attempt element resolution first
- Cross-platform unified API over pyautogui (all platforms) + platform-native backends
- Confirmation prompts for irreversible actions (delete, send, submit, purchase)
- Rate limiting to prevent runaway execution
- Full action log for debugging and compliance

#### Module 5 — ElementTreeBuilder

The structural understanding layer. Builds a hierarchical representation of all interactive elements on screen.

- Assigns unique semantic IDs to every interactive element (1, 1.1, 1.2, 2, 2.1, etc.)
- Hybrid detection: Accessibility APIs first (pywinauto/Windows, pyobjc/macOS, AT-SPI/Linux), vision-based fallback (OpenCV + ONNX) for inaccessible UIs
- Tracks parent-child relationships and element hierarchy for contextual understanding
- Enables resolution-independent action targeting (element IDs work across window resizes)
- Provides semantic labels, types, states, and bounding regions for each element
- Falls back to coordinate-based targeting for canvas apps, games, and non-accessible interfaces

#### Module 6 — StorageManager

The disk space and retention guardian. Ensures local storage does not exhaust system resources.

- Continuous disk space monitoring with configurable thresholds
- Auto-deletion of sessions older than N days (default: 7 days, user-configurable)
- Graceful degradation when disk space is low (e.g., reduce screenshot quality, skip redundant frames)
- Consolidates retention policy logic from retention_policy.json into active management
- User notifications when storage limits are approached
- Enterprise-configurable retention policies for compliance (e.g., "delete all data after 24 hours")

### 3.2 Vision Layer Deep Dive

```
Layer 1 — Static Snapshot (per frame)
├── OCR           → all visible text + bounding box coordinates
├── OpenCV        → UI element regions (buttons, inputs, menus, dialogs)
└── UI tree       → accessible element names, types, states

Layer 2 — Temporal Understanding (across frames)
├── Diff engine   → what meaningfully changed since last frame
└── UI-JEPA*      → user intent prediction from action sequences
                    (*for Lumina use case — user-driven sessions)

Layer 3 — Safety Pass
└── SentinelLayer → HALT / WARN / SAFE classification

Output: Enriched Intent Summary JSON → LLMBridge
```

### 3.3 UI-JEPA & V-JEPA — Research Model Integration

#### V-JEPA 2 (Meta)

V-JEPA 2 is Meta's world model trained on over 1 million hours of video. For ScreenBridge, its relevance is limited and specific:

- Meaningful change detection: distinguishes a real UI change from a loading animation
- Action outcome prediction: predicts what the screen will look like after an action
- Not suitable for: reading text, identifying UI elements, or understanding app context

V-JEPA 2 is an optional enhancement, not a core dependency. Offered as an opt-in module for users with capable hardware.

#### UI-JEPA (Apple Research)

UI-JEPA is a framework developed by Apple researchers specifically for understanding user intent from sequences of UI interactions.

**Key Result:** UI-JEPA outperforms GPT-4 Turbo and Claude 3.5 Sonnet by 10.0% and 7.2% respectively on UI intent understanding tasks, while achieving a 50.5x reduction in computational cost and 6.6x improvement in latency.

Critical distinction: UI-JEPA predicts what a human user is trying to accomplish by watching their actions. It is a passive observer of human behaviour — not an agent controller.

| Scenario | UI-JEPA Applicable? | Why |
|---|---|---|
| User is manually using Figma — Lumina watches | YES | UI-JEPA watches human actions and predicts intent |
| ScreenBridge agent is controlling the screen | NO | No human actions to observe — agent is driving |
| Lumina detects user confusion proactively | YES | UI-JEPA detects hesitation patterns in action sequences |

> **Note:** As of early 2026, Apple has released the UI-JEPA research code and datasets but NOT the trained model weights. Options: train from scratch on Apple's released datasets, or implement the architectural pattern with Phi-3 as the LM decoder.

---

## 4. Technology Stack

### 4.1 Core Stack

| Layer | Technology | Purpose |
|---|---|---|
| Screen Capture | mss, Pillow | Cross-platform screenshot capture |
| OCR | EasyOCR + Tesseract | Text extraction from screen |
| Element Detection | OpenCV + YOLO/ONNX | UI element region detection |
| UI Tree (Windows) | pywinauto | Native Win32/WPF element access |
| UI Tree (macOS) | pyobjc / appscript | macOS Accessibility API |
| UI Tree (Linux) | AT-SPI | Linux accessibility layer |
| Action Execution | pyautogui | Cross-platform mouse/keyboard control |
| Sensitivity Detection | Local rules + regex + small local model | On-device safety classification |
| Claude Connector | anthropic Python SDK | MCP + direct API |
| OpenAI Connector | openai Python SDK | GPT-4 tool calling |
| Gemini Connector | google-generativeai | Gemini integration |
| Local LLM Connector | ollama Python client | Fully offline mode |
| MCP Server | mcp Python SDK | MCP protocol implementation |
| Local Storage | Filesystem + SQLite | Screenshots + session metadata |
| Config | TOML / JSON | User and enterprise configuration |
| Packaging | uv + pyproject.toml + PyPI | Distribution |

### 4.2 Developer Requirements

- Python 3.10+
- `pip install screenbridge`
- API key for chosen LLM, or Ollama installed for fully local mode

```python
# Minimal working integration — 4 lines:
from screenbridge import ScreenBridge, ClaudeConnector
bridge = ScreenBridge(llm=ClaudeConnector(api_key="..."))
bridge.run("Open Spotify and play my liked songs")
```

### 4.3 End User Requirements

- Windows 10/11, macOS 12+, or Ubuntu 20+
- Python 3.10+ (or bundled installer hides this entirely)
- 4GB RAM minimum, 8GB recommended
- LLM API key (Claude, GPT, etc.) or Ollama for fully local mode
- ~500MB disk space

### 4.4 Enterprise Requirements

- Python runtime or Docker container
- Outbound network access to LLM API (or fully on-prem with local LLM)
- Admin rights for screen capture permissions (macOS requires Accessibility permission grant)
- Config file for custom sensitivity rules and compliance policies

---

## 5. Module Structure & Developer API

### 5.1 Package Layout

```
screenbridge/
├── capture/        ← Screenshot capture, local storage, retention policy
├── processor/      ← OCR, element detection, UI tree parsing, diff engine
├── redactor/       ← PII stripping (emails, credit cards, phone numbers)
├── summariser/     ← Combines processor outputs into structured JSON
├── sentinel/       ← Sensitivity detection, HALT/WARN/SAFE decisions
├── transport/      ← Sends summaries to LLM, receives action instructions
├── executor/       ← Executes click/type/scroll/hotkey actions
├── security/       ← Permission tiers, audit log, action confirmation
├── connectors/
│   ├── claude.py   ← Anthropic SDK + MCP server
│   ├── openai.py   ← OpenAI tool calling
│   ├── gemini.py   ← Google Generative AI
│   └── ollama.py   ← Local LLM (fully offline)
└── plugins/        ← Extension interface for Lumina and 3rd party apps
```

### 5.2 MCP Server Implementation

ScreenBridge exposes its capabilities as an MCP server, making it natively usable in Claude Desktop and any MCP-compatible LLM interface.

```python
# Core tools exposed via MCP:
@app.list_tools()
async def list_tools():
    return [
        # Screen Understanding
        Tool(name="screenshot",           description="Capture and summarise current screen state with hierarchical element tree"),
        Tool(name="get_element_tree",     description="Return hierarchical element tree with semantic IDs"),
        Tool(name="get_active_window",    description="Return name of currently focused application"),
        Tool(name="find_text",            description="Find and return position of text on screen via OCR"),
        Tool(name="find_element_by_label",description="Search for element by label/text and return its element ID"),

        # Element-Based Actions (Primary)
        Tool(name="click_element",        description="Click an element by its semantic ID (e.g., '1.2')"),
        Tool(name="type_into_element",    description="Type text into a specific element by ID"),

        # Coordinate-Based Actions (Fallback for canvas/games/inaccessible UIs)
        Tool(name="click",                description="Click at screen coordinates (x, y) — auto-upgrades to element-based when possible"),
        Tool(name="type_text",            description="Type text into the focused element"),

        # Universal Actions
        Tool(name="hotkey",               description="Execute a keyboard shortcut"),
        Tool(name="scroll",               description="Scroll in a direction by amount"),
    ]
```

### 5.3 Local Storage Structure

```
~/.screenbridge/
├── sessions/
│   ├── 2026-04-01_10-42/
│   │   ├── frames/
│   │   │   ├── 0001.png          ← Raw screenshot (NEVER sent to cloud)
│   │   │   ├── 0001.json         ← Structured summary (what IS sent to LLM)
│   │   │   └── 0001.diff.json    ← What changed from previous frame
│   │   ├── session.log           ← Action audit trail
│   │   └── task.json             ← Goal, steps taken, outcome
├── config.toml                   ← Privacy settings, LLM config
└── retention_policy.json         ← Auto-delete after N days
```

### 5.4 Small Language Model (SLM) Compatibility

Most frontier LLMs (GPT-4o, Claude 3.x, Gemini 1.5) ship with native vision capabilities, enabling them to interpret raw or lightly described screen states directly. SLMs typically do not. Without structured, low-token, semantically rich screen representations, SLMs cannot reliably reason about UI state or issue accurate control commands.

ScreenBridge addresses this gap natively. By sitting between the OS and the agent as a structured intermediary, the middleware abstracts raw screen data into normalised, text-serialised UI state before it ever reaches the model. This means SLMs receive:

- **Structured element trees** rather than pixel data or screenshot blobs (e.g., JSON/XML accessibility tree with labelled interactive elements, roles, bounds, and states)
- **PII-redacted summaries** with enough semantic context to reason about next actions without requiring vision
- **Pre-filtered, task-relevant state** via the state summarisation layer, reducing token overhead to what the SLM can handle within its context window

This makes ScreenBridge one of the few infrastructure layers that actively **extends the capability ceiling of SLMs** for desktop interaction tasks, rather than assuming a capable frontier model is always in the loop.

> **Design Constraint:** The state summarisation layer must produce outputs that remain actionable for models with context windows as small as 4K tokens. Summary verbosity must be configurable per agent profile.

**Target SLMs:** Phi-3, Mistral 7B, Gemma 2, Qwen2.5, and locally-served models via Ollama are the primary targets. ScreenBridge must be validated against at least two SLMs during Phase 2 testing.

---

## 6. Use Cases & Utilities

### 6.1 AI-Guided Software Teaching — Lumina

The flagship use case. Lumina uses ScreenBridge to watch a user's screen, understand what they are trying to do, and guide them through complex software step by step.

```
User opens Figma for first time.
Lumina: "I can see Figma is open on the home screen. What are you trying to design today?"
User: "A business card"
Lumina: "Great. Click the blue 'New Design' button top right — I'll wait."
[User clicks. ScreenBridge detects screen changed — canvas now open]
Lumina: "Perfect. You're now on the canvas. The toolbar on the left has your drawing tools.
         For a business card, we'll start with a Frame — press F on your keyboard."
```

### 6.2 Autonomous Task Execution

Multi-step autonomous tasks across any desktop application. The LLM drives the loop; ScreenBridge handles perception and execution.

```
User: "Research standing desks under $500 on 3 websites and make a comparison table in Google Sheets"

ScreenBridge loop:
  Opens Chrome → navigates to Officeworks → extracts 3 products + prices
  Navigates to IKEA → extracts 3 products + prices
  Navigates to Kogan → extracts 3 products + prices
  Opens Google Sheets → creates headers → types all 9 products
  Reports: "Done. Your comparison sheet is ready."

If user said "buy the cheapest one":
  Stops at checkout → "Payment page detected. Please complete this yourself."
```

### 6.3 Enterprise RPA — Robotic Process Automation

Automates repetitive cross-application workflows, including legacy software with no API.

```
Daily 9am workflow: "Open SAP, pull yesterday's orders, paste totals into Excel report, save to shared drive"

ScreenBridge:
  Opens SAP (legacy desktop app — no API needed, works via UI)
  Navigates to orders module
  Extracts order data via OCR
  DETECTS: employee salary column visible
  SentinelLayer: HALT on that column — logs the skip
  Continues with non-sensitive order totals only
  Opens Excel report template → pastes extracted figures
  Saves to \shared-drive\reports
  Sends Slack notification: "Daily report complete"
```

### 6.4 Accessibility Navigation

Enables users with motor disabilities or visual impairments to control any application using natural language, without requiring the target application to have built-in accessibility support.

### 6.5 AI-Powered UI Testing

QA teams write tests in plain English. ScreenBridge runs them visually on real applications, providing screenshot evidence at each step. No Selenium. No Playwright. No brittle selectors.

### 6.6 Research & Data Collection

Navigate multiple sources and extract structured data, handling pagination, dynamic content, and login-gated pages — stopping at paywalls and payment screens.

### 6.7 Utility Summary

| Utility | What It Enables |
|---|---|
| Screen Reading | Any LLM can see and understand any app |
| Action Execution | Any LLM can control any app |
| Agentic Loop | Multi-step autonomous tasks across applications |
| SentinelLayer | Safe to deploy on real machines with real data |
| LLM-Agnostic Design | Works with Claude, GPT, Gemini, and local models |
| Local Screenshot Storage | Privacy-compliant for enterprise and regulated industries |
| Diff Engine | Efficient — only sends what changed, reducing token cost |
| Audit Log | Compliance and debugging support |
| Plugin Interface | Lumina and third-party products can build cleanly on top |

---

## 7. Market Analysis & Competitive Landscape

### 7.1 The Opportunity

- E-learning market: $400B+ globally and growing
- Enterprise RPA: multi-billion dollar market dominated by legacy tools (UiPath, Automation Anywhere)
- Neither space has a credible, privacy-first, LLM-native middleware layer

### 7.2 Existing MCP Ecosystem Analysis

| MCP / Tool | What It Does | Key Gap vs ScreenBridge |
|---|---|---|
| Jam | Records screen + auto-packages context for bug reports | Read-only, no agentic loop, no action execution, cloud-based |
| Desktop Commander | File access + terminal on local machine | No screen vision, no UI interaction, no safety layer |
| Control Chrome | Controls Chrome browser tabs only | Browser-only, no desktop apps, Claude-specific |
| Control your Mac | AppleScript automation on macOS | macOS only, Apple-specific, no cross-platform |
| Windows-MCP | Claude interacts with Windows OS | Windows only, no privacy layer, no LLM agnosticism |
| Macos MCP | Lightweight macOS desktop interaction | macOS only, no privacy architecture |
| Kapture | Browser automation via Chrome DevTools | Browser only, no desktop app support |
| Anthropic computer-use | Raw screenshot to cloud LLM | No privacy buffer, Claude-only, not an open SDK |

### 7.3 Competitive Differentiation

| Feature | ScreenBridge | Anthropic computer-use | OpenAdapt | UiPath |
|---|---|---|---|---|
| LLM-agnostic | YES | NO — Claude only | Partial | NO |
| Raw screenshots stay local | YES | NO — sent to cloud | NO | YES |
| Sensitive context auto-detection | YES | NO | NO | Manual rules |
| Open SDK for developers | YES | NO | YES | NO |
| Built-in agentic loop | YES | Partial | Partial | YES |
| Cross-platform (Win+Mac+Linux) | YES | Partial | YES | YES |
| Privacy-first architecture | YES | NO | NO | Partial |

### 7.4 The Three Genuine Differentiators

**Differentiator 1 — The Privacy Buffer**

No tool in the ecosystem processes screen data locally and sends only structured summaries to the cloud. Every existing solution — including Anthropic's own computer-use — sends raw screenshots. ScreenBridge's local processing layer is the only approach that is genuinely enterprise-safe without additional infrastructure.

**Differentiator 2 — SentinelLayer**

Zero MCPs or desktop AI tools automatically halt when they encounter a financial, healthcare, or authentication screen. This is a real safety gap. Enterprises cite this exact concern as a primary blocker to adopting AI automation tools. ScreenBridge solves it natively.

**Differentiator 3 — The Platform / SDK Model**

Every tool in the MCP directory is a closed, single-purpose tool. ScreenBridge is open infrastructure that any developer builds on. The platform model creates network effects that a single-use tool cannot.

### 7.5 Strategic Risk

> The MCP ecosystem is expanding rapidly. Six months ago, half the current directory did not exist. Anthropic is clearly building native desktop control capabilities. The window for ScreenBridge to establish itself as the open infrastructure standard is real but time-limited. Speed of execution is the most important variable.

---

## 8. Business Model

### 8.1 Open Source Core

The core SDK is open source (MIT or Apache 2.0). `pip install screenbridge` — free, open, no account required.

### 8.2 Revenue Streams

| Stream | Model | Target |
|---|---|---|
| ScreenBridge Cloud | Hosted MCP server, managed infrastructure, SaaS | Developers who want zero-setup integration |
| Enterprise SDK | Annual license, SLA, custom sensitivity rules, audit dashboard | IT/security-conscious enterprises |
| On-premise deployment | Professional services + license | Regulated industries (finance, healthcare) |
| Platform licensing | "Powered by ScreenBridge" — SaaS companies embed it | SaaS vendors wanting to reduce support tickets |
| Lumina Pro | Consumer subscription built on ScreenBridge | Individual users, students, professionals |

### 8.3 Lumina Pricing (Built On ScreenBridge)

| Tier | Price | Features |
|---|---|---|
| Free | $0/month | 2 hrs/month guided sessions, 5 supported apps |
| Pro | $15/month | Unlimited sessions, all apps, voice mode, session history |
| Teams | $40/user/month | Everything in Pro, admin dashboard, analytics, custom app flows |
| Enterprise | Custom pricing | On-premise, SSO, compliance, custom LLM, API access |

---

## 9. Development Roadmap

### Phase 1 — Core Engine (Weeks 1–8) - **40% COMPLETE**

**✅ Completed:**
- ✅ Screen capture + local storage with JPEG compression (mss)
- ✅ OCR-based text extraction with bounding box coordinates (Tesseract + EasyOCR fallback)
- ✅ Element detection via macOS Accessibility API (atomacos)
- ✅ Hierarchical element tree with semantic IDs (1, 1.1, 1.2.3)
- ✅ Element-level diff engine with state change tracking
- ✅ Structured JSON summary builder
- ✅ Privacy buffer architecture (raw screenshots never leave machine)

**✅ SentinelLayer (Advanced from Phase 2):**
- ✅ Financial page detection (checkout, banking, crypto URLs + keywords)
- ✅ Healthcare data detection (medical record field patterns)
- ✅ Authentication screen detection (login forms, 2FA)
- ✅ HALT / WARN / SAFE decision pipeline with confidence scoring
- ✅ Configurable sensitivity levels (paranoid/balanced/relaxed)
- ✅ PII redaction (email, credit cards, phone, SSN, API keys) with Luhn validation
- ✅ JSON audit logging per session

**⏳ Remaining:**
- ⏳ Claude and OpenAI LLM connectors (+ Gemini, Ollama)
- ⏳ Canonical tool format definition and translation layer
- ⏳ Basic agentic loop with step limiting and termination
- ⏳ ActionExecutor: click_element, type_into_element, coordinate fallback
- ⏳ User confirmation prompts for destructive actions
- ⏳ Rate limiting (2 actions/sec, 50/task max, exponential backoff)
- ⏳ MCP server adapter layer

**Current Milestone Target:** "Click the Spotify icon" works end-to-end via element-based action.

**Note:** SentinelLayer was completed ahead of schedule due to its critical importance for privacy and safety. Phase 1 now includes full safety infrastructure.

### Phase 2 — Integration & Testing (Weeks 9–16) - **UPDATED SCOPE**

**Revised Focus:**
- Storage manager with retention policy enforcement
- Disk space monitoring and auto-cleanup
- SLM validation: test structured output against Phi-3, Mistral 7B, Gemma 2
- Comprehensive unit test suite (>80% coverage target)
- Integration tests with Playwright
- Performance optimization (OCR caching, element tree caching)
- Debug mode implementation (logs, bounding box visualization, slow-mo)
- User notification flow refinement

**Milestone:** "Order a pizza" works end-to-end from command to confirmation dialog, stopping before payment page. All safety checks validated with zero false negatives on 50+ test scenarios.

### Phase 3 — SDK & Plugin Interface (Weeks 17–22)

- Clean Python package — `pip install screenbridge` works in under 5 minutes
- Plugin interface allowing Lumina and other apps to hook in cleanly
- MCP server mode — connect directly to Claude Desktop
- Full developer documentation
- Example integrations: VS Code automation, Figma guided tour, Excel manipulation

**Milestone:** Lumina can integrate ScreenBridge in under one day of development work.

### Phase 4 — Cross-Platform Polish (Weeks 23–28)

- Linux support (AT-SPI accessibility layer)
- Platform-specific backends: pywinauto (Windows), appscript (macOS)
- Unified abstraction API — same developer code runs on all three platforms
- Cross-platform test suite
- Diff engine optimisation — reduce token cost by 60–80% on stable screens

### Phase 5 — Enterprise & Launch (Weeks 29+)

- Audit log dashboard
- On-premise deployment documentation
- Admin configuration panel
- PyPI public release
- MCP registry listing
- Documentation site
- Lumina v1.0 public beta powered by ScreenBridge

---

## 10. Research Prompt

The following prompt is designed to be fed into Claude Deep Research, Perplexity, or any other research tool to build a comprehensive intelligence report on the ScreenBridge opportunity:

```
Conduct a comprehensive research report on the current landscape of AI-powered desktop
automation, screen understanding middleware, and LLM-computer interaction systems. The
goal is to inform the development of a privacy-first, LLM-agnostic desktop control SDK
called ScreenBridge. Structure the report across the following areas:

1. Existing Solutions & Competitive Landscape
   Map every existing tool, SDK, MCP server, open-source project, and commercial product
   that gives LLMs the ability to see and/or interact with a desktop screen.

2. Screen Understanding & Vision Models
   Research UI-JEPA (Apple), V-JEPA 2 (Meta), Ferret-UI, and any other models
   purpose-built for UI or screen understanding.

3. Privacy & Data Architecture
   Research how existing desktop AI tools handle screen data. Research enterprise
   compliance requirements (GDPR, HIPAA, SOC2) as they relate to screen capture.

4. Sensitivity & Safety Detection
   Research whether any existing tools automatically halt on sensitive screen contexts.

5. Agentic Loop Design
   Research best practices for multi-step agentic loops: termination, error recovery,
   goal verification, action confirmation for irreversible operations, MCP integration.

6. Market & Business Landscape
   Research the opportunity in enterprise RPA, AI QA testing, accessibility tooling,
   AI tutoring, and consumer productivity.

7. Technical Feasibility
   Research cross-platform desktop control feasibility (Windows/macOS/Linux accessibility
   APIs), OCR engines suitable for on-device use, and lightweight local models for
   intent classification.

8. Open Questions
   Are UI-JEPA weights publicly released? What are Anthropic's computer-use API
   restrictions? Has anyone built an open, LLM-agnostic desktop SDK with a privacy
   layer? What do enterprise IT teams cite as the primary blockers to AI desktop
   automation adoption?

Deliver with clear section headings, direct citations, and a final synthesis identifying
the three most significant gaps in the current landscape and the strongest defensible
positioning for ScreenBridge.
```

---

## 11. Summary & Strategic Positioning

### 11.1 What ScreenBridge Is

- An open-source, LLM-agnostic middleware SDK
- Gives any LLM the ability to see and interact with any desktop application
- Processes screen data locally — raw screenshots never leave the machine
- Automatically halts when sensitive context (financial, healthcare, auth) is detected
- Exposes a plugin interface for products like Lumina to build on top of it
- Distributed as a Python package and MCP server

### 11.2 What ScreenBridge Is Not

- Not an AI assistant
- Not tied to any single LLM
- Not a consumer product on its own
- Not a competitor to Lumina — it is Lumina's foundation

### 11.3 The One-Line Pitch

> ScreenBridge is the open, privacy-first middleware that gives any LLM eyes and hands on your desktop — with a built-in safety layer that stops the moment it sees something sensitive.

### 11.4 Why This Stands Out

The MCP ecosystem has over 150 connectors and is growing rapidly. Despite this, no tool combines: cross-platform desktop control, a local privacy buffer, automatic sensitivity detection, an open SDK model, and LLM agnosticism — in a single coherent platform. ScreenBridge is not another MCP tool. It is the infrastructure layer underneath them.

### 11.5 Priority Action

Begin Phase 1 development immediately. The competitive window is real but narrowing as Anthropic, OpenAI, and the broader MCP ecosystem expand native desktop control capabilities. The privacy architecture and SentinelLayer are the defensible differentiators — build them fast, build them well, and ship.
