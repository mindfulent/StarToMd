from typing import List
import pypdf
from ..core.document import StarDocument
from ..config.settings import get_settings
import ell

class PDFChunker:
    """Service for chunking PDF documents"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def chunk(self, doc: StarDocument) -> List[str]:
        """Split PDF into processable chunks"""
        if not doc.path:
            raise ValueError("Document path is required for PDF chunking")
            
        with open(doc.path, 'rb') as file:
            pdf = pypdf.PdfReader(file)
            chunks = []
            current_chunk = []
            current_size = 0
            
            for page in pdf.pages:
                text = page.extract_text()
                estimated_tokens = len(text) // 4
                
                if current_size + estimated_tokens > self.settings.max_chunk_size:
                    # Save current chunk and start new one
                    if current_chunk:
                        chunks.append('\n'.join(current_chunk))
                    current_chunk = [text]
                    current_size = estimated_tokens
                else:
                    current_chunk.append(text)
                    current_size += estimated_tokens
            
            # Add final chunk
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
            
            return await self._optimize_chunks(chunks)
    
    @ell.simple(model="gpt-4o-mini")
    async def _optimize_chunks(self, chunks: List[str]) -> List[str]:
        """Optimize chunk boundaries using LLM"""
        return [
            ell.system("You are a document chunking specialist."),
            ell.user(f"""
            Optimize these document chunks by:
            1. Ensuring semantic completeness
            2. Avoiding mid-sentence breaks
            3. Preserving section boundaries
            
            Chunks:
            {chunks}
            """)
        ] 