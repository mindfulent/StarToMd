import ell
from .settings import get_settings

def init_ell():
    """Initialize ell configuration"""
    settings = get_settings()
    
    # Configure ell
    ell.init(
        store='./logs/ell',  # Store ell logs in the logs directory
        verbose=settings.debug,  # Enable verbose mode in debug
        autocommit=True  # Enable automatic versioning
    )
