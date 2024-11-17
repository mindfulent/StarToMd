from star_to_md.core import BaseProcessor
from star_to_md.core.document import StarDocument, MarkdownResult
from star_to_md.config.settings import Settings
from star_to_md.services.analyzer import PDFAnalyzer
from star_to_md.services.chunker import PDFChunker
from star_to_md.services.enhancer import ContentEnhancer
from star_to_md.utils.errors import ProcessorError

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