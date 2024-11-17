from typing import List
import ell
from ..core.document import MarkdownResult
from ..config.settings import get_settings

class ContentEnhancer:
    """Service for enhancing markdown content with versioning and tracing"""
    
    def __init__(self):
        self.settings = get_settings()
        # Initialize ell with storage and versioning
        ell.init(
            store='./logs/enhancer',
            verbose=self.settings.debug,
            autocommit=True
        )
    
    @ell.simple(model="gpt-4o-mini")
    async def enhance(self, content: str) -> str:
        """Enhance markdown content while preserving structure"""
        return [
            ell.system("""You are an expert markdown enhancer focused on:
                         1. Clarity and readability
                         2. Proper heading hierarchy
                         3. Consistent formatting
                         4. Accurate link references"""),
            ell.user(f"Enhance this markdown while preserving its structure and meaning:\n\n{content}")
        ]
    
    @ell.simple(model="gpt-4o-mini", temperature=0.2)
    async def combine(self, chunks: List[str]) -> MarkdownResult:
        """Combine markdown chunks intelligently"""
        return [
            ell.system("""You are an expert at combining markdown sections.
                         Ensure proper heading hierarchy and smooth transitions."""),
            ell.user("Combine these markdown sections into a cohesive document:\n\n" + 
                    "\n---\n".join(chunks))
        ]
    
    @ell.simple(model="gpt-4o-mini", temperature=0.1)
    async def validate_structure(self, content: str) -> bool:
        """Validate markdown structure"""
        return [
            ell.system("You are a markdown structure validator."),
            ell.user(f"""Validate this markdown structure. Return only 'true' or 'false'.
                        Check for:
                        1. Valid heading hierarchy
                        2. Proper list formatting
                        3. Complete code blocks
                        4. Valid link syntax
                        
                        Content:
                        {content}""")
        ]
    