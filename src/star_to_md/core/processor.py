from abc import ABC, abstractmethod
from typing import Protocol
from .document import StarDocument, MarkdownResult
from ..config.settings import Settings, get_settings
from ..utils.errors import ErrorHandler, ValidationError
from ..utils.monitoring import MetricsCollector

class ProcessorProtocol(Protocol):
    """Protocol for processor implementations"""
    
    async def preprocess(self, doc: StarDocument) -> StarDocument:
        """Preprocess document"""
        ...
    
    async def convert(self, doc: StarDocument) -> MarkdownResult:
        """Convert document"""
        ...
    
    async def validate(self, result: MarkdownResult) -> bool:
        """Validate conversion result"""
        ...

class BaseProcessor(ProcessorProtocol):
    """Base processor implementation"""
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        self.metrics = MetricsCollector()
        self.error_handler = ErrorHandler()
    
    async def process(self, doc: StarDocument) -> MarkdownResult:
        """Main processing pipeline"""
        self.metrics.start_conversion(doc.id)
        
        try:
            # Preprocessing
            preprocessed = await self.preprocess(doc)
            
            # Conversion
            result = await self.convert(preprocessed)
            
            # Validation
            if not await self.validate(result):
                raise ValidationError("Validation failed", document_id=doc.id)
                
            return result
            
        except Exception as e:
            # Error handling
            recovery_result = await self.error_handler.handle_error(e)
            if recovery_result:
                return MarkdownResult(content=recovery_result, confidence=0.5)
            raise
            
        finally:
            self.metrics.end_conversion(doc.id) 