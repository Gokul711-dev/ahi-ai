"""
ui/cli.py
Polished Rich terminal interface.
"""
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

console = Console()


def print_banner():
    banner = """
[bold cyan]
    ___       __  __       ____ 
   /   |     / / / /      /  _/ 
  / /| |    / /_/ /       / /   
 / ___ |_  / __  /  _   _/ /    
/_/  |_(_)/_/ /_/  (_) /___/    
[/bold cyan]
[dim]Artificial Human Intelligence — Phase 1 (Local Core)[/dim]
    """
    console.print(banner)


def run_cli(orchestrator):
    print_banner()
    console.print("[green]Jane is online and ready. Type 'exit' to quit.[/green]\n")

    # Prompt toolkit style
    style = Style.from_dict({
        'prompt': 'ansicyan bold',
    })
    session = PromptSession(style=style)

    while True:
        try:
            user_input = session.prompt("You > ")
            if not user_input.strip():
                continue
                
            if user_input.lower() in ["exit", "quit"]:
                console.print("[dim]Jane: Goodbye. I'll be here in my mental palace.[/dim]")
                break
                
            # Handle special slash commands
            if user_input.startswith("/"):
                handle_command(user_input, orchestrator)
                continue

            with console.status("[dim]Jane is thinking...[/dim]"):
                response = orchestrator.process(user_input)

            # Print Jane's response in a panel
            console.print(Panel(Markdown(response), title="[bold magenta]Jane[/bold magenta]", border_style="magenta"))
            print()

        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            console.print(f"[bold red]Critical Error:[/bold red] {e}")


def handle_command(cmd_text: str, orchestrator):
    parts = cmd_text.split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd == "/clear":
        orchestrator.short_memory.clear()
        console.print("[yellow]Short-term memory cleared.[/yellow]")
    elif cmd == "/project":
        if args:
            orchestrator.project_state.set_project(args)
            console.print(f"[green]Switched to project: {args}[/green]")
        else:
            p = orchestrator.project_state.get_active()
            if p:
                console.print(f"[cyan]Active Project: {p['name']}[/cyan]")
            else:
                console.print("[dim]No active project.[/dim]")
    else:
        console.print(f"[red]Unknown command: {cmd}[/red]")
