"""Main application orchestrator for AI Assistant Pro."""
import os
import sys
import threading
from pathlib import Path
from queue import Queue

from core import (
    ConfigManager,
    setup_logger,
    GeminiIntegration,
    ScreenshotCapture,
    AutoPaste,
    HotkeyListener,
    StartupManager,
    SystemTray,
)
from core.logger import get_log_manager


class AIAssistantPro:
    """Main application orchestrating all components."""
    
    VERSION = "2.0.0"
    
    def __init__(self):
        """Initialize AI Assistant Pro application."""
        # Change to application directory
        os.chdir(Path(__file__).parent)
        
        # Initialize configuration
        self.config = ConfigManager()
        
        # Setup logger
        log_level = self.config.get('logging.level', 'INFO')
        save_logs = self.config.get('logging.save_logs', True)
        self.logger = setup_logger(log_level=log_level, save_logs=save_logs)
        
        self.logger.info("=" * 50)
        self.logger.info("AI Assistant Pro Starting...")
        self.logger.info("=" * 50)
        
        # Initialize core components
        self._init_core_components()
        
        # State
        self.is_enabled = True
        self.is_processing = False
        self.image_queue: Queue = Queue()
        self._queue_lock = threading.Lock()
        
        # UI components (lazy loaded)
        self._main_window = None
        self._floating_widget = None
        self._settings_window = None
        
        # Register hotkeys
        self._register_hotkeys()
        
        # Check startup setting
        self._apply_startup_setting()
        
        self.logger.info("AI Assistant Pro initialized successfully")
    
    def _init_core_components(self):
        """Initialize core service components."""
        # Screenshot capture
        save_screenshots = self.config.get('screenshot.save_to_disk', False)
        self.screenshot = ScreenshotCapture(save_to_disk=save_screenshots)
        
        # Gemini AI integration
        self.gemini = GeminiIntegration(self.config)
        
        # Auto-paste
        paste_delay = self.config.get_paste_delay()
        restore_clipboard = self.config.get('auto_paste.restore_clipboard', False)
        self.auto_paste = AutoPaste(
            delay_ms=paste_delay,
            restore_clipboard=restore_clipboard
        )
        
        # Hotkey listener
        self.hotkey_listener = HotkeyListener()
        
        # Startup manager
        self.startup_manager = StartupManager()
        
        # System tray
        self.system_tray = SystemTray(
            on_toggle=self._on_toggle,
            on_settings=self._on_settings,
            on_show_main=self._on_show_main,
            on_exit=self._on_exit,
        )
    
    def _register_hotkeys(self):
        """Register global hotkeys."""
        # Main analysis hotkey
        main_hotkey = self.config.get_hotkey()
        if self.hotkey_listener.register(main_hotkey, self._on_main_hotkey):
            self.logger.info(f"Main hotkey registered: {main_hotkey}")
        else:
            self.logger.error(f"Failed to register main hotkey: {main_hotkey}")
        
        # Capture-only hotkey
        capture_hotkey = self.config.get_capture_hotkey()
        if self.hotkey_listener.register(capture_hotkey, self._on_capture_hotkey):
            self.logger.info(f"Capture hotkey registered: {capture_hotkey}")
        else:
            self.logger.error(f"Failed to register capture hotkey: {capture_hotkey}")
        
        # Update system tray display
        self.system_tray.update_hotkey_display(main_hotkey)
    
    def _apply_startup_setting(self):
        """Apply Windows startup setting from config."""
        startup_enabled = self.config.get('startup.launch_on_boot', False)
        if startup_enabled and not self.startup_manager.is_enabled():
            self.startup_manager.enable()
        elif not startup_enabled and self.startup_manager.is_enabled():
            self.startup_manager.disable()
    
    # Hotkey handlers
    def _on_main_hotkey(self):
        """Handle main analysis hotkey press."""
        if not self.is_enabled:
            self.logger.info("Hotkey pressed but assistant is disabled")
            return
        
        if self.is_processing:
            self.logger.info("Already processing, ignoring hotkey")
            return
        
        self.logger.info("Main hotkey pressed!")
        
        # Run in thread to avoid blocking
        thread = threading.Thread(target=self._process_capture, daemon=True)
        thread.start()
    
    def _on_capture_hotkey(self):
        """Handle capture-only hotkey press."""
        if not self.is_enabled:
            return
        
        self.logger.info("Capture hotkey pressed! Queuing screenshot...")
        
        thread = threading.Thread(target=self._queue_screenshot, daemon=True)
        thread.start()
    
    def _queue_screenshot(self):
        """Capture and queue a screenshot."""
        try:
            image = self.screenshot.capture_full_screen()
            self.image_queue.put(image)
            
            count = self.image_queue.qsize()
            self.logger.info(f"Screenshot queued. Total: {count}")
            
            # Update UI
            self.system_tray.update_queue_count(count)
            self.system_tray.show_notification(
                "Screenshot Queued",
                f"Images in queue: {count}\nPress main hotkey to analyze."
            )
            
            if self._main_window:
                self._main_window.update_queue_count(count)
            
            if self._floating_widget:
                self._floating_widget.update_queue_count(count)
                
        except Exception as e:
            self.logger.error(f"Error queuing screenshot: {e}")
    
    def _process_capture(self):
        """Process screenshot(s) - capture, analyze, paste."""
        try:
            self.is_processing = True
            self._update_processing_state(True, "Capturing...")
            
            # Determine images to process - drain queue thread-safely
            images = []
            with self._queue_lock:
                while not self.image_queue.empty():
                    try:
                        images.append(self.image_queue.get_nowait())
                    except Exception:
                        break
            
            if images:
                self.logger.info(f"Processing {len(images)} queued images...")
                self.system_tray.update_queue_count(0)
                if self._main_window:
                    self._main_window.update_queue_count(0)
                if self._floating_widget:
                    self._floating_widget.update_queue_count(0)
            else:
                self.logger.info("Capturing screenshot...")
                images = self.screenshot.capture_full_screen()
            
            # Analyze with Gemini
            self._update_processing_state(True, "Analyzing...")
            prompt = self.config.get_system_prompt()
            response = self.gemini.analyze_screenshot_sync(images, prompt)
            
            self.logger.info(f"Received response: {response[:100]}...")
            
            # Auto-paste or copy to clipboard
            if self.config.is_auto_paste_enabled():
                self._update_processing_state(True, "Pasting...")
                if self.auto_paste.paste_text(response):
                    self.system_tray.show_notification(
                        "AI Assistant Pro",
                        "Response pasted!"
                    )
                else:
                    self.auto_paste.copy_to_clipboard(response)
                    self.system_tray.show_notification(
                        "AI Assistant Pro",
                        "Response copied to clipboard"
                    )
            else:
                self.auto_paste.copy_to_clipboard(response)
                self.system_tray.show_notification(
                    "AI Assistant Pro",
                    "Response copied to clipboard"
                )
            
            # Update stats
            if self._main_window:
                self._main_window.increment_capture_count()
                self._main_window.update_queue_count(0)
                
        except Exception as e:
            self.logger.error(f"Error processing: {e}")
            self.system_tray.show_notification(
                "Error",
                f"Failed: {str(e)[:50]}"
            )
        finally:
            self.is_processing = False
            self._update_processing_state(False, "Ready")
    
    def _update_processing_state(self, processing: bool, status: str):
        """Update processing state across UI components."""
        self.system_tray.set_processing(processing)
        
        if self._main_window:
            self._main_window.set_processing(processing, status)
        
        if self._floating_widget:
            self._floating_widget.set_processing(processing)
    
    # Callbacks
    def _on_toggle(self, enabled: bool):
        """Handle enable/disable toggle."""
        self.is_enabled = enabled
        
        if enabled:
            self.hotkey_listener.enable()
        else:
            self.hotkey_listener.disable()
        
        self.logger.info(f"Assistant {'enabled' if enabled else 'disabled'}")
        
        # Sync UI states
        if self._main_window and self._main_window.is_enabled != enabled:
            self._main_window.is_enabled = enabled
    
    def _on_settings(self):
        """Handle settings request."""
        self.logger.info("Opening settings...")
        
        if self._main_window:
            # Import here to avoid circular imports
            from ui.windows import SettingsWindow
            
            self._settings_window = SettingsWindow(
                self._main_window,
                config_manager=self.config,
                on_save=self._on_settings_saved,
                on_test_capture=self._on_test_capture,
            )
    
    def _on_test_capture(self):
        """Handle test capture from settings window."""
        try:
            self.logger.info("Test capture initiated...")
            
            # Temporarily enable saving to disk
            original_save = self.screenshot.save_to_disk
            self.screenshot.save_to_disk = True
            
            # Capture screenshot
            self.screenshot.capture_full_screen()
            
            # Restore original setting
            self.screenshot.save_to_disk = original_save
            
            self.logger.info("Test capture completed successfully")
            
        except Exception as e:
            self.logger.error(f"Test capture failed: {e}")
    
    def _on_settings_saved(self):
        """Handle settings saved."""
        self.logger.info("Settings saved. Restart for full effect.")
        
        if self._main_window:
            self._main_window.show_toast(
                "Settings saved. Restart for changes to take effect.",
                "success",
                "Settings Saved"
            )
    
    def _on_show_main(self):
        """Handle show main window request."""
        if self._main_window:
            self._main_window.show()
    
    def _on_exit(self):
        """Handle exit request."""
        self.logger.info("Shutting down AI Assistant Pro...")
        
        # Unregister hotkeys
        self.hotkey_listener.unregister_all()
        
        # Save floating widget position if enabled
        if self._floating_widget:
            pos = self._floating_widget.get_position()
            self.config.set('ui.floating_widget_position', list(pos))
        
        # Close windows
        if self._main_window:
            self._main_window.destroy()
        
        sys.exit(0)
    
    def run(self):
        """Run the application."""
        self.logger.info("Starting application...")
        
        try:
            # Start system tray (detached)
            self.system_tray.run_detached()
            
            # Create main window
            from ui.windows import MainWindow, FloatingWidget
            
            self._main_window = MainWindow(
                on_toggle=self._on_toggle,
                on_capture=lambda: threading.Thread(
                    target=self._process_capture, daemon=True
                ).start(),
                on_settings=self._on_settings,
                on_exit=self._on_exit,
                initial_enabled=self.is_enabled,
            )
            
            # Update hotkey display
            self._main_window.update_hotkey_display(self.config.get_hotkey())
            
            # Create floating widget if enabled
            if self.config.get('ui.show_floating_widget', True):
                pos = self.config.get('ui.floating_widget_position', [50, 50])
                self._floating_widget = FloatingWidget(
                    self._main_window,
                    on_capture=lambda: threading.Thread(
                        target=self._process_capture, daemon=True
                    ).start(),
                    on_toggle=self._on_toggle,
                    position=tuple(pos),
                )
            
            # Connect logger to GUI
            log_manager = get_log_manager()
            log_manager.add_gui_handler(
                lambda ts, level, msg: self._main_window.log(msg, level)
                if self._main_window else None
            )
            
            # Show main window
            self._main_window.show()
            
            # Run main loop
            self._main_window.mainloop()
            
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
            self._on_exit()
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            raise


def main():
    """Main entry point."""
    try:
        app = AIAssistantPro()
        app.run()
    except Exception as e:
        import traceback
        print(f"Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
