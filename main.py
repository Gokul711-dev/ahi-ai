"""
main.py
A.H.I. Entry Point.
"""
import sys
import yaml
from pathlib import Path

from brain.orchestrator import JaneOrchestrator
from ui.cli import run_cli
from utils.logger import get_logger

def load_config() -> dict:
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("Error: config.yaml not found.")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    logger = get_logger(config=config)
    logger.info("Initializing A.H.I. Core...")
    
    try:
        orchestrator = JaneOrchestrator(config)
        logger.info("Orchestrator ready. Starting UI.")
        
        # Start CLI
        run_cli(orchestrator)
        
    except Exception as e:
        logger.exception(f"Startup failed: {e}")
        print(f"Startup failed: {e}")

if __name__ == "__main__":
    main()
