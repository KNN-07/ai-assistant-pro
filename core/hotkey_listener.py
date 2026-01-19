"""Global hotkey listener for triggering AI assistant."""
from typing import Callable, Optional, Dict


class HotkeyListener:
    """Manages global hotkey registration and callbacks."""
    
    def __init__(self):
        """Initialize hotkey listener."""
        self.registered_hotkeys: Dict[str, Callable] = {}
        self.is_enabled = False
        self._logger = None
    
    @property
    def logger(self):
        if self._logger is None:
            from .logger import get_logger
            self._logger = get_logger()
        return self._logger
    
    def register(
        self, 
        hotkey: str, 
        callback: Callable, 
        replace: bool = False
    ) -> bool:
        """
        Register a global hotkey.
        
        Args:
            hotkey: Hotkey combination (e.g., 'ctrl+shift+alt+a')
            callback: Function to call when hotkey is pressed
            replace: If True, unregister all previous hotkeys
            
        Returns:
            True if registration successful, False otherwise
        """
        import keyboard
        
        try:
            if replace and self.registered_hotkeys:
                self.unregister_all()
            
            if hotkey in self.registered_hotkeys:
                self.logger.warning(f"Hotkey '{hotkey}' already registered, replacing")
                keyboard.remove_hotkey(hotkey)
            
            keyboard.add_hotkey(hotkey, callback, suppress=False)
            self.registered_hotkeys[hotkey] = callback
            self.is_enabled = True
            
            self.logger.info(f"Hotkey registered: {hotkey}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register hotkey '{hotkey}': {e}")
            return False
    
    def unregister(self, hotkey: str) -> None:
        """Unregister a specific hotkey."""
        import keyboard
        
        if hotkey in self.registered_hotkeys:
            try:
                keyboard.remove_hotkey(hotkey)
                del self.registered_hotkeys[hotkey]
                self.logger.info(f"Hotkey unregistered: {hotkey}")
            except Exception as e:
                self.logger.warning(f"Error unregistering hotkey '{hotkey}': {e}")
    
    def unregister_all(self) -> None:
        """Unregister all hotkeys."""
        import keyboard
        
        for hotkey in list(self.registered_hotkeys.keys()):
            try:
                keyboard.remove_hotkey(hotkey)
                self.logger.info(f"Hotkey unregistered: {hotkey}")
            except Exception as e:
                self.logger.warning(f"Error unregistering hotkey '{hotkey}': {e}")
        
        self.registered_hotkeys.clear()
        self.is_enabled = False
    
    def enable(self) -> bool:
        """Re-enable all registered hotkeys."""
        import keyboard
        
        if not self.registered_hotkeys:
            self.logger.warning("Cannot enable: no hotkeys registered")
            return False
        
        if self.is_enabled:
            return True
        
        # Re-register all hotkeys
        hotkeys_snapshot = dict(self.registered_hotkeys)
        self.registered_hotkeys.clear()
        
        success = True
        for hotkey, callback in hotkeys_snapshot.items():
            if not self.register(hotkey, callback):
                success = False
        
        return success
    
    def disable(self) -> None:
        """Disable all hotkeys temporarily."""
        import keyboard
        
        for hotkey in self.registered_hotkeys.keys():
            try:
                keyboard.remove_hotkey(hotkey)
            except Exception as e:
                self.logger.warning(f"Error disabling hotkey '{hotkey}': {e}")
        
        self.is_enabled = False
        self.logger.info("All hotkeys disabled")
    
    @staticmethod
    def is_valid_hotkey(hotkey: str) -> bool:
        """Check if hotkey string is valid."""
        import keyboard
        try:
            keyboard.parse_hotkey(hotkey)
            return True
        except Exception:
            return False
    
    def get_registered_hotkeys(self) -> list[str]:
        """Get list of registered hotkey strings."""
        return list(self.registered_hotkeys.keys())
    
    def wait(self) -> None:
        """Block and wait for hotkey events."""
        import keyboard
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            self.logger.info("Hotkey listener stopped")
            self.unregister_all()
