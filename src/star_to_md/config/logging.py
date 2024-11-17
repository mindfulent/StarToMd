import logging
from pathlib import Path
from rich.logging import RichHandler
import sys

def setup_logging(debug: bool = False) -> None:
    """Configure application logging"""
    log_dir = Path('./logs')
    log_dir.mkdir(exist_ok=True)
    
    # Set log level based on debug flag
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Create handlers
    file_handler = logging.FileHandler(log_dir / 'star_to_md.log')
    file_handler.setLevel(log_level)
    
    error_handler = logging.FileHandler(log_dir / 'errors.log')
    error_handler.setLevel(logging.ERROR)
    
    console_handler = RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[file_handler, error_handler, console_handler]
    )
    
    # Get logger for this module
    logger = logging.getLogger('star_to_md')
    
    if debug:
        # Add debug file handler
        debug_handler = logging.FileHandler(log_dir / 'debug.log')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        logger.addHandler(debug_handler)
        
        # Log some debug info
        logger.debug("Debug mode enabled")
        logger.debug(f"Python version: {sys.version}")
        logger.debug(f"Log directory: {log_dir.absolute()}") 