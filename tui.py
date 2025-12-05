#!/usr/bin/env python3
"""
LiaAI – Professional Left-Aligned TUI (White Text • Modern Design)
Inspired by: Gemini CLI • Claude • Warp • Perplexity
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from rich.align import Align

try:
    from rich.console import Console, Group
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.rule import Rule
    from rich.live import Live
    from rich.text import Text
    from rich.padding import Padding
except ImportError:
    print("Rich library not found. Install with: pip install rich")
    sys.exit(1)

from core.lia_main import LiaMain


class LiaTUI:
    def __init__(self):
        self.console = Console()
        self.lia = None
        self.initialize_lia()

    def initialize_lia(self):
        api_key = os.getenv("COHERE_API_KEY", "doeM32W2so3ubfYYs673lmiOmUzwN15weKfB68bj")
        try:
            self.lia = LiaMain(api_key=api_key, memory_file="Hound_memory.json")
        except Exception as e:
            self.console.print(f"[bold red]Failed to initialize LiaAI: {e}[/bold red]")
            sys.exit(1)

    def header(self):
        # ───── HoundAI ASCII Logo ─────
        logo = Text(
            " ██╗  ██╗ ██████╗ ██╗   ██╗███╗   ██╗██████╗ \n"
            " ██║  ██║██╔═══██╗██║   ██║████╗  ██║██╔══██╗\n"
            " ███████║██║   ██║██║   ██║██╔██╗ ██║██║  ██║\n"
            " ██╔══██║██║   ██║██║   ██║██║╚██╗██║██║  ██║\n"
            " ██║  ██║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝\n"
            " ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ \n",
            style="bold #a78bfa"
        )

        subtitle = Text("Cybersecurity • Threat Hunting • Intelligence", style="bold #c4b5fd")
        tagline  = Text("Always watching. Always ready.", style="dim white")

        # Group everything and center the subtitle/tagline inside the panel
        content = Group(
            logo,
            "\n",
            Align.center(subtitle),
            Align.center(tagline)
        )

        banner = Panel(
            content,
            style="on #0f0f1a",
            border_style="#4c1d95",
            padding=(2, 6),
            expand=False,
        )

        # Finally center the entire panel on screen
        return Align.center(banner)

    def user_message(self, text: str):
        label = Text("You", style="bold #c4b5fd")
        content = Text(f"  {text}", style="white")
        bubble = Panel(
            Group(label, content),
            style="on #1e1b4b",
            border_style="#6366f1",
            padding=(1, 2),
            expand=False,
        )
        return Padding(bubble, pad=(0, 4, 1, 0))  # Left-aligned with margin

    def assistant_message(self, text: str):
        label = Text("HoundAI\n", style="bold #22d3ee")
        try:
            md = Markdown(
                text,
                code_theme="one-dark",
                inline_code_lexer="bash",
                style="white"
            )
            content = md
        except:
            content = Text(text, style="white")

        bubble = Panel(
            Group(label, content),
            style="on #0f0f1a",
            border_style="#22d3ee",
            padding=(1, 2),
            expand=False,
        )
        return Padding(bubble, pad=(0, 4, 1, 0))  # Left-aligned

    def thinking(self):
        return Padding(
            Text("● LiaAI is thinking...", style="white dim"),
            pad=(0, 4)
        )

    def run(self):
        self.console.clear()
        self.console.print(self.header())
        self.console.print(Rule(style="#4c1d95"))
        self.console.print(Text("Type your message • ", style="dim white") +
                           Text("quit", style="bold yellow") +
                           Text(" or ", style="dim white") +
                           Text("exit", style="bold yellow") +
                           Text(" to leave\n", style="dim white"))

        # Initial greeting
        greeting = (
            "Hello! I'm **HoundAI**, your advanced cybersecurity assistant.\n\n"
            "**How can I assist you today?**"
        )
        self.console.print(self.assistant_message(greeting))
        self.console.print()

        while True:
            try:
                user_input = Prompt.ask(
                    Text("You ", style="bold #c4b5fd"),
                    console=self.console
                ).strip()

                if not user_input:
                    continue

                if user_input.lower() in {"quit", "exit", "bye", ":q", "goodbye"}:
                    farewell = Panel(
                        Text("Stay secure.\nUntil next time! 👋", style="white bold"),
                        style="on #0f0f1a",
                        border_style="#22d3ee",
                        padding=(1, 3)
                    )
                    self.console.print(Padding(farewell, (1, 4, 2, 0)))
                    break

                if user_input.lower() == "clear":
                    self.console.clear()
                    self.console.print(self.header())
                    self.console.print(Rule(style="#4c1d95"))
                    continue

                # Display user message
                self.console.print(self.user_message(user_input))
                self.console.print()

                # Thinking
                with Live(self.thinking(), refresh_per_second=8, console=self.console):
                    response = self.lia.process_input(user_input)

                # Display assistant response
                self.console.print(self.assistant_message(response))
                self.console.print()

            except KeyboardInterrupt:
                self.console.print("\n[dim]Interrupted. Type 'quit' to exit.[/]")
            except Exception as e:
                self.console.print(f"[bold red]Error: {e}[/]")


def main():
    app = LiaTUI()
    app.run()


if __name__ == "__main__":
    main()