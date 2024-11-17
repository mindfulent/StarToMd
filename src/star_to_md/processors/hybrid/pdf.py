from star_to_md.core import BaseProcessor
from star_to_md.core.document import StarDocument, MarkdownResult
from star_to_md.config.settings import Settings
from star_to_md.services.analyzer import PDFAnalyzer
from star_to_md.services.chunker import PDFChunker
from star_to_md.services.enhancer import ContentEnhancer
from star_to_md.utils.errors import ProcessorError
from star_to_md.utils.pandoc import is_pandoc_available, get_pandoc_path
import tempfile
import subprocess
import ell

class PdfProcessor(BaseProcessor):
    """PDF processor implementation"""
    
    def __init__(self, settings: Settings = None):
        super().__init__(settings)
        self.analyzer = PDFAnalyzer()
        self.chunker = PDFChunker()
        self.enhancer = ContentEnhancer()
    
    async def preprocess(self, doc: StarDocument) -> StarDocument:
        """Analyze and prepare PDF"""
        analysis = await self.analyzer.analyze(doc)
        doc.metadata["analysis"] = analysis
        return doc
    
    async def convert(self, doc: StarDocument) -> MarkdownResult:
        """Convert PDF to markdown"""
        try:
            # Get chunks
            chunks = await self.chunker.chunk(doc)
            
            # Process chunks
            processed = []
            for chunk in chunks:
                try:
                    # Process with pandoc
                    pandoc_result = await self._pandoc_convert(chunk)
                    
                    # Enhance with LLM
                    enhanced = await self.enhancer.enhance(pandoc_result)
                    
                    processed.append(enhanced)
                    
                except Exception as e:
                    self.metrics.add_error(doc.id, str(e))
                    if len(processed) == 0:
                        raise ProcessorError(
                            message=str(e),
                            processor_name="PdfProcessor",
                            document_id=doc.id,
                            source=e
                        )
            
            # Combine results
            return await self.enhancer.combine(processed)
        except Exception as e:
            if not isinstance(e, ProcessorError):
                raise ProcessorError(
                    message="Failed to convert PDF",
                    processor_name="PdfProcessor",
                    source=e,
                    document_id=doc.id
                )
            raise
    
    async def validate(self, result: MarkdownResult) -> bool:
        """Validate the conversion result"""
        if not result.content:
            return False
        return result.confidence >= self.settings.confidence_threshold 
    
    async def _pandoc_convert(self, chunk: str) -> str:
        """Convert chunk using pandoc if available"""
        if not is_pandoc_available():
            # Fall back to direct LLM conversion if pandoc isn't available
            return await self._direct_convert(chunk)
        
        pandoc_path = get_pandoc_path()
        try:
            # Write chunk to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as temp_in:
                temp_in.write(chunk)
                temp_in.flush()
                
                # Run pandoc conversion
                result = subprocess.run(
                    [pandoc_path, temp_in.name, '-f', 'plain', '-t', 'markdown'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout
        except subprocess.SubprocessError as e:
            # Log error and fall back to direct conversion
            self.metrics.add_error(
                "pandoc_conversion",
                f"Pandoc conversion failed: {str(e)}"
            )
            return await self._direct_convert(chunk)
    
    @ell.simple(model="gpt-4o-mini")
    async def _direct_convert(self, chunk: str) -> str:
        """Direct conversion using LLM when pandoc isn't available"""
        return [
            ell.system("Convert the following text to clean markdown format."),
            ell.user(chunk)
        ]