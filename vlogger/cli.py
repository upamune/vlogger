from typing import Optional
import typer
from rich.console import Console

from vlogger.commands.main_command import create_vlog
from vlogger.commands.gen_config import generate_config_command
from vlogger.commands.gen_schema import generate_schema_command

app = typer.Typer(help="A CLI tool to create Vlog videos with text overlays, BGM, etc.")
console = Console()


@app.command("create")
def create(
    config: str = typer.Option(..., "--config", "-c", help="Path to YAML configuration file"),
    output: str = typer.Option("output.mp4", "--output", "-o", help="Output filename")
):
    """
    Command to perform video editing and create the final Vlog.
    """
    create_vlog(config_path=config, output_path=output)


@app.command("generate-config")
def generate_config(
    directory: Optional[str] = typer.Option(None, "--dir", "-d", help="Directory path containing video files. If specified, auto-generates template configuration."),
    extension: str = typer.Option("mp4", "--extension", "-e", help="File extensions to search for videos (comma-separated)")
):
    """
    Command to auto-generate a configuration file template.
    """
    generate_config_command(directory=directory, extension=extension)


@app.command("generate-schema")
def generate_schema():
    """
    For developers: Command to generate JSON Schema file.
    """
    generate_schema_command()


def main():
    app()


if __name__ == "__main__":
    main()
