from pathlib import Path
import subprocess
import tempfile
import ell
from typing import Optional

def is_pandoc_available() -> bool:
    """Check if pandoc is installed"""
    try:
        subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def convert_with_pandoc(pdf_path: Path) -> str:
    """Convert PDF to markdown using pandoc"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as temp:
        # First convert PDF to text
        result = subprocess.run(
            ['pdftotext', str(pdf_path), temp.name],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Then convert text to markdown
        result = subprocess.run(
            ['pandoc', temp.name, '-f', 'plain', '-t', 'markdown'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout

@ell.simple(model="gpt-4o-mini")
async def convert_with_llm(text: str) -> str:
    """Convert text to markdown using LLM when pandoc isn't available"""
    return [
        ell.system("Convert the following text to clean markdown format."),
        ell.user(text)
    ]

async def pdf_to_markdown(pdf_path: Path, output_path: Optional[Path] = None) -> str:
    """Convert PDF to markdown, using pandoc if available, falling back to LLM"""
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
    try:
        # Try pandoc first if available
        if is_pandoc_available():
            markdown = convert_with_pandoc(pdf_path)
        else:
            # Fall back to LLM conversion
            with open(pdf_path, 'rb') as f:
                text = subprocess.run(
                    ['pdftotext', '-', '-'],
                    input=f.read(),
                    capture_output=True,
                    text=True,
                    check=True
                ).stdout
                markdown = await convert_with_llm(text)
        
        # Save or return
        if output_path:
            output_path.write_text(markdown)
            return f"Converted successfully to: {output_path}"
        return markdown
    except Exception as e:
        raise Exception(f"Failed to convert PDF: {str(e)}")
