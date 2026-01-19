"""Gemini AI integration with automatic API key rotation."""
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from PIL import Image
    from .config_manager import ConfigManager


class GeminiIntegration:
    """Handles communication with Gemini AI API with key rotation."""
    
    QUOTA_ERROR_INDICATORS = [
        'quota',
        'rate limit',
        'resource exhausted',
        '429',
        'too many requests',
        'exceeded'
    ]
    
    def __init__(self, config_manager: 'ConfigManager', model_name: Optional[str] = None):
        """
        Initialize Gemini integration.
        
        Args:
            config_manager: ConfigManager instance for key rotation
            model_name: Model to use (defaults to config value)
        """
        self.config = config_manager
        self.model_name = model_name or config_manager.get_model()
        self.client = None
        self.current_api_key: Optional[str] = None
        self._logger = None
        
        # Initialize with first available key
        api_key = self.config.get_api_key()
        if api_key:
            self._initialize_client(api_key)
    
    @property
    def logger(self):
        if self._logger is None:
            from .logger import get_logger
            self._logger = get_logger()
        return self._logger
    
    def _initialize_client(self, api_key: str) -> None:
        """Initialize Gemini client with API key."""
        try:
            from google import genai
            self.client = genai.Client(api_key=api_key)
            self.current_api_key = api_key
            self.logger.info(f"Gemini client initialized with model: {self.model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def _is_quota_error(self, error: Exception) -> bool:
        """Check if error is a quota/rate limit error."""
        error_str = str(error).lower()
        return any(indicator in error_str for indicator in self.QUOTA_ERROR_INDICATORS)
    
    def _try_rotate_key(self) -> bool:
        """
        Attempt to rotate to next API key.
        
        Returns:
            True if rotation successful, False if no more keys
        """
        if not self.config.is_auto_rotate_enabled():
            self.logger.info("Auto-rotation disabled")
            return False
        
        all_keys = self.config.get_all_api_keys()
        if len(all_keys) <= 1:
            self.logger.warning("No alternative API keys available")
            return False
        
        next_key = self.config.rotate_to_next_key()
        
        if next_key == self.current_api_key:
            self.logger.warning("Rotated back to same key (full cycle)")
            return False
        
        try:
            self._initialize_client(next_key)
            key_index = self.config.get('gemini.current_key_index', 0)
            self.logger.info(f"Rotated to API key #{key_index + 1}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize with rotated key: {e}")
            return False
    
    def set_api_key(self, api_key: str) -> None:
        """Update API key and reinitialize client."""
        self._initialize_client(api_key)
    
    def analyze_screenshot_sync(
        self,
        images: Union[list, 'Image.Image'],
        prompt: str = "Analyze this screenshot and provide a solution.",
        retry_count: int = 0
    ) -> str:
        """
        Synchronous screenshot analysis with auto-rotation.
        
        Args:
            images: Single PIL Image or list of PIL Images
            prompt: Custom prompt for analysis
            retry_count: Internal retry counter
            
        Returns:
            AI response text
        """
        if not self.client:
            error_msg = "Gemini client not initialized. Please set API key."
            self.logger.error(error_msg)
            return error_msg
        
        try:
            self.logger.info("Sending screenshot(s) to Gemini...")
            
            # Prepare contents
            contents = [prompt]
            if isinstance(images, list):
                contents.extend(images)
                self.logger.info(f"Attached {len(images)} images")
            else:
                contents.append(images)
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            
            result_text = response.text
            self.logger.info(f"Received response ({len(result_text)} chars)")
            return result_text
            
        except Exception as e:
            max_retries = len(self.config.get_all_api_keys())
            if self._is_quota_error(e) and retry_count < max_retries:
                self.logger.warning(f"Quota error: {str(e)[:100]}")
                
                if self._try_rotate_key():
                    self.logger.info("Retrying with rotated key...")
                    return self.analyze_screenshot_sync(images, prompt, retry_count + 1)
            
            error_msg = f"Error analyzing screenshot: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    async def analyze_screenshot(
        self,
        images: Union[list, 'Image.Image'],
        prompt: str = "Analyze this screenshot and provide a solution.",
        retry_count: int = 0
    ) -> str:
        """
        Async screenshot analysis with auto-rotation.
        
        Args:
            images: Single PIL Image or list of PIL Images
            prompt: Custom prompt for analysis
            retry_count: Internal retry counter
            
        Returns:
            AI response text
        """
        if not self.client:
            error_msg = "Gemini client not initialized. Please set API key."
            self.logger.error(error_msg)
            return error_msg
        
        try:
            self.logger.info("Sending screenshot(s) to Gemini (async)...")
            
            contents = [prompt]
            if isinstance(images, list):
                contents.extend(images)
                self.logger.info(f"Attached {len(images)} images")
            else:
                contents.append(images)
            
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            
            result_text = response.text
            self.logger.info(f"Received response ({len(result_text)} chars)")
            return result_text
            
        except Exception as e:
            max_retries = len(self.config.get_all_api_keys())
            if self._is_quota_error(e) and retry_count < max_retries:
                self.logger.warning(f"Quota error: {str(e)[:100]}")
                
                if self._try_rotate_key():
                    self.logger.info("Retrying with rotated key...")
                    return await self.analyze_screenshot(images, prompt, retry_count + 1)
            
            error_msg = f"Error analyzing screenshot: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Test connection to Gemini API.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.client:
            return False, "Client not initialized"
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Hello"
            )
            return True, "Connection successful"
        except Exception as e:
            error_msg = str(e)[:100]
            self.logger.error(f"Connection test failed: {error_msg}")
            return False, error_msg
