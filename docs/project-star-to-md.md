# * To MD (Star To MD) - Modern Implementation Plan

## 1. Project Architecture

```text
star_to_md/
├── .github/                    # CI/CD workflows
├── src/
│   └── star_to_md/
│       ├── config/            # Configuration management
│       │   ├── __init__.py
│       │   ├── settings.py    # Pydantic settings
│       │   └── logging.py     # Logging configuration
│       │
│       ├── core/              # Core functionality
│       │   ├── document.py    # Document models
│       │   ├── processor.py   # Base processor
│       │   └── registry.py    # Plugin registry
│       │
│       ├── processors/        # Format processors
│       │   ├── pandoc/        # Direct pandoc processors
│       │   ├── hybrid/        # Hybrid processors
│       │   └── custom/        # Custom processors
│       │
│       ├── services/          # Business logic services
│       │   ├── analyzer.py    # Content analysis
│       │   ├── chunker.py     # Content chunking
│       │   └── enhancer.py    # Content enhancement
│       │
│       ├── llm/              # LLM integration
│       │   ├── client.py     # LLM client
│       │   ├── prompts.py    # Prompt templates
│       │   └── callbacks.py  # LLM callbacks
│       │
│       └── utils/            # Utilities
           ├── monitoring.py  # Telemetry
           ├── errors.py     # Error handling
           └── validation.py # Validation utilities
```

## 1.1 Integration with ell Platform

The project leverages the ell platform for LLM interactions, providing:

1. **Simplified Message Handling**
   - Type-safe message construction
   - Automatic prompt versioning
   - Built-in monitoring

2. **Functional Programming Patterns**
   - Decorator-based LLM calls
   - Clean separation of concerns
   - Improved testability

3. **Performance & Monitoring**
   - Built-in telemetry
   - Request versioning
   - Cost tracking

Example usage:

```python
@ell.simple(model="gpt-4o-mini")
async def enhance_markdown(content: str):
"""You are an expert markdown enhancer."""
return [
ell.system("Enhance the markdown while preserving structure."),
ell.user(content)
    ]
```

This integration simplifies our LLM interactions while providing robust monitoring and versioning capabilities.

## 2. Core System Components

### 2.1 Configuration Management

```python
# src/star_to_md/config/settings.py
from pydantic_settings import BaseSettings
from typing import Dict, Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    app_name: str = "star_to_md"
    debug: bool = False
    
    # LLM Settings
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    
    # Processing Settings
    max_chunk_size: int = 4
    confidence_threshold: float = 0.8
    
    # Pandoc Settings
    pandoc_path: Optional[str] = None
    
    class Config:
        env_prefix = "STAR_TO_MD_"
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()
```

### 2.2 Error Handling

```python
# src/star_to_md/utils/errors.py
from typing import Optional
from dataclasses import dataclass

@dataclass
class ConversionError(Exception):
    """Base conversion error"""
    message: str
    source: Optional[Exception] = None
    document_id: Optional[str] = None
    
    def __str__(self) -> str:
        return f"{self.message} (doc: {self.document_id})"

class ProcessorError(ConversionError):
    """Processor-specific errors"""
    processor_name: str
    
class ValidationError(ConversionError):
    """Validation errors"""
    validation_errors: Dict[str, str]

class ErrorHandler:
    """Centralized error handling"""
    
    async def handle_error(self, error: Exception) -> Optional[str]:
        """Handle errors with potential recovery"""
        if isinstance(error, ProcessorError):
            return await self._handle_processor_error(error)
        elif isinstance(error, ValidationError):
            return await self._handle_validation_error(error)
        return None
        
    @ell.simple(model="gpt-4o-mini")
    async def _handle_processor_error(self, error: ProcessorError) -> Optional[str]:
        """Attempt to recover from processor errors"""
        return [
            ell.system("You are an error recovery specialist."),
            ell.user(f"""
            Error: {error.message}
            Processor: {error.processor_name}
            
            Attempt to recover from this error and suggest a solution.
            """)
        ]
```

### 2.3 Monitoring and Telemetry

