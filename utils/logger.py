"""
Logging Configuration

Centralized logging setup for FODEMIR-Sim application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logger(name: str = 'fodemir_sim', 
                log_level: str = 'INFO',
                log_to_file: bool = True,
                log_file: Optional[Path] = None) -> logging.Logger:
    """
    Setup logger with console and optional file handlers.
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_file: Path to log file (default: logs/fodemir_sim_YYYYMMDD.log)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Set logging level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        if log_file is None:
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = log_dir / f'fodemir_sim_{timestamp}.log'
        else:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_file}")
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = 'fodemir_sim') -> logging.Logger:
    """
    Get existing logger instance.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerContext:
    """Context manager for temporary logger configuration."""
    
    def __init__(self, logger: logging.Logger, level: str):
        """
        Initialize logger context.
        
        Args:
            logger: Logger instance
            level: Temporary logging level
        """
        self.logger = logger
        self.new_level = getattr(logging, level.upper(), logging.INFO)
        self.old_level = None
    
    def __enter__(self):
        """Store current level and set new level."""
        self.old_level = self.logger.level
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original logging level."""
        self.logger.setLevel(self.old_level)


