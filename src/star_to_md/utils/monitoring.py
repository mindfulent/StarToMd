from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List
import logging
import os
from pathlib import Path

# Configure logging
log_dir = Path('./logs')
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    filename=log_dir / 'star_to_md.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
            # Log error to file
            logging.error(f"Document {document_id}: {error}")
    