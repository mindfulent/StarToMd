import typer
import asyncio
from pathlib import Path
from pdf_to_md import pdf_to_markdown

app = typer.Typer()

@app.command()
def convert(
    pdf: Path = typer.Argument(..., help="PDF file to convert"),
    output: Path = typer.Option(None, help="Output markdown file")
):
    """Convert PDF to markdown"""
    try:
        # Create and run the async task
        result = asyncio.run(pdf_to_markdown(pdf, output))
            
        if output:
            print(f"Converted PDF saved to {output}")
        else:
            print(result)
    except Exception as e:
        print(f"Error: {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()