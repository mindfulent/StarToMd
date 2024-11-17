import typer
from rich.console import Console
from pathlib import Path
from typing import Optional
import asyncio
from functools import wraps
from .config.settings import get_settings
from .config.logging import setup_logging
from .core.document import StarDocument
from .core.registry import ProcessorRegistry
from .utils.errors import ErrorHandler

app = typer.Typer()
console = Console()
error_handler = ErrorHandler()

def coro(f):
    """Decorator to run async functions"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

@app.command()
@coro
async def convert(
    source: Path = typer.Argument(..., help="Source file to convert"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
    format: Optional[str] = typer.Option(None, help="Force specific format"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
):
    """Convert document to markdown"""
    try:
        # Setup logging
        setup_logging(debug)
        
        # Load settings
        settings = get_settings()
        settings.debug = debug
        
        # Initialize processor
        processor = ProcessorRegistry().create_processor(format or "pdf")
        
        # Create document
        doc = StarDocument(
            id=str(source),
            content="",  # Will be loaded by processor
            format=format or "pdf",
            path=source
        )
        
        # Process document
        result = await processor.process(doc)
        
        # Save or print result
        if output:
            output.write_text(str(result))
            console.print(f"✓ Converted successfully to: {output}")
        else:
            console.print(str(result))
            
    except Exception as e:
        if debug:
            console.print_exception()
        else:
            console.print(f"[red]Error: {str(e)}")
        raise typer.Exit(1)

def main():
    """Entry point for the CLI application"""
    app()

if __name__ == "__main__":
    main() 