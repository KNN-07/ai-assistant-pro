"""System tray integration for AI Assistant Pro."""
import os
from pathlib import Path
from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import pystray
    from PIL import Image


class SystemTray:
    """Manages system tray icon and menu."""
    
    def __init__(
        self,
        on_toggle: Optional[Callable[[bool], None]] = None,
        on_settings: Optional[Callable[[], None]] = None,
        on_show_main: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[], None]] = None,
        assets_dir: str = "assets"
    ):
        """
        Initialize system tray.
        
        Args:
            on_toggle: Callback for enable/disable toggle
            on_settings: Callback for settings menu item
            on_show_main: Callback for showing main window
            on_exit: Callback for exit menu item
            assets_dir: Directory containing icon assets
        """
        self.on_toggle = on_toggle
        self.on_settings = on_settings
        self.on_show_main = on_show_main
        self.on_exit = on_exit
        self.assets_dir = Path(assets_dir)
        
        self.icon: Optional['pystray.Icon'] = None
        self.is_enabled = True
        self.is_processing = False
        self.hotkey_text = "Ctrl+Shift+Alt+A"
        self.queue_count = 0
        
        self._logger = None
        
        # Load icons
        self.icon_enabled = self._load_icon("icon.png")
        self.icon_disabled = self._load_icon("icon_disabled.png")
    
    @property
    def logger(self):
        if self._logger is None:
            from .logger import get_logger
            self._logger = get_logger()
        return self._logger
    
    def _load_icon(self, filename: str) -> 'Image.Image':
        """Load icon from file or create default."""
        from PIL import Image
        
        path = self.assets_dir / filename
        
        try:
            if path.exists():
                return Image.open(path)
            else:
                self.logger.warning(f"Icon not found: {path}, using default")
                return self._create_default_icon()
        except Exception as e:
            self.logger.error(f"Error loading icon: {e}")
            return self._create_default_icon()
    
    def _create_default_icon(self, color: tuple = (70, 130, 180)) -> 'Image.Image':
        """Create a simple default icon."""
        from PIL import Image, ImageDraw
        
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a circle
        margin = 4
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=color,
            outline=(255, 255, 255)
        )
        
        return img
    
    def _create_menu(self) -> 'pystray.Menu':
        """Create system tray menu."""
        import pystray
        
        return pystray.Menu(
            pystray.MenuItem(
                lambda _: f"{'✓' if self.is_enabled else '✗'} AI Assistant Pro",
                lambda: None,
                enabled=False
            ),
            pystray.MenuItem(
                lambda _: f"Hotkey: {self.hotkey_text}",
                lambda: None,
                enabled=False
            ),
            pystray.MenuItem(
                lambda _: f"Queue: {self.queue_count}" if self.queue_count > 0 else "",
                lambda: None,
                enabled=False,
                visible=lambda _: self.queue_count > 0
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Show Window",
                self._handle_show_main
            ),
            pystray.MenuItem(
                lambda _: "Disable" if self.is_enabled else "Enable",
                self._handle_toggle
            ),
            pystray.MenuItem(
                "Settings...",
                self._handle_settings
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Exit",
                self._handle_exit
            )
        )
    
    def _handle_toggle(self, icon, item) -> None:
        """Handle enable/disable toggle."""
        self.is_enabled = not self.is_enabled
        
        icon.icon = self.icon_enabled if self.is_enabled else self.icon_disabled
        
        status = "Enabled" if self.is_enabled else "Disabled"
        icon.title = f"AI Assistant Pro - {status}"
        
        if self.on_toggle:
            self.on_toggle(self.is_enabled)
        
        self.logger.info(f"AI Assistant {'enabled' if self.is_enabled else 'disabled'}")
        icon.update_menu()
    
    def _handle_settings(self, icon, item) -> None:
        """Handle settings menu click."""
        if self.on_settings:
            self.on_settings()
    
    def _handle_show_main(self, icon, item) -> None:
        """Handle show main window click."""
        if self.on_show_main:
            self.on_show_main()
    
    def _handle_exit(self, icon, item) -> None:
        """Handle exit menu click."""
        self.logger.info("Exiting AI Assistant Pro")
        
        if self.on_exit:
            self.on_exit()
        
        icon.stop()
    
    def run(self) -> None:
        """Run the system tray icon (blocking)."""
        import pystray
        
        try:
            self.icon = pystray.Icon(
                "ai_assistant_pro",
                self.icon_enabled,
                "AI Assistant Pro - Enabled",
                menu=self._create_menu()
            )
            
            self.logger.info("System tray icon started")
            self.icon.run()
            
        except Exception as e:
            self.logger.error(f"Error running system tray: {e}")
            raise
    
    def run_detached(self) -> None:
        """Run system tray in a separate thread (non-blocking)."""
        import pystray
        
        try:
            self.icon = pystray.Icon(
                "ai_assistant_pro",
                self.icon_enabled,
                "AI Assistant Pro - Enabled",
                menu=self._create_menu()
            )
            
            self.icon.run_detached()
            self.logger.info("System tray icon started (detached)")
            
        except Exception as e:
            self.logger.error(f"Error running system tray: {e}")
            raise
    
    def stop(self) -> None:
        """Stop the system tray icon."""
        if self.icon:
            self.icon.stop()
            self.logger.info("System tray icon stopped")
    
    def update_hotkey_display(self, hotkey: str) -> None:
        """Update hotkey display in menu."""
        self.hotkey_text = hotkey
        if self.icon:
            self.icon.update_menu()
    
    def update_queue_count(self, count: int) -> None:
        """Update queue count display."""
        self.queue_count = count
        if self.icon:
            self.icon.update_menu()
    
    def set_processing(self, is_processing: bool) -> None:
        """Update processing state."""
        self.is_processing = is_processing
        # Could animate icon or update tooltip here
    
    def show_notification(
        self, 
        title: str, 
        message: str, 
        duration: int = 3
    ) -> None:
        """Show a system notification."""
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception as e:
                self.logger.warning(f"Could not show notification: {e}")
