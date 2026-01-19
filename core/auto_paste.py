"""Auto-paste functionality with clipboard management."""
import time
from typing import Optional


class AutoPaste:
    """Handles automatic pasting of AI responses."""
    
    def __init__(self, delay_ms: int = 500, restore_clipboard: bool = False):
        """
        Initialize auto-paste handler.
        
        Args:
            delay_ms: Delay before pasting in milliseconds
            restore_clipboard: Whether to restore original clipboard after paste
        """
        self.delay_ms = delay_ms
        self.restore_clipboard = restore_clipboard
        self._logger = None
        
        # Import and configure pyautogui
        import pyautogui
        pyautogui.FAILSAFE = False
    
    @property
    def logger(self):
        if self._logger is None:
            from .logger import get_logger
            self._logger = get_logger()
        return self._logger
    
    def paste_text(self, text: str) -> bool:
        """
        Paste text at current cursor position.
        
        Args:
            text: Text to paste
            
        Returns:
            True if successful, False otherwise
        """
        import pyautogui
        import pyperclip
        
        original_clipboard: Optional[str] = None
        
        try:
            # Store original clipboard content if needed
            if self.restore_clipboard:
                try:
                    original_clipboard = pyperclip.paste()
                except Exception as e:
                    self.logger.warning(f"Could not read original clipboard: {e}")
            
            # Copy AI response to clipboard
            pyperclip.copy(text)
            self.logger.info(f"Copied {len(text)} characters to clipboard")
            
            # Wait for specified delay
            time.sleep(self.delay_ms / 1000.0)
            
            # Simulate Ctrl+V keypress
            pyautogui.hotkey('ctrl', 'v')
            self.logger.info("Paste command sent")
            
            # Small delay to ensure paste completes
            time.sleep(0.1)
            
            # Restore original clipboard if needed
            if self.restore_clipboard and original_clipboard is not None:
                time.sleep(0.2)
                pyperclip.copy(original_clipboard)
                self.logger.info("Original clipboard restored")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to paste text: {e}")
            return False
    
    def copy_to_clipboard(self, text: str) -> bool:
        """
        Copy text to clipboard without pasting.
        
        Args:
            text: Text to copy
            
        Returns:
            True if successful, False otherwise
        """
        import pyperclip
        
        try:
            pyperclip.copy(text)
            self.logger.info(f"Copied {len(text)} characters to clipboard")
            return True
        except Exception as e:
            self.logger.error(f"Failed to copy to clipboard: {e}")
            return False
    
    def set_delay(self, delay_ms: int) -> None:
        """Update paste delay."""
        self.delay_ms = delay_ms
        self.logger.info(f"Paste delay updated to {delay_ms}ms")
    
    def set_restore_clipboard(self, restore: bool) -> None:
        """Update clipboard restore setting."""
        self.restore_clipboard = restore
        self.logger.info(f"Restore clipboard: {restore}")
