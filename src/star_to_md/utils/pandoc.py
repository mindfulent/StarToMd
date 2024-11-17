import shutil
import subprocess
from typing import Optional
from ..config.settings import get_settings

def get_pandoc_path() -> Optional[str]:
    """Get the path to the pandoc executable"""
    settings = get_settings()
    
    # Check settings first
    if settings.pandoc_path:
        if shutil.which(settings.pandoc_path):
            return settings.pandoc_path
    
    # Check system PATH
    pandoc_path = shutil.which('pandoc')
    if pandoc_path:
        return pandoc_path
    
    return None

def check_pandoc_version() -> Optional[str]:
    """Check pandoc version and return version string if available"""
    pandoc_path = get_pandoc_path()
    if not pandoc_path:
        return None
        
    try:
        result = subprocess.run(
            [pandoc_path, '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.split('\n')[0]  # First line contains version
    except subprocess.SubprocessError:
        return None

def is_pandoc_available() -> bool:
    """Check if pandoc is available for use"""
    return get_pandoc_path() is not None
