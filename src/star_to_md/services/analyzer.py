from typing import Dict, Any
import ell
from PyPDF2 import PdfReader

class PDFAnalyzer:
    """Service for analyzing PDF documents"""
    
    async def analyze(self, doc) -> Dict[str, Any]:
        """Public method to analyze PDF document"""
        if not doc.pdf:
            raise ValueError("PDF document not initialized")
        return await self._analyze_structure(doc.pdf)
    
    @ell.complex(model="gpt-4o-mini")
    async def _analyze_structure(self, pdf: PdfReader) -> Dict[str, Any]:
        """Analyze PDF structure and extract key information."""
        # Extract text from first few pages for analysis
        text_sample = "\n".join(page.extract_text() for page in pdf.pages[:3])
        
        return [
            ell.system("""You are a PDF structure analyzer. Analyze the document structure and return a JSON object with:
                      - document_type: str (academic, business, technical, etc)
                      - heading_levels: int (number of heading levels detected)
                      - has_tables: boolean
                      - has_code_blocks: boolean
                      - estimated_complexity: float (0-1)"""),
            ell.user(f"Analyze this PDF content:\n\n{text_sample}")
        ]