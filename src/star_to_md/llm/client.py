from typing import Optional, Dict, Any
import ell
from ..config.settings import get_settings
from ..config.ell_config import init_ell

class LLMClient:
    """Client for LLM interactions using ell"""
    
    def __init__(self):
        self.settings = get_settings()
        init_ell()  # Initialize ell if not already initialized
    
    @ell.simple(model="gpt-4o-mini")
    async def enhance_markdown(self, content: str) -> str:
        """You are an expert markdown enhancer focused on clarity and readability."""
        return [
            ell.system("Enhance the markdown while preserving structure and meaning."),
            ell.user(content)
        ]
    
    @ell.simple(model="gpt-4o-mini", temperature=0.1)
    async def validate_markdown(self, content: str) -> Dict[str, Any]:
        """You are a markdown validation specialist."""
        return [
            ell.system("""
            Validate the markdown structure and report any issues.
            Return a JSON object with:
            - valid: boolean
            - issues: list of strings (empty if valid)
            """),
            ell.user(content)
        ]