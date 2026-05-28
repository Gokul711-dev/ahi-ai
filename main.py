"""
main.py — A.H.I. Entry Point

Usage:
    python main.py                  # CLI text mode
    python main.py --gui            # Desktop GUI (requires PyQt6)
    python main.py --gui --voice    # GUI + voice I/O
    python main.py --voice          # CLI + voice
    python main.py --ingest         # Ingest knowledge/sources/ into ChromaDB
"""
import sys
import yaml
import argparse
from pathlib import Path

from brain.orchestrator import JaneOrchestrator
from utils.logger import get_logger


def load_config() -> dict:
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("Error: config.yaml not found. Run from the project root directory.")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_args():
    parser = argparse.ArgumentParser(description="A.H.I. — Jane OS")
    parser.add_argument("--gui",    action="store_true", help="Launch desktop GUI (requires PyQt6)")
    parser.add_argument("--voice",  action="store_true", help="Enable voice I/O")
    parser.add_argument("--ingest", action="store_true", help="Run knowledge ingestion and exit")
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config()
    logger = get_logger(config=config)
    logger.info("Initializing A.H.I. Core...")

    # Knowledge ingestion mode
    if args.ingest:
        print("Running knowledge ingestion pipeline...")
        from knowledge.ingest import ingest_directory
        k = config.get("knowledge", {})
        o = config.get("ollama", {})
        result = ingest_directory(
            sources_dir=k.get("sources_dir", "knowledge/sources"),
            chromadb_path=k.get("chromadb_path", "data/chromadb"),
            collection_name=k.get("collection_name", "jane_knowledge"),
            ollama_url=o.get("base_url", "http://localhost:11434"),
            embedding_model=o.get("models", {}).get("embedding", "nomic-embed-text"),
            chunk_size=k.get("chunk_size", 500),
            overlap=k.get("chunk_overlap", 50),
        )
        print(f"Done: {result}")
        sys.exit(0)

    # Boot orchestrator
    try:
        print("Starting Jane OS...")
        orchestrator = JaneOrchestrator(config)
        logger.info("Orchestrator ready.")
    except Exception as e:
        logger.exception(f"Orchestrator init failed: {e}")
        print(f"\n[Startup Error] {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure Ollama is running:   ollama serve")
        print("  2. Pull required models:")
        print("       ollama pull llama3.1")
        print("       ollama pull qwen2.5-coder")
        print("       ollama pull nomic-embed-text")
        sys.exit(1)

    # Voice setup
    voice_manager = None
    if args.voice:
        try:
            from voice.voice_manager import VoiceManager
            if "voice" not in config:
                config["voice"] = {}
            config["voice"]["enabled"] = True
            voice_manager = VoiceManager(config)
            status = voice_manager.get_status()
            print(f"[Voice] TTS: {status['tts']}")
            print(f"[Voice] STT: Whisper ({status['stt_model']})")
        except ImportError as e:
            print(f"[Voice] Missing dependency: {e}")
            print("[Voice] pip install faster-whisper sounddevice pyttsx3")
            print("[Voice] Continuing in text-only mode.")
        except Exception as e:
            print(f"[Voice] Init failed: {e} — text-only mode.")

    # Launch
    try:
        if args.gui:
            _launch_gui(orchestrator, voice_manager)
        else:
            _launch_cli(orchestrator, voice_manager)
    except KeyboardInterrupt:
        print("\nGoodbye.")
    finally:
        if voice_manager:
            voice_manager.shutdown()


def _launch_gui(orchestrator, voice_manager):
    try:
        from ui.gui import run_gui
        run_gui(orchestrator, voice_manager)
    except ImportError:
        print("\n[GUI Error] PyQt6 not installed. Run: pip install PyQt6")
        print("Falling back to CLI.\n")
        _launch_cli(orchestrator, voice_manager)


def _launch_cli(orchestrator, voice_manager):
    from ui.cli import run_cli
    run_cli(orchestrator, voice_manager=voice_manager)


if __name__ == "__main__":
    main()
