from typing import Dict, Any, Optional
from ..utils.monitoring import MetricsCollector

class LLMCallbacks:
    """Callbacks for LLM interactions"""
    
    def __init__(self):
        self.metrics = MetricsCollector()
    
    async def on_llm_start(self, document_id: str) -> None:
        """Called when LLM processing starts"""
        self.metrics.start_conversion(document_id)
    
    async def on_llm_end(self, document_id: str, response: Dict[str, Any]) -> None:
        """Called when LLM processing completes"""
        if 'usage' in response:
            # Track token usage
            self.metrics.add_token_usage(
                document_id,
                response['usage'].get('total_tokens', 0)
            )
        self.metrics.end_conversion(document_id)
    
    async def on_llm_error(self, document_id: str, error: Exception) -> None:
        """Called when LLM processing encounters an error"""
        self.metrics.add_error(document_id, str(error)) 