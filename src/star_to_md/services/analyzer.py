from typing import Dict, Any
import ell
from PyPDF2 import PdfReader
from pydantic import BaseModel, Field
from ell.types import Message, ContentBlock

class PDFAnalysis(BaseModel):
    document_type: str = Field(description="Type of document (academic, business, technical, etc)")
    heading_levels: int = Field(description="Number of heading levels detected")
    has_tables: bool = Field(description="Whether document contains tables")
    has_code_blocks: bool = Field(description="Whether document contains code blocks")
    estimated_complexity: float = Field(description="Estimated complexity score (0-1)")

class PDFAnalyzer:
    """Service for analyzing PDF documents"""
    
    async def analyze(self, doc) -> Dict[str, Any]:
        """Public method to analyze PDF document"""
        if not doc.pdf:
            raise ValueError("PDF document not initialized")
        return await self._analyze_structure(doc.pdf)
    
    @ell.simple(model="gpt-4o-mini", temperature=0.2)
    async def _analyze_structure(self, pdf: PdfReader) -> PDFAnalysis:
        """Analyze PDF structure and extract key information."""
        # Extract text from first few pages for analysis
        text_sample = "\n".join(page.extract_text() for page in pdf.pages[:3])
        
        # Return the analysis prompt directly - ell.simple will handle message formatting
        return f"""Analyze this PDF content and determine:
        - The document type (academic, business, technical, etc)
        - Number of heading levels present
        - Whether it contains tables
        - Whether it contains code blocks
        - An estimated complexity score from 0-1

        Content:
        {text_sample}"""