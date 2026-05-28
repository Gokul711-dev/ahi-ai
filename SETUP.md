# A.H.I. Jane OS — Complete Setup & Run Guide

---

## 1. Prerequisites

| Requirement | Version | Install |
|---|---|---|
| Python | 3.11+ | https://python.org |
| Ollama | latest | https://ollama.com |
| Git | any | https://git-scm.com |

---

## 2. Install Ollama & Pull Models

### Install Ollama
- **Windows**: Download from https://ollama.com/download
- **macOS**: `brew install ollama`
- **Linux**: `curl -fsSL https://ollama.com/install.sh | sh`

### Start Ollama
```bash
ollama serve
```
Keep this terminal open (or it runs as a background service on Windows/macOS).

### Pull Required Models
```bash
ollama pull llama3.1           # General brain (~4.7 GB)
ollama pull qwen2.5-coder:7b   # Coding + cyber model (~4.4 GB)
ollama pull nomic-embed-text   # Memory embeddings (~274 MB)
```

---

## 3. Install Jane OS

```bash
# Clone / extract the project
cd ahi-ai

# Create virtual environment (recommended)
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install core dependencies
pip install -r requirements.txt
```

---

## 4. Run Modes

### TEXT MODE (CLI) — No extras needed
```bash
python main.py
```

### DESKTOP GUI — Requires PyQt6
```bash
pip install PyQt6
python main.py --gui
```

### VOICE + CLI — Microphone + speakers
```bash
pip install faster-whisper sounddevice pyttsx3
python main.py --voice
```

### FULL EXPERIENCE — GUI + Voice
```bash
pip install PyQt6 faster-whisper sounddevice pyttsx3
python main.py --gui --voice
```

---

## 5. Voice Setup (Detailed)

### STT — Speech to Text (Whisper)
```bash
pip install faster-whisper sounddevice
```
- First run downloads the Whisper model (~140 MB for "base")
- Model sizes: `tiny` (fast) → `base` → `small` → `medium` (most accurate)
- Change in `config.yaml` → `voice.stt_model`

**Windows microphone fix** — if mic not detected:
```bash
pip install sounddevice
# Then in Windows: Settings → Privacy → Microphone → Allow desktop apps
```

### TTS — Text to Speech

**Option A: pyttsx3** (easiest, uses built-in OS voices)
```bash
pip install pyttsx3
```

**Option B: Piper TTS** (better quality neural voices, fully offline)
```bash
# 1. Download Piper from https://github.com/rhasspy/piper/releases
# 2. Extract to a folder (e.g. C:\piper\ or ~/piper/)
# 3. Add piper to your PATH, or note the path
# 4. Download a voice model from https://huggingface.co/rhasspy/piper-voices
#    Example: en_US-lessac-medium.onnx + en_US-lessac-medium.onnx.json
# 5. Place model files in:  voice/models/
mkdir -p voice/models
# Copy your .onnx and .onnx.json files there
```

Jane will automatically prefer Piper over pyttsx3 if both are installed.

### Wake Word (Hands-Free — Optional)
```bash
pip install openwakeword
```
Then in `config.yaml`:
```yaml
voice:
  wake_word_enabled: true
  wake_words:
    - "hey jane"
```

### VAD (Smart mic stop — Optional)
```bash
pip install webrtcvad
```
With VAD enabled, Jane stops listening when you stop talking instead of waiting a fixed duration.

---

## 6. Cyber Tools Setup

### Nmap (Network Scanner)
- **Windows**: Download from https://nmap.org/download → install to `C:\nmap\`
  Jane auto-detects it. If not found, tell Jane:
  ```
  You > set nmap path to C:\nmap\nmap.exe
  ```
- **Linux/macOS**: `sudo apt install nmap` or `brew install nmap`

Jane auto-discovers Nmap if it's on your system PATH.

### Expanding Allowed Scan Targets
By default, Nmap scans are restricted to: `localhost`, `127.0.0.1`, `scanme.nmap.org`.

To add your own lab machines, edit `tools/cyber_helper.py`:
```python
ALLOWED_TARGETS = {"localhost", "127.0.0.1", "scanme.nmap.org", "192.168.1.0/24"}
```

### Scapy (Packet Crafting)
Already installed via `pip install scapy`.
- **Windows**: Also install `Npcap` from https://npcap.com for live packet capture.
- **Linux**: May need `sudo` for raw socket access.

