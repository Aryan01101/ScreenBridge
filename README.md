# ScreenBridge

**Privacy-first middleware that gives any LLM eyes and hands on your desktop.**

ScreenBridge is an open-source SDK that enables Large Language Models (LLMs) to see and interact with desktop applications while keeping raw screenshots entirely local. Only structured JSON summaries are sent to cloud APIs, ensuring privacy without sacrificing functionality.

## 🎯 Core Features

- **Privacy Buffer**: Raw screenshots never leave your machine - only structured summaries
- **SentinelLayer**: Automatic detection of sensitive contexts (financial, healthcare, auth screens)
- **LLM-Agnostic**: Works with Claude, GPT-4, Gemini, and local models (Ollama)
- **Element-Based Actions**: Robust, resolution-independent desktop control
- **Agentic Loop**: Multi-step autonomous task execution with built-in safety guardrails

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install screenbridge

# Full installation with all models
pip install screenbridge[full]
```

### Basic Usage

```python
from screenbridge import ScreenBridge
from screenbridge.connectors import ClaudeConnector
import asyncio

async def main():
    async with ScreenBridge(llm=ClaudeConnector(api_key="your-api-key")) as bridge:
        result = await bridge.run("Open Spotify and play my liked songs")
        print(f"Success: {result['success']}")

asyncio.run(main())
```

## 📋 Requirements

- **Python**: 3.10+
- **Platform**: macOS 12+ (Monterey or later)
  - Windows & Linux support coming in Phase 4
- **LLM API Key**: Claude, OpenAI, Gemini, or Ollama (local)
- **Disk Space**: ~500MB for models and session storage

## 🏗️ Architecture

ScreenBridge consists of 6 core modules:

1. **ScreenReader** - Screenshot capture and local storage
2. **SentinelLayer** - Privacy and safety guardian
3. **LLMBridge** - LLM communication and agentic loop
4. **ActionExecutor** - Desktop action execution
5. **ElementTreeBuilder** - UI element hierarchy construction
6. **StorageManager** - Disk space and retention management

See [SCREENBRIDGE_PRD.md](./SCREENBRIDGE_PRD.md) for complete architecture details.

## 🔒 Privacy & Security

### What Gets Sent to LLMs

✅ **Sent**: Structured JSON with element tree, extracted text, semantic summary
❌ **NEVER Sent**: Raw screenshots, pixel data, images

### SentinelLayer Protection

ScreenBridge automatically **HALTS** on:
- Financial pages (checkout, banking, crypto)
- Healthcare/medical records
- Authentication screens (login, 2FA)
- Personal documents (passport, tax forms, IDs)
- Password manager screens

### Data Storage

- Screenshots: `~/.screenbridge/sessions/<session-id>/frames/`
- Retention: 7 days (configurable)
- Format: JPEG (compressed, configurable quality)
- Audit logs: Full action history for debugging

## 🛠️ Configuration

Config file: `~/.screenbridge/config.json`

```json
{
  "privacy_tier": "summarised",
  "max_steps": 10,
  "screenshot_format": "jpeg",
  "retention_days": 7,
  "confirmation_required": [
    "delete_file",
    "send_message",
    "submit_form"
  ]
}
```

See [config_template.json](./screenbridge/config_template.json) for all options.

## 🤝 Use Cases

- **AI-Guided Tutorials** (Lumina): Watch users learn software, provide step-by-step guidance
- **Autonomous Task Execution**: Multi-step workflows across any desktop application
- **Enterprise RPA**: Automate legacy software without APIs
- **Accessibility**: Natural language control for users with motor disabilities
- **QA Testing**: Write UI tests in plain English

## 🗺️ Roadmap

- **Phase 1** (Current): Core engine, macOS support, basic agentic loop
- **Phase 2** (Weeks 9-16): Full SentinelLayer, PII redaction, SLM validation
- **Phase 3** (Weeks 17-22): MCP server, plugin interface, SDK polish
- **Phase 4** (Weeks 23-28): Windows & Linux support
- **Phase 5** (Weeks 29+): Enterprise features, PyPI release, public beta

## 📚 Documentation

- [Product Requirements Document](./SCREENBRIDGE_PRD.md) - Complete technical spec
- [Development Guidelines](./CLAUDE.md) - Contribution standards
- API Documentation (coming soon)
- MCP Server Guide (coming soon)

## 🧪 Development Status

**Current Version**: 0.1.0-alpha
**Status**: Phase 1 - Core Engine Development

ScreenBridge is in active development. The API may change between releases.

## 🤔 FAQ

**Q: Does this work with my LLM of choice?**
A: Yes! ScreenBridge supports Claude, GPT-4, Gemini, and any local model via Ollama.

**Q: What gets sent to the cloud?**
A: Only structured JSON summaries. Raw screenshots stay on your machine.

**Q: Can I run this fully offline?**
A: Yes, use the Ollama connector for 100% local operation.

**Q: Which platforms are supported?**
A: Phase 1 focuses on macOS 12+. Windows & Linux support coming in Phase 4.

**Q: Is this safe for sensitive work?**
A: SentinelLayer automatically halts on financial/healthcare/auth screens. However, always review actions before confirming destructive operations.

## 📄 License

MIT License - See [LICENSE](./LICENSE) for details.

## 🙏 Acknowledgments

Built with:
- [mss](https://github.com/BoboTiG/python-mss) - Screenshot capture
- [atomacos](https://github.com/pyatom/atomacos) - macOS accessibility
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) - integration
- [OpenAI SDK](https://github.com/openai/openai-python) - GPT integration

---

**Note**: Do not include "Claude" in commit messages (per project guidelines)