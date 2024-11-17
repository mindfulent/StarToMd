from star_to_md.core.registry import ProcessorRegistry
from star_to_md.processors.hybrid.pdf import PdfProcessor

def register_processors():
    """Register all available processors"""
    registry = ProcessorRegistry()
    registry.register("pdf", PdfProcessor)

# Register processors on import
register_processors()