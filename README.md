# A.H.I. — Artificial Human Intelligence (Jane OS)

> *"I suspect the real issue isn't the code — it's the architecture."*

A local-first, privacy-respecting AI cognitive assistant modeled after **Patrick Jane** from *The Mentalist*, fused with the operational intelligence of **J.A.R.V.I.S.**

Built entirely on free, open-source tools. Runs 100% on your machine.

---

## What Jane Can Do

| Domain | Capability |
|---|---|
| 🧠 **Conversation** | Patrick Jane personality — observant, charming, Socratic |
| 💻 **Coding** | Write, debug, explain code; routes to a specialized coder model |
| 🔐 **Cybersecurity** | Ethical hacking mentor: Nmap, Scapy, WHOIS, DNS, attack explanations |
| 🌐 **Web Search** | DuckDuckGo + RSS news feeds for real-time information |
| 📚 **Teaching** | Builds structured learning roadmaps (Beginner → Advanced) |
| 🗂️ **Memory** | Short-term (ring buffer) + long-term (ChromaDB vector search) |
| 📁 **File System** | Read, write, list files with approval gates |
| 🖥️ **System Info** | Live CPU, RAM, disk, uptime stats |
| 🗺️ **IP Locator** | Geolocate any IP address |
| 📂 **Projects** | Track active projects, goals, notes across sessions |

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed and running

### 2. Pull Required Models

```bash
ollama pull llama3.1        # General brain
ollama pull qwen2.5-coder   # Coding + cyber model
ollama pull nomic-embed-text # Memory embeddings
```

### 3. Install Dependencies

```bash
git clone https://github.com/yourname/ahi-ai
cd ahi-ai
pip install -r requirements.txt
```

### 4. Run

```bash
python main.py
```

---

## Slash Commands

| Command | Description |
|---|---|
| `/help` | Show all commands |
| `/clear` | Wipe short-term memory |
| `/project <name>` | Set or view active project |
| `/memory` | Show memory stats |
| `/tools` | List all available tools |
| `/exit` | Quit |

---

## Architecture

```
ahi-ai/
│
├── main.py                    # Entry point
├── config.yaml                # All settings
│
├── brain/
│   ├── orchestrator.py        # Core agent loop (intent → route → tools → respond)
│   ├── intent_classifier.py   # Weighted keyword + regex intent detection
│   ├── model_router.py        # Routes to best Ollama model per intent
│   └── personality_engine.py  # Patrick Jane system prompt builder
│
├── memory/
│   ├── short_term.py          # JSON ring buffer (last N exchanges)
│   ├── long_term.py           # ChromaDB vector memory (semantic search)
│   └── project_state.py       # Active project tracking
│
├── tools/
│   ├── tool_registry.py       # Central tool hub with Ollama function-calling schemas
│   ├── web_search.py          # DuckDuckGo + RSS news
│   ├── ip_locator.py          # IP geolocation
│   ├── code_executor.py       # Safe Python subprocess executor
│   ├── file_manager.py        # Read/write/list filesystem
│   ├── system_info.py         # Hardware + OS stats
│   └── cyber_helper.py        # Nmap, Scapy, WHOIS, DNS, attack explanations
│
├── teacher/
│   ├── curriculum_builder.py  # LLM-powered learning roadmap generator
│   └── teaching_loop.py       # Tool wrappers for teaching engine
│
├── knowledge/
│   ├── ingest.py              # PDF/Markdown/TXT → ChromaDB ingestion pipeline
│   ├── retrieve.py            # Semantic search over knowledge base
│   └── sources/               # Drop your PDFs and notes here
│
├── ui/
│   └── cli.py                 # Rich terminal UI with prompt history
│
├── utils/
│   ├── logger.py              # Rich console + rotating file logger
│   └── security.py            # Input sanitization + approval gates
│
└── data/
    ├── short_term.json         # Persisted conversation buffer
    ├── project_state.json      # Active project data
    ├── chromadb/               # Vector database files
    ├── curricula/              # Saved learning roadmaps
    └── logs/jane.log           # Rotating log file
```

---

## Adding Your Own Knowledge

Drop PDF, Markdown, or TXT files into `knowledge/sources/`, then run:

```bash
python -m knowledge.ingest
```

Jane will embed and index them. From then on, relevant passages are automatically retrieved and injected into context when you ask about related topics.

---

## Nmap Setup (Windows)

Jane auto-detects Nmap if it's on your PATH. For a custom install path:

```
You ❯ tell jane: nmap is at D:\nmap\nmap.exe
```

Or edit `data/nmap_path.json` directly:
```json
{"path": "D:\\nmap\\nmap.exe"}
```

---

## Roadmap

| Phase | Status | Features |
|---|---|---|
| **Phase 1** | ✅ Complete | Core brain, memory, tools, CLI, teaching |
| **Phase 2** | 🔄 In Progress | Scapy labs, PCAP analysis, RAG improvements |
| **Phase 3** | 📋 Planned | Voice (Whisper STT + Piper TTS), wake word |
| **Phase 4** | 📋 Planned | Desktop UI (PyQt6), multi-agent reasoning, autonomous tasks |

---

## Improving Intent Detection

The intent classifier uses weighted keyword scoring + regex patterns. To extend it, add entries to `brain/intent_classifier.py`:

```python
"your_category": {
    "keywords": ["word1", "word2"],
    "strong_keywords": ["exact phrase"],
    "patterns": [r"regex pattern \w+"],
}
```

---

## Security Notes

- All network tools (Nmap, DNS, WHOIS) require user approval before execution.
- Code execution is sandboxed to a subprocess with a configurable timeout.
- File writes require user approval.
- Nmap scans are restricted to a whitelist (`localhost`, `scanme.nmap.org`) by default.
- No data leaves your machine unless you explicitly use web search or IP lookup.

---

*Built with Python · Ollama · ChromaDB · Rich*
