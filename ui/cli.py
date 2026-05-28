"""
ui/cli.py
Rich terminal interface with voice-aware input loop and proper slash commands.
"""
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from pathlib import Path

console = Console()

SLASH_COMMANDS = {
    "/clear":   "Clear short-term conversation memory",
    "/project": "View or set active project  (e.g. /project MyApp)",
    "/memory":  "Show long-term memory stats",
    "/tools":   "List all available tools",
    "/voice":   "Toggle voice output on/off",
    "/help":    "Show this help message",
    "/exit":    "Quit Jane",
}


def print_banner():
    banner = Text()
    banner.append("\n")
    banner.append("  ╔══════════════════════════════╗\n", style="bold cyan")
    banner.append("  ║   A.H.I. — Jane OS  v2.0     ║\n", style="bold cyan")
    banner.append("  ║   Artificial Human Intel.    ║\n", style="dim cyan")
    banner.append("  ╚══════════════════════════════╝\n", style="bold cyan")
    banner.append("  Local · Private · Always Watching\n", style="dim")
    console.print(banner)


def show_help():
    table = Table(title="Slash Commands", border_style="cyan", header_style="bold magenta")
    table.add_column("Command", style="cyan", width=16)
    table.add_column("Description", style="white")
    for cmd, desc in SLASH_COMMANDS.items():
        table.add_row(cmd, desc)
    console.print(table)


def run_cli(orchestrator, voice_manager=None):
    print_banner()

    voice_hint = ""
    if voice_manager:
        status = voice_manager.get_status()
        voice_hint = f"  🔊 Voice: {status['tts']}  |  🎤 STT: Whisper ({status['stt_model']})\n"
        console.print(f"[green]{voice_hint}[/green]")

    console.print(
        "[green]Jane is online. Type [bold]/help[/bold] for commands "
        "or [bold]/voice[/bold] to speak.[/green]\n"
    )

    history_file = Path("data/.cli_history")
    history_file.parent.mkdir(parents=True, exist_ok=True)

    style = Style.from_dict({"prompt": "ansicyan bold"})
    session = PromptSession(
        style=style,
        history=FileHistory(str(history_file)),
    )

    _voice_output_enabled = voice_manager is not None

    while True:
        try:
            prompt_str = "You 🎤 ❯ " if voice_manager else "You ❯ "
            user_input = session.prompt(prompt_str)
        except KeyboardInterrupt:
            console.print("\n[dim]Ctrl+C — type /exit to quit.[/dim]")
            continue
        except EOFError:
            break

        if not user_input.strip():
            continue

        stripped = user_input.strip()

        # Slash commands
        if stripped.startswith("/"):
            _voice_output_enabled = _handle_slash(
                stripped, orchestrator, voice_manager, _voice_output_enabled
            )
            continue

        # Voice input trigger: "speak" or "listen"
        if stripped.lower() in ("speak", "listen", "voice input") and voice_manager:
            console.print("[dim cyan]🎤 Listening...[/dim cyan]")
            spoken = voice_manager.listen()
            if spoken:
                console.print(f"[dim]Heard: {spoken}[/dim]")
                stripped = spoken
            else:
                console.print("[yellow]Didn't catch that. Try again or type your message.[/yellow]")
                continue

        # Send to orchestrator
        with console.status("[dim italic]Jane is thinking...[/dim italic]", spinner="dots"):
            try:
                response = orchestrator.process(stripped)
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {e}")
                continue

        console.print(
            Panel(
                Markdown(response),
                title="[bold magenta]Jane[/bold magenta]",
                border_style="magenta",
                padding=(0, 2),
            )
        )
        console.print()

        # Speak the response if voice enabled
        if _voice_output_enabled and voice_manager:
            voice_manager.speak(response)


def _handle_slash(cmd_text: str, orchestrator, voice_manager, voice_output: bool) -> bool:
    """Handle slash commands. Returns updated voice_output state."""
    parts = cmd_text.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""

    if cmd in ("/exit", "/quit"):
        console.print("[dim italic]Jane: Until next time.[/dim italic]")
        sys.exit(0)

    elif cmd == "/help":
        show_help()

    elif cmd == "/clear":
        orchestrator.short_memory.clear()
        console.print("[yellow]✓ Short-term memory cleared.[/yellow]")

    elif cmd == "/project":
        if arg:
            orchestrator.project_state.set_project(arg)
            console.print(f"[green]✓ Active project:[/green] [bold]{arg}[/bold]")
        else:
            p = orchestrator.project_state.get_active()
            if p:
                table = Table(border_style="cyan", show_header=False)
                table.add_column("Key", style="dim cyan", width=14)
                table.add_column("Value")
                table.add_row("Name",  p.get("name", "—"))
                table.add_row("Goal",  p.get("goal", "Not set"))
                if p.get("tech_stack"):
                    table.add_row("Stack", ", ".join(p["tech_stack"]))
                if p.get("recent_files"):
                    table.add_row("Files", ", ".join(p["recent_files"][:3]))
                console.print(table)
            else:
                console.print("[dim]No active project. Use [bold]/project <name>[/bold][/dim]")

    elif cmd == "/memory":
        count = orchestrator.long_memory.count()
        short = len(orchestrator.short_memory)
        console.print(f"[cyan]Long-term:[/cyan] {count} documents")
        console.print(f"[cyan]Short-term:[/cyan] {short} exchanges")

    elif cmd == "/tools":
        tool_names = orchestrator.tools.list_tools()
        table = Table(title="Available Tools", border_style="cyan", header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Tool Name", style="cyan")
        for i, name in enumerate(tool_names, 1):
            table.add_row(str(i), name)
        console.print(table)

    elif cmd == "/voice":
        if not voice_manager:
            console.print(
                "[yellow]Voice not available. Run with --voice flag and install:[/yellow]\n"
                "  pip install faster-whisper sounddevice pyttsx3"
            )
        else:
            voice_output = not voice_output
            state = "[green]ON[/green]" if voice_output else "[red]OFF[/red]"
            console.print(f"[cyan]Voice output:[/cyan] {state}")
            return voice_output

    else:
        console.print(f"[red]Unknown command:[/red] {cmd}  — try [bold]/help[/bold]")

    return voice_output
