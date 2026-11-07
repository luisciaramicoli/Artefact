import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from emporio_agent.agent.core import get_agent
from emporio_agent.db.seed import seed_database
from emporio_agent.rag.ingest_policy import ingest_policies

console = Console()


def run_cli():
    console.print(
        Panel.fit(
            "[bold cyan]🎸 Empório da Música — Assistente Virtual de Atendimento[/bold cyan]\n"
            "[dim]Atendimento Inteligente com IA Generativa (Gemini + Qdrant RAG + SQL)[/dim]\n"
            "[yellow]Digite 'sair' ou 'exit' para encerrar | 'limpar' para nova conversa[/yellow]",
            border_style="cyan"
        )
    )

    # Ensure database and vector store are ready
    try:
        seed_database()
        ingest_policies()
    except Exception as e:
        console.print(f"[red]Aviso durante inicialização: {e}[/red]")

    agent = get_agent()
    conversation_id = None

    console.print("[green]✓ Sistema pronto! Envie sua mensagem para o Empório da Música:[/green]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold green]Você[/bold green]")
            if not user_input.strip():
                continue

            clean_input = user_input.strip()
            if clean_input.lower() in ["sair", "exit", "quit", "q"]:
                console.print("[cyan]Empório da Música agradece sua visita! Até logo e boa música! 🎸[/cyan]")
                break

            if clean_input.lower() in ["limpar", "clear", "novo"]:
                conversation_id = None
                console.print("[yellow]Conversa reiniciada. Iniciando nova sessão.[/yellow]\n")
                continue

            with console.status("[bold cyan]Consultando sistemas da loja...[/bold cyan]"):
                res = agent.chat(clean_input, conversation_id=conversation_id)
                conversation_id = res["conversation_id"]

            # Display tool calls if any
            if res.get("tool_calls"):
                tools_used = ", ".join([f"{t['tool']}" for t in res["tool_calls"]])
                console.print(f"[dim italic]🔧 Ferramentas acionadas: {tools_used}[/dim italic]")

            console.print(Panel(Markdown(res["message"]), title="[bold magenta]Empório da Música[/bold magenta]", border_style="magenta"))
            console.print()

        except KeyboardInterrupt:
            console.print("\n[cyan]Até logo![/cyan]")
            break
        except Exception as e:
            console.print(f"[red]Erro durante a conversa: {e}[/red]\n")


if __name__ == "__main__":
    run_cli()
