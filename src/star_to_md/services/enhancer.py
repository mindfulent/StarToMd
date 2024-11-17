from typing import List
import ell
from ..core.document import MarkdownResult
from ..config.settings import get_settings

class ContentEnhancer:
    """Service for enhancing markdown content"""
    
    def __init__(self):
        self.settings = get_settings()
    
    @ell.simple(model="gpt-4o-mini")
    async def enhance(self, content: str) -> str:
        """Enhance markdown content"""
        return [
            ell.system("You are an expert markdown enhancer focused on clarity and readability."),
            ell.user(
                "Enhance this markdown while preserving its structure and meaning:\n\n"
                f"{content}"
            )
        ]
    
    @ell.simple(model="gpt-4o-mini")
    async def combine(self, chunks: List[str]) -> MarkdownResult:
        """Combine markdown chunks"""
        separator = "\n---\n"
        return [
            ell.system("You are an expert at combining markdown sections."),
            ell.user(
                "Combine these markdown sections into a cohesive document:\n\n"
                f"{separator.join(chunks)}"
            )
        ] 