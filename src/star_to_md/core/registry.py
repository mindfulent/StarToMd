from typing import Dict, Type, Optional
from .processor import BaseProcessor, ProcessorProtocol
from ..utils.errors import ProcessorError

class ProcessorRegistry:
    """Registry for document processors"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.processors: Dict[str, Type[ProcessorProtocol]] = {}
        return cls._instance
    
    def register(self, format_type: str, processor_class: Type[ProcessorProtocol]) -> None:
        """Register a processor for a specific format"""
        self.processors[format_type.lower()] = processor_class
    
    def get_processor(self, format_type: str) -> Optional[Type[ProcessorProtocol]]:
        """Get processor for a specific format"""
        return self.processors.get(format_type.lower())
    
    def create_processor(self, format_type: str, **kwargs) -> ProcessorProtocol:
        """Create a processor instance for a specific format"""
        processor_class = self.get_processor(format_type)
        if not processor_class:
            raise ProcessorError(
                message=f"No processor found for format: {format_type}",
                processor_name="registry"
            )
        return processor_class(**kwargs)