```python
# src/star_to_md/utils/monitoring.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List

@dataclass
class ConversionMetrics:
    """Metrics for a conversion operation"""
    document_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    chunks_processed: int = 0
    llm_calls: int = 0
    token_usage: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

class MetricsCollector:
    """Collects and reports metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, ConversionMetrics] = {}
    
    def start_conversion(self, document_id: str) -> None:
        self.metrics[document_id] = ConversionMetrics(
            document_id=document_id,
            start_time=datetime.now()
        )
    
    def end_conversion(self, document_id: str) -> None:
        if document_id in self.metrics:
            self.metrics[document_id].end_time = datetime.now()
    
    def add_error(self, document_id: str, error: str) -> None:
        if document_id in self.metrics:
            self.metrics[document_id].errors.append(error)
```

## 3. Processor Implementation

### 3.1 Base Processor

```python
# src/star_to_md/core/processor.py
from abc import ABC, abstractmethod
from typing import Protocol

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
```

### 3.2 PDF Processor

```python
# src/star_to_md/processors/hybrid/pdf.py
from ...core import BaseProcessor
from ...services import PDFAnalyzer, PDFChunker, ContentEnhancer

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
        # Get chunks
        chunks = await self.chunker.chunk(doc)
        
        # Process chunks
        processed = []
        for chunk in chunks:
            try:
                # Process with pandoc
                pandoc_result = self._pandoc_convert(chunk)
                
                # Enhance with LLM
                enhanced = await self.enhancer.enhance(pandoc_result)
                
                processed.append(enhanced)
                
            except Exception as e:
                self.metrics.add_error(doc.id, str(e))
                if len(processed) == 0:
                    raise  # Re-raise if no successful chunks
                
        # Combine results
        return await self.enhancer.combine(processed)
```

## 4. Quality Control System

### 4.1 Validation Pipeline

```python
# src/star_to_md/utils/validation.py
from typing import List, Tuple

class ValidationPipeline:
    """Validation pipeline for conversion results"""
    
    def __init__(self):
        self.validators: List[Callable] = [
            self._validate_structure,
            self._validate_content,
            self._validate_formatting
        ]
    
    async def validate(self, result: MarkdownResult) -> Tuple[bool, List[str]]:
        """Run validation pipeline"""
        errors = []
        
        for validator in self.validators:
            try:
                await validator(result)
            except ValidationError as e:
                errors.extend(e.validation_errors.values())
                
        return len(errors) == 0, errors
    
    @ell.simple(model="gpt-4o-mini")
    async def _validate_structure(self, result: MarkdownResult) -> None:
        """Validate markdown structure"""
        return [
            ell.system("You are a markdown structure validator."),
            ell.user(f"""
            Content: {result.content}
            
            Validate the markdown structure and report any issues.
            Consider:
            1. Heading hierarchy
            2. List formatting
            3. Code blocks
            4. Link references
            5. Image references
            """)
        ]
```

## 5. CLI Implementation

```python
# src/star_to_md/cli.py
import typer
from rich.console import Console
from rich.progress import Progress
from pathlib import Path

app = typer.Typer()
console = Console()

@app.command()
def convert(
    source: Path = typer.Argument(..., help="Source file to convert"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
    format: Optional[str] = typer.Option(None, help="Force specific format"),
    config: Optional[Path] = typer.Option(None, help="Custom config file"),
):
    """Convert document to markdown"""
    # Load configuration
    settings = get_settings()
    if config:
        settings = Settings.parse_file(config)
    
    # Initialize processor
    processor = ProcessorRegistry.get(format or detect_format(source))
    
    with Progress() as progress:
        try:
            # Create document
            doc = StarDocument(path=source, format=format)
            
            # Convert
            task = progress.add_task("Converting...", total=100)
            result = processor.convert(doc)
            
            # Save or print
            if output:
                output.write_text(result.content)
                console.print(f"✓ Converted successfully to: {output}")
            else:
                console.print(result.content)
                
        except Exception as e:
            console.print(f"[red]Error: {str(e)}")
            raise typer.Exit(1)
```

This improved plan addresses several key aspects:

1. **Robust Error Handling**
   - Centralized error handling system
   - Error recovery strategies
   - Detailed error reporting

2. **Monitoring & Telemetry**
   - Conversion metrics collection
   - Performance monitoring
   - Error tracking

3. **Configuration Management**
   - Type-safe settings with Pydantic
   - Environment variable support
   - Configuration file support

4. **Quality Control**
   - Validation pipeline
   - LLM-based validation
   - Structured error reporting

5. **Developer Experience**
   - Clear project structure
   - Type hints throughout
   - Comprehensive documentation

6. **Performance**
   - Chunked processing
   - Async operations
   - Error recovery

Would you like me to elaborate on any particular aspect or provide more detailed implementations for specific components?