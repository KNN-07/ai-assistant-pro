"""Enhanced logging configuration for AI Assistant Pro."""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LogEntry:
    """Represents a single log entry."""
    timestamp: datetime
    level: str
    message: str
    
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'message': self.message
        }


class GUILogHandler(logging.Handler):
    """Handler that forwards logs to a GUI callback."""
    
    def __init__(self, callback: Callable[[str, str, str], None]):
        """
        Initialize GUI log handler.
        
        Args:
            callback: Function(timestamp, level, message) to call for each log
        """
        super().__init__()
        self.callback = callback
        self.setFormatter(logging.Formatter('%(message)s'))
    
    def emit(self, record: logging.LogRecord) -> None:
        try:
            timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
            level = record.levelname
            message = self.format(record)
            self.callback(timestamp, level, message)
        except Exception:
            pass  # Silently ignore GUI errors


class LogManager:
    """Centralized log management with GUI support."""
    
    _instance: Optional['LogManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._logger: Optional[logging.Logger] = None
        self._gui_handlers: list[GUILogHandler] = []
        self._log_history: list[LogEntry] = []
        self._max_history = 1000
    
    def setup(
        self,
        name: str = "ai_assistant_pro",
        log_level: str = "INFO",
        save_logs: bool = True,
        log_dir: str = "logs"
    ) -> logging.Logger:
        """
        Set up the application logger.
        
        Args:
            name: Logger name
            log_level: Logging level
            save_logs: Whether to save logs to file
            log_dir: Directory for log files
            
        Returns:
            Configured logger instance
        """
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        self._logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # File handler (if enabled)
        if save_logs:
            log_path = Path(log_dir)
            log_path.mkdir(exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_path / "ai_assistant.log",
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=3,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        
        # History handler (internal tracking)
        self._logger.addHandler(self._create_history_handler())
        
        return self._logger
    
    def _create_history_handler(self) -> logging.Handler:
        """Create a handler that stores logs in memory."""
        handler = logging.Handler()
        handler.emit = lambda record: self._store_log(record)
        return handler
    
    def _store_log(self, record: logging.LogRecord) -> None:
        """Store log entry in history."""
        entry = LogEntry(
            timestamp=datetime.fromtimestamp(record.created),
            level=record.levelname,
            message=record.getMessage()
        )
        self._log_history.append(entry)
        
        # Trim history if too long
        if len(self._log_history) > self._max_history:
            self._log_history = self._log_history[-self._max_history:]
    
    def add_gui_handler(self, callback: Callable[[str, str, str], None]) -> GUILogHandler:
        """
        Add a GUI log handler.
        
        Args:
            callback: Function to call with (timestamp, level, message)
            
        Returns:
            The created handler (can be used to remove later)
        """
        if self._logger is None:
            self.setup()
        
        handler = GUILogHandler(callback)
        self._gui_handlers.append(handler)
        if self._logger:
            self._logger.addHandler(handler)
        return handler
    
    def remove_gui_handler(self, handler: GUILogHandler) -> None:
        """Remove a GUI log handler."""
        if handler in self._gui_handlers:
            self._gui_handlers.remove(handler)
            if self._logger:
                self._logger.removeHandler(handler)
    
    def get_history(self, limit: int = 100) -> list[LogEntry]:
        """Get recent log history."""
        return self._log_history[-limit:]
    
    @property
    def logger(self) -> logging.Logger:
        if self._logger is None:
            self.setup()
        return self._logger  # type: ignore[return-value]


# Module-level convenience functions
_log_manager = LogManager()


def setup_logger(
    name: str = "ai_assistant_pro",
    log_level: str = "INFO",
    save_logs: bool = True
) -> logging.Logger:
    """Set up and return the application logger."""
    return _log_manager.setup(name=name, log_level=log_level, save_logs=save_logs)


def get_logger() -> logging.Logger:
    """Get the application logger instance."""
    return _log_manager.logger


def get_log_manager() -> LogManager:
    """Get the log manager instance."""
    return _log_manager
