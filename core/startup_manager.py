"""Windows startup management."""
import os
import sys
from pathlib import Path
from typing import Optional


class StartupManager:
    """Manages Windows startup registration."""
    
    REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    def __init__(self, app_name: str = "AIAssistantPro"):
        """
        Initialize startup manager.
        
        Args:
            app_name: Application name for registry
        """
        self.app_name = app_name
        self._logger = None
    
    @property
    def logger(self):
        if self._logger is None:
            from .logger import get_logger
            self._logger = get_logger()
        return self._logger
    
    def is_enabled(self) -> bool:
        """Check if application is set to run on startup."""
        if sys.platform != 'win32':
            return False
            
        import winreg
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY,
                0,
                winreg.KEY_READ
            )
            
            try:
                winreg.QueryValueEx(key, self.app_name)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking startup status: {e}")
            return False
    
    def enable(self) -> bool:
        """Enable application to run on Windows startup."""
        if sys.platform != 'win32':
            self.logger.warning("Startup management only available on Windows")
            return False
            
        import winreg
        
        try:
            # Get path to current executable or script
            if getattr(sys, 'frozen', False):
                app_path = sys.executable
            else:
                app_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY,
                0,
                winreg.KEY_WRITE
            )
            
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, app_path)
            winreg.CloseKey(key)
            
            self.logger.info(f"Startup enabled: {app_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error enabling startup: {e}")
            return False
    
    def disable(self) -> bool:
        """Disable application from running on Windows startup."""
        if sys.platform != 'win32':
            return False
            
        import winreg
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY,
                0,
                winreg.KEY_WRITE
            )
            
            try:
                winreg.DeleteValue(key, self.app_name)
                self.logger.info("Startup disabled")
            except FileNotFoundError:
                self.logger.info("Startup was already disabled")
            
            winreg.CloseKey(key)
            return True
            
        except Exception as e:
            self.logger.error(f"Error disabling startup: {e}")
            return False
    
    def toggle(self) -> bool:
        """
        Toggle startup setting.
        
        Returns:
            New state (True = enabled, False = disabled)
        """
        if self.is_enabled():
            self.disable()
            return False
        else:
            self.enable()
            return True
