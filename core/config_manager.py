"""Enhanced configuration management for AI Assistant Pro."""
import json
from pathlib import Path
from typing import Any, Callable, Dict, List
from dataclasses import dataclass, field, asdict
from enum import Enum


class ScreenshotMode(Enum):
    """Screenshot capture modes."""
    FULL_SCREEN = "full_screen"
    ACTIVE_WINDOW = "active_window"
    REGION = "region"


@dataclass
class GeminiConfig:
    """Gemini API configuration."""
    api_keys: list[str] = field(default_factory=list)
    current_key_index: int = 0
    auto_rotate_on_quota_error: bool = True
    model: str = "gemini-2.5-flash-preview-05-20"
    system_prompt: str = (
        "You are a helpful assistant. Analyze this screenshot and provide "
        "a concise solution. Be direct and actionable. Focus on the most "
        "relevant information visible in the image."
    )


@dataclass
class AutoPasteConfig:
    """Auto-paste configuration."""
    enabled: bool = True
    delay_ms: int = 500
    restore_clipboard: bool = False


@dataclass 
class ScreenshotConfig:
    """Screenshot configuration."""
    mode: str = "full_screen"
    save_to_disk: bool = False
    output_dir: str = "screenshots"


@dataclass
class StartupConfig:
    """Startup configuration."""
    launch_on_boot: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    save_logs: bool = True


@dataclass
class UIConfig:
    """UI configuration."""
    theme: str = "dark"  # dark, light, system
    show_floating_widget: bool = True
    floating_widget_position: tuple[int, int] = (50, 50)
    main_window_geometry: str = "500x700"
    transparency: float = 0.95


@dataclass
class AppConfig:
    """Complete application configuration."""
    hotkey: str = "ctrl+shift+alt+a"
    capture_hotkey: str = "ctrl+shift+alt+c"
    gemini: GeminiConfig = field(default_factory=GeminiConfig)
    auto_paste: AutoPasteConfig = field(default_factory=AutoPasteConfig)
    screenshot: ScreenshotConfig = field(default_factory=ScreenshotConfig)
    startup: StartupConfig = field(default_factory=StartupConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    ui: UIConfig = field(default_factory=UIConfig)


class ConfigManager:
    """Enhanced configuration manager with type-safe access."""
    
    _DEFAULT_CONFIG_NAME = "config.json"
    
    def __init__(self, config_path: str = ""):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file (defaults to config.json in app directory)
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path(__file__).parent.parent / self._DEFAULT_CONFIG_NAME
        self._raw_config: Dict[str, Any] = {}
        self._observers: List[Callable[['ConfigManager'], None]] = []
        self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._raw_config = json.load(f)
            except json.JSONDecodeError:
                self._raw_config = self._get_default_dict()
                self.save()
        else:
            self._raw_config = self._get_default_dict()
            self.save()
    
    def save(self) -> None:
        """Save configuration to file."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self._raw_config, f, indent=2)
        self._notify_observers()
    
    def _notify_observers(self) -> None:
        """Notify all observers of config change."""
        from .logger import get_logger
        for observer in self._observers:
            try:
                observer(self)
            except Exception as e:
                try:
                    get_logger().warning(f"Config observer callback failed: {e}")
                except Exception:
                    pass
    
    def add_observer(self, callback: Callable[['ConfigManager'], None]) -> None:
        """Add a config change observer."""
        self._observers.append(callback)
    
    def remove_observer(self, callback: Callable[['ConfigManager'], None]) -> None:
        """Remove a config change observer."""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'gemini.api_key')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._raw_config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any, save: bool = True) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'gemini.api_key')
            value: Value to set
            save: Whether to save immediately
        """
        keys = key.split('.')
        config = self._raw_config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        
        if save:
            self.save()
    
    def _get_default_dict(self) -> Dict[str, Any]:
        """Get default configuration as dictionary."""
        config = AppConfig()
        return {
            "hotkey": config.hotkey,
            "capture_hotkey": config.capture_hotkey,
            "gemini": asdict(config.gemini),
            "auto_paste": asdict(config.auto_paste),
            "screenshot": asdict(config.screenshot),
            "startup": asdict(config.startup),
            "logging": asdict(config.logging),
            "ui": {
                "theme": config.ui.theme,
                "show_floating_widget": config.ui.show_floating_widget,
                "floating_widget_position": list(config.ui.floating_widget_position),
                "main_window_geometry": config.ui.main_window_geometry,
                "transparency": config.ui.transparency,
            }
        }
    
    # Convenience methods
    def get_hotkey(self) -> str:
        """Get main analysis hotkey."""
        return self.get('hotkey', 'ctrl+shift+alt+a')
    
    def get_capture_hotkey(self) -> str:
        """Get capture-only hotkey."""
        return self.get('capture_hotkey', 'ctrl+shift+alt+c')
    
    def get_system_prompt(self) -> str:
        """Get AI system prompt."""
        default = AppConfig().gemini.system_prompt
        return self.get('gemini.system_prompt', default)
    
    def get_api_key(self) -> str:
        """Get current active API key."""
        keys = self.get('gemini.api_keys', [])
        if not keys:
            return ''
        index = self.get('gemini.current_key_index', 0)
        if index >= len(keys):
            index = 0
            self.set('gemini.current_key_index', 0)
        return keys[index]
    
    def get_all_api_keys(self) -> list[str]:
        """Get all configured API keys."""
        return self.get('gemini.api_keys', [])
    
    def add_api_key(self, api_key: str) -> bool:
        """
        Add a new API key.
        
        Returns:
            True if added, False if already exists
        """
        keys = self.get_all_api_keys()
        if api_key and api_key not in keys:
            keys.append(api_key)
            self.set('gemini.api_keys', keys)
            return True
        return False
    
    def remove_api_key(self, api_key: str) -> bool:
        """
        Remove an API key.
        
        Returns:
            True if removed, False if not found
        """
        keys = self.get_all_api_keys()
        if api_key in keys:
            keys.remove(api_key)
            self.set('gemini.api_keys', keys)
            
            # Reset index if needed
            current_index = self.get('gemini.current_key_index', 0)
            if current_index >= len(keys) and keys:
                self.set('gemini.current_key_index', 0)
            return True
        return False
    
    def rotate_to_next_key(self) -> str:
        """
        Rotate to the next API key.
        
        Returns:
            The new current API key
        """
        keys = self.get_all_api_keys()
        if len(keys) <= 1:
            return self.get_api_key()
        
        current_index = self.get('gemini.current_key_index', 0)
        next_index = (current_index + 1) % len(keys)
        self.set('gemini.current_key_index', next_index)
        
        return keys[next_index]
    
    def is_auto_rotate_enabled(self) -> bool:
        """Check if automatic rotation on quota error is enabled."""
        return self.get('gemini.auto_rotate_on_quota_error', True)
    
    def is_auto_paste_enabled(self) -> bool:
        """Check if auto-paste is enabled."""
        return self.get('auto_paste.enabled', True)
    
    def get_paste_delay(self) -> int:
        """Get paste delay in milliseconds."""
        return self.get('auto_paste.delay_ms', 500)
    
    def get_theme(self) -> str:
        """Get current UI theme."""
        return self.get('ui.theme', 'dark')
    
    def set_theme(self, theme: str) -> None:
        """Set UI theme."""
        self.set('ui.theme', theme)
    
    def get_model(self) -> str:
        """Get Gemini model name."""
        return self.get('gemini.model', 'gemini-2.5-flash-preview-05-20')