---

## 7. Slash Commands (CLI & GUI)

| Command | What it does |
|---|---|
| `/help` | Show all commands |
| `/clear` | Wipe short-term memory |
| `/project <name>` | Set or view active project |
| `/memory` | Show memory stats (long + short term) |
| `/tools` | List all loaded tools |
| `/voice` | Toggle voice output on/off (CLI) |
| `/exit` | Quit |

---

## 8. Knowledge Base (Add Your Own Docs)

Drop PDF, Markdown, or TXT files into `knowledge/sources/`:
```
knowledge/sources/
  networking_bible.pdf
  python_cookbook.pdf
  my_notes.md
```

Then run ingestion:
```bash
python main.py --ingest
```

Jane will semantically index everything. From then on, relevant passages are automatically retrieved and injected into context when you ask about related topics.

---

## 9. Project Tracking

```
You > /project AHI-Assistant
```
Jane tracks your active project across sessions — goals, notes, recent files.

---

## 10. Troubleshooting

### "Ollama connection refused"
```bash
# Make sure Ollama is running:
ollama serve
```

### "Model not found"
```bash
ollama pull llama3.1
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text
```

### GUI won't open (Linux)
```bash
# Install Qt platform plugin:
sudo apt install python3-pyqt6 libxcb-xinerama0
# Or set display:
export DISPLAY=:0
```

### Voice mic not working (Linux)
```bash
sudo apt install portaudio19-dev python3-pyaudio
pip install sounddevice
```

### "chromadb error on first run"
Normal — ChromaDB creates its database on first run. If it fails:
```bash
rm -rf data/chromadb
python main.py
```

### Windows: Scapy needs Npcap
Download from https://npcap.com and install before using packet crafting tools.

---

## 11. File Structure

```
ahi-ai/
├── main.py                  ← Entry point
├── config.yaml              ← All settings
├── requirements.txt
│
├── brain/                   ← Intelligence layer
│   ├── orchestrator.py      ← Main agent loop
│   ├── intent_classifier.py ← What does the user want?
│   ├── model_router.py      ← Which model to use?
│   └── personality_engine.py← Patrick Jane system prompt
│
├── memory/                  ← Memory systems
│   ├── short_term.py        ← Recent conversation (ring buffer)
│   ├── long_term.py         ← ChromaDB vector memory
│   └── project_state.py     ← Active project tracking
│
├── tools/                   ← All tool implementations
│   ├── tool_registry.py     ← Central tool hub
│   ├── cyber_helper.py      ← Nmap, Scapy, WHOIS, DNS, attacks
│   ├── web_search.py        ← DuckDuckGo + RSS
│   ├── code_executor.py     ← Python subprocess runner
│   ├── file_manager.py      ← Read/write/list files
│   ├── system_info.py       ← CPU/RAM/disk stats
│   └── ip_locator.py        ← IP geolocation
│
├── voice/                   ← Voice layer
│   ├── stt.py               ← Whisper speech-to-text
│   ├── tts.py               ← pyttsx3 / Piper TTS
│   ├── wake_word.py         ← OpenWakeWord / Porcupine
│   └── voice_manager.py     ← Coordinates all voice I/O
│
├── teacher/                 ← Learning engine
│   ├── curriculum_builder.py← LLM roadmap generator
│   └── teaching_loop.py     ← Tool wrappers
│
├── knowledge/               ← RAG knowledge base
│   ├── ingest.py            ← PDF/MD/TXT → ChromaDB
│   ├── retrieve.py          ← Semantic search
│   └── sources/             ← DROP YOUR FILES HERE
│
├── ui/
│   ├── cli.py               ← Rich terminal interface
│   └── gui.py               ← PyQt6 Jarvis-style desktop GUI
│
└── data/                    ← Runtime data (auto-created)
    ├── short_term.json
    ├── project_state.json
    ├── chromadb/
    ├── curricula/
    └── logs/jane.log
```

---

## 12. Quick Reference Card

```
# Bare minimum (text only):
ollama serve
python main.py

# With GUI:
pip install PyQt6
python main.py --gui

# With voice:
pip install faster-whisper sounddevice pyttsx3
python main.py --voice

# Full Jarvis experience:
python main.py --gui --voice

# Add knowledge:
python main.py --ingest
```

---

*Built with Python · Ollama · ChromaDB · PyQt6 · Whisper · Piper*
