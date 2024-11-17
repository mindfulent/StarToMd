from ell import ell
from PyPDF2 import PdfReader
from typing import Dict, Any
from star_to_md.models.document import StarDocument
from ell.types import Message, ContentBlock

class PDFAnalyzer:
    async def analyze(self, doc: StarDocument) -> Dict[str, Any]:
        """Public method to analyze PDF document"""
        if not doc.pdf:
            raise ValueError("PDF document not initialized")
        return await self._analyze_structure(doc.pdf)

    @ell.complex(model="gpt-4o-mini")
    async def _analyze_structure(self, pdf: PdfReader) -> Dict[str, Any]:
        """Analyze PDF structure and return metadata"""
        # Create a list of messages for the language model
        messages = [
            Message(
                role="user",
                content=[ContentBlock(text=f"Analyze the structure of this PDF document: {pdf}")]
            )
        ]
        # Return the messages list directly - this is what ell.complex expects
        return messages