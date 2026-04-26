# ScreenBridge Development Guidelines

## Primary Reference Document

**ALWAYS** consult `SCREENBRIDGE_PRD.md` for:
- Complete architecture and module structure (Section 3)
- Technology stack decisions (Section 4)
- Privacy and security requirements (Section 2.2, 2.3, 2.4)
- Development roadmap and phase requirements (Section 9)
- Use cases and expected behavior (Section 6)

The PRD is the single source of truth for this project.

## Core Principles

### 1. Privacy-First Architecture
- Raw screenshots MUST NEVER be sent to cloud APIs
- Only structured JSON summaries are transmitted to LLMs
- All screenshot data stays in local storage (`~/.screenbridge/`)
- Default to "Summarised" privacy tier unless user explicitly opts into "Full"
- Implement PII redaction BEFORE summary generation

### 2. Security Requirements

#### SentinelLayer - Non-Negotiable Safety
The SentinelLayer MUST halt execution on these contexts:
- Financial pages (checkout, banking, crypto)
- Healthcare/medical records
- Authentication screens (login, 2FA)
- Personal documents (passport, tax, ID)
- Password manager screens

See PRD Section 2.3 for detection methods and Section 3.2 for implementation details.

#### Sensitive Data Handling
- Never commit API keys, credentials, or config files with secrets
- Use environment variables or secure config files (excluded from git)
- Audit log every HALT/WARN decision with timestamp and reason
- Rate limit action execution to prevent runaway loops

### 3. LLM-Agnostic Design
- Support Claude, GPT-4, Gemini, and Ollama (local) equally
- Use connector pattern for all LLM integrations (see PRD Section 5.1)
- Never hardcode LLM-specific behavior into core modules
- MCP server implementation should work with any MCP-compatible client

### 4. Module Boundaries

Respect the six core modules (PRD Section 3.1):
1. **ScreenReader** - Vision layer only, no decision making
2. **SentinelLayer** - Safety decisions, runs before LLMBridge
3. **LLMBridge** - LLM communication only, no screen interaction
4. **ActionExecutor** - Action execution only, requires confirmation for irreversible actions
5. **ElementTreeBuilder** - Builds hierarchical element tree with semantic IDs
6. **StorageManager** - Disk space monitoring and retention policy management

Do not mix responsibilities across modules.

### 5. Element-Based Interaction

ScreenBridge uses element-based actions as the primary interaction method, with coordinate-based fallback.

#### When to Use Element IDs vs Coordinates

**Use element-based actions (primary):**
- Standard desktop applications with accessibility APIs
- Web browsers (buttons, links, forms, inputs)
- Native OS controls (menus, dialogs, toolbars)
- Office applications (Word, Excel, PowerPoint)
- Development tools (VS Code, IDEs)

**Use coordinate-based fallback:**
- Canvas-based applications (Figma, Photoshop, games)
- Custom-rendered UIs without accessibility support
- WebGL/Canvas elements in browsers
- Virtual machines or remote desktop sessions
- When element detection fails

#### Auto-Upgrade Strategy

The ActionExecutor implements an auto-upgrade layer:
```python
# Old coordinate-based call
click(x=150, y=200)

# Internally:
# 1. Check if element exists at (150, 200)
# 2. If yes, extract element_id and use click_element(element_id)
# 3. If no, fall back to coordinate-based click(150, 200)
```

This ensures backwards compatibility while gaining robustness benefits.

#### Element ID Format

- Root window: `"1"`
- Top-level children: `"1.1"`, `"1.2"`, `"1.3"`
- Nested children: `"1.1.1"`, `"1.2.1"`, etc.
- Hierarchical structure preserves parent-child relationships

#### Best Practices

1. **Always prefer element IDs when available** - More robust to window resize, DPI changes, and UI updates
2. **Include element IDs in action logs** - Easier debugging and replay
3. **Graceful degradation** - If element tree building fails, fall back to coordinate mode
4. **Validate element state** - Check `state` field (enabled/disabled/focused) before acting
5. **Use `find_element_by_label()`** - When you know the button text but not the ID

#### Resolution Independence

Element-based actions work across:
- Different screen resolutions
- Window resizes
- DPI scaling changes
- Multi-monitor setups

Coordinate-based actions break in these scenarios. Always prefer element IDs when possible.

### 6. Cross-Platform Compatibility

Target platforms: Windows 10/11, macOS 12+, Ubuntu 20+
- Use platform-specific backends via unified API
- Test on all three platforms before marking features complete
- See PRD Section 4.1 for platform-specific tech choices

### 7. Small Language Model (SLM) Support

Per PRD Section 5.4:
- Structured summaries MUST work with SLMs (Phi-3, Mistral 7B, Gemma 2)
- Keep summary verbosity configurable
- Target: summaries under 4K tokens for lowest-capability SLMs
- Validate against at least two SLMs during Phase 2
- Element tree structure is particularly beneficial for SLMs (token-efficient, semantically rich)

## Implementation Standards

### Code Quality
- Type hints required for all public APIs
- Comprehensive docstrings for modules, classes, and public methods
- Unit tests for all modules with >80% coverage
- Integration tests for agentic loops

### Dependencies
- Minimize dependency footprint
- Use `uv` for package management (PRD Section 4.1)
- Pin versions in pyproject.toml
- Document installation requirements clearly

### Developer Experience
- `pip install screenbridge` should work in under 5 minutes
- Clear error messages when permissions/API keys missing
- Example code in docstrings and README
- MCP server mode should be trivial to enable

## Common Pitfalls to Avoid

1. **Sending screenshots to cloud** - This violates the core value proposition
2. **Skipping SentinelLayer checks** - Never bypass safety for "just testing"
3. **Hardcoding LLM provider** - Always use connector abstraction
4. **Mixing module concerns** - Keep ScreenReader, Sentinel, Bridge, Executor, ElementTreeBuilder, StorageManager separate
5. **Ignoring SLM compatibility** - Summaries must work without vision models
6. **Missing action confirmations** - Irreversible actions need user approval
7. **Platform-specific code in core** - Use platform abstraction layer
8. **Using coordinates when elements available** - Always prefer element IDs for robustness
9. **Not handling element tree build failures** - Always have coordinate fallback
10. **Ignoring disk space limits** - StorageManager must actively monitor and clean up

## Security Vulnerabilities to Watch

Per instructions, be vigilant about:
- Command injection in action execution
- Path traversal in screenshot storage
- XSS if exposing web interfaces
- Credential leakage in logs or error messages
- Unvalidated user input in LLM prompts
- Race conditions in agentic loops

Fix immediately if detected.

## Development Workflow

Follow the roadmap phases in PRD Section 9:
- Phase 1: Core Engine (Weeks 1-8)
- Phase 2: SentinelLayer (Weeks 9-16)
- Phase 3: SDK & Plugin Interface (Weeks 17-22)
- Phase 4: Cross-Platform Polish (Weeks 23-28)
- Phase 5: Enterprise & Launch (Weeks 29+)

Do not skip ahead or backport features across phases without consulting PRD.

## Questions or Ambiguity?

When uncertain about:
- Architecture decisions → Check PRD Section 3
- Technology choices → Check PRD Section 4
- Privacy behavior → Check PRD Section 2
- Use case requirements → Check PRD Section 6
- Competitive positioning → Check PRD Section 7

The PRD contains the answer. If genuinely ambiguous, ask the user for clarification.

## Commit Message Convention

Follow the global convention: Do not include "Claude" in commit messages.
