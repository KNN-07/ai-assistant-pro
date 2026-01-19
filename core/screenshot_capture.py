"""Screenshot capture functionality."""
import io
from pathlib import Path
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image


class ScreenshotCapture:
    """Handles screenshot capture without changing window focus."""
    
    def __init__(self, save_to_disk: bool = False, output_dir: str = "screenshots"):
        """
        Initialize screenshot capture.
        
        Args:
            save_to_disk: Whether to save screenshots to disk
            output_dir: Directory to save screenshots
        """
        self.save_to_disk = save_to_disk
        self.output_dir = Path(output_dir)
        self._logger = None
        
        if self.save_to_disk:
            self.output_dir.mkdir(exist_ok=True)
    
    @property
    def logger(self):
        if self._logger is None:
            from .logger import get_logger
            self._logger = get_logger()
        return self._logger
    
    def capture_full_screen(self, monitor: int = 1) -> 'Image.Image':
        """
        Capture full screen without changing focus.
        
        Args:
            monitor: Monitor number (1 for primary)
            
        Returns:
            PIL Image object
        """
        import mss
        from PIL import Image
        
        try:
            with mss.mss() as sct:
                monitor_data = sct.monitors[monitor]
                screenshot = sct.grab(monitor_data)
                
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                self.logger.info(f"Screenshot captured: {screenshot.size}")
                
                if self.save_to_disk:
                    self._save_screenshot(img)
                
                return img
                
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot: {e}")
            raise
    
    def capture_all_monitors(self) -> 'Image.Image':
        """
        Capture all monitors as a single image.
        
        Returns:
            PIL Image object
        """
        import mss
        from PIL import Image
        
        try:
            with mss.mss() as sct:
                # Monitor 0 is the "all monitors" virtual screen
                screenshot = sct.grab(sct.monitors[0])
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                
                self.logger.info(f"All monitors captured: {screenshot.size}")
                
                if self.save_to_disk:
                    self._save_screenshot(img, prefix="all_monitors")
                
                return img
                
        except Exception as e:
            self.logger.error(f"Failed to capture all monitors: {e}")
            raise
    
    def capture_region(
        self, 
        x: int, 
        y: int, 
        width: int, 
        height: int
    ) -> 'Image.Image':
        """
        Capture specific screen region.
        
        Args:
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of region
            height: Height of region
            
        Returns:
            PIL Image object
        """
        import mss
        from PIL import Image
        
        try:
            with mss.mss() as sct:
                region = {"top": y, "left": x, "width": width, "height": height}
                screenshot = sct.grab(region)
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                
                self.logger.info(f"Region captured: {width}x{height} at ({x}, {y})")
                
                if self.save_to_disk:
                    self._save_screenshot(img, prefix="region")
                
                return img
                
        except Exception as e:
            self.logger.error(f"Failed to capture region: {e}")
            raise
    
    def _save_screenshot(
        self, 
        img: 'Image.Image', 
        prefix: str = "screenshot"
    ) -> Path:
        """Save screenshot to disk."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}.png"
        filepath = self.output_dir / filename
        img.save(filepath)
        self.logger.info(f"Screenshot saved: {filepath}")
        return filepath
    
    @staticmethod
    def image_to_bytes(img: 'Image.Image', format: str = "PNG") -> bytes:
        """
        Convert PIL Image to bytes.
        
        Args:
            img: PIL Image object
            format: Image format (PNG, JPEG, etc.)
            
        Returns:
            Image bytes
        """
        byte_arr = io.BytesIO()
        img.save(byte_arr, format=format)
        return byte_arr.getvalue()
    
    @staticmethod
    def get_monitor_count() -> int:
        """Get number of available monitors."""
        import mss
        with mss.mss() as sct:
            # Subtract 1 because monitor[0] is the virtual "all monitors" screen
            return len(sct.monitors) - 1
