from typing import Dict, Optional, Any
from pathlib import Path
from pydantic import BaseModel, Field
from PyPDF2 import PdfReader

class StarDocument:
    """Document to be converted"""
    
    def __init__(
        self,
        id: str,
        content: str,
        format: str,
        path: Optional[Path] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.content = content
        self.format = format
        self.path = path
        self.metadata = metadata or {}
        self.pdf = None  # Initialize pdf attribute as None
        
        # If path exists and format is pdf, initialize the pdf reader
        if path and format.lower() == 'pdf':
            with open(path, 'rb') as file:
                self.pdf = PdfReader(file)

class MarkdownResult(BaseModel):
    """Result of markdown conversion"""
    
    content: str = Field(description="Converted markdown content")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the conversion"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the conversion"
    )
    
    class Config:
        arbitrary_types_allowed = True
    
    def __str__(self) -> str:
        return self.content