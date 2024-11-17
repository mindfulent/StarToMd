import ell
from typing import Optional, Dict
from dataclasses import dataclass, field
from pathlib import Path
import logging
from ..config.ell_config import init_ell

logger = logging.getLogger(__name__)

@dataclass
class ConversionError(Exception):
    """Base conversion error"""
    message: str
    document_id: str
    source: Optional[Exception] = None
    
    def __str__(self) -> str:
        return f"{self.message} (doc: {self.document_id})"

@dataclass
class ProcessorError(Exception):
    """Processor-specific errors"""
    message: str
    processor_name: str
    source: Optional[Exception] = None
    document_id: str = None
    
    def __str__(self) -> str:
        return f"{self.message} (processor: {self.processor_name}, doc: {self.document_id})"

@dataclass
class ValidationError(Exception):
    """Validation errors"""
    message: str
    validation_errors: Dict[str, str]
    document_id: str
    source: Optional[Exception] = None

class ErrorHandler:
    """Centralized error handling"""
    
    def __init__(self):
        # Ensure logs directory exists
        log_dir = Path('./logs')
        log_dir.mkdir(exist_ok=True)
        init_ell()  # Initialize ell if not already initialized
    
    async def handle_error(self, error: Exception) -> Optional[str]:
        """Handle errors with potential recovery"""
        try:
            if isinstance(error, ProcessorError):
                return await self._handle_processor_error(error)
            elif isinstance(error, ValidationError):
                return await self._handle_validation_error(error)
            return None
        except Exception as e:
            logger.error(f"Error during error handling: {str(e)}")
            return None
        
    @ell.simple(model="gpt-4o-mini")
    async def _handle_processor_error(self, error: ProcessorError) -> Optional[str]:
        """Attempt to recover from processor errors"""
        return {
            "messages": [
                {"role": "system", "content": "You are an error recovery specialist."},
                {"role": "user", "content": f"Error: {error.message}\n"
                         f"Processor: {error.processor_name}\n\n"
                         f"Attempt to recover from this error and suggest a solution."}
            ]
        }
    
    @ell.simple(model="gpt-4o-mini")
    async def _handle_validation_error(self, error: ValidationError) -> Optional[str]:
        """Attempt to recover from validation errors"""
        error_list = '\n'.join(f'- {k}: {v}' for k, v in error.validation_errors.items())
        return {
            "messages": [
                {"role": "system", "content": "You are a validation error recovery specialist."},
                {"role": "user", "content": f"Validation Errors:\n{error_list}\n\n"
                         f"Attempt to recover from these validation errors and suggest solutions."}
            ]
        }
