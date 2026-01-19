"""Main dashboard window for AI Assistant Pro."""
import customtkinter as ctk
from typing import Callable, Optional
import queue
from datetime import datetime

from ui.theme import get_theme
from ui.components import (
    AnimatedButton,
    CaptureButton,
    Card,
    StatsCard,
    StatusCard,
    StatusBadge,
    LogViewer,
    ToastManager,
)


class MainWindow(ctk.CTk):
    """Main application window with dashboard."""
    
    APP_NAME = "AI Assistant Pro"
    VERSION = "2.0.0"
    
    def __init__(
        self,
        on_toggle: Optional[Callable[[bool], None]] = None,
        on_capture: Optional[Callable[[], None]] = None,
        on_settings: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[], None]] = None,
        initial_enabled: bool = True,
    ):
        super().__init__()
        
        self.theme = get_theme()
        self.on_toggle = on_toggle
        self.on_capture = on_capture
        self.on_settings = on_settings
        self.on_exit = on_exit
        self.is_enabled = initial_enabled
        
        # Stats tracking
        self._capture_count = 0
        self._queue_count = 0
        
        # Configure window
        self._setup_window()
        self._create_ui()
        
        # Toast manager
        self.toast_manager = ToastManager(self, position="top-right")
    
    def _setup_window(self):
        """Configure window properties."""
        self.title(self.APP_NAME)
        self.geometry("480x720")
        self.minsize(400, 600)
        
        # Dark title bar on Windows
        self.configure(fg_color=self.theme.colors.bg_dark)
        
        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 480) // 2
        y = (self.winfo_screenheight() - 720) // 2
        self.geometry(f"480x720+{x}+{y}")
        
        # Handle close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_ui(self):
        """Create the main UI layout."""
        # Main container with padding
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self._create_header(container)
        
        # Status section
        self._create_status_section(container)
        
        # Capture button
        self._create_capture_section(container)
        
        # Stats section
        self._create_stats_section(container)
        
        # Log viewer
        self._create_log_section(container)
        
        # Footer with controls
        self._create_footer(container)
    
    def _create_header(self, parent):
        """Create header with title and status badge."""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        
        # Title
        title = ctk.CTkLabel(
            header,
            text=self.APP_NAME,
            text_color=self.theme.colors.text_primary,
            font=(self.theme.fonts.family, 24, "bold"),
        )
        title.pack(side="left")
        
        # Version badge
        version = ctk.CTkLabel(
            header,
            text=f"v{self.VERSION}",
            text_color=self.theme.colors.text_tertiary,
            font=self.theme.get_font("xs"),
        )
        version.pack(side="left", padx=(10, 0), pady=(8, 0))
        
        # Status badge
        self.status_badge = StatusBadge(
            header,
            text="Active" if self.is_enabled else "Paused",
            status="success" if self.is_enabled else "inactive",
        )
        self.status_badge.pack(side="right")
    
    def _create_status_section(self, parent):
        """Create status card section."""
        self.status_card = StatusCard(
            parent,
            title="Assistant Status",
            status="Ready",
            status_type="success",
            description="Press hotkey or click capture button",
        )
        self.status_card.pack(fill="x", pady=(0, 16))
    
    def _create_capture_section(self, parent):
        """Create main capture button section."""
        capture_frame = ctk.CTkFrame(parent, fg_color="transparent")
        capture_frame.pack(fill="x", pady=16)
        
        self.capture_button = CaptureButton(
            capture_frame,
            command=self._handle_capture,
            size=100,
        )
        self.capture_button.pack(expand=True)
    
    def _create_stats_section(self, parent):
        """Create stats cards section."""
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 16))
        
        # Configure grid
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        
        # Captures today
        self.captures_stat = StatsCard(
            stats_frame,
            value="0",
            label="Captures Today",
            icon="📸",
            color=self.theme.colors.primary,
        )
        self.captures_stat.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        # Queue count
        self.queue_stat = StatsCard(
            stats_frame,
            value="0",
            label="In Queue",
            icon="📋",
            color=self.theme.colors.warning,
        )
        self.queue_stat.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
    
    def _create_log_section(self, parent):
        """Create log viewer section."""
        self.log_viewer = LogViewer(
            parent,
            height=150,
            auto_scroll=True,
            show_timestamps=True,
        )
        self.log_viewer.pack(fill="both", expand=True, pady=(0, 16))
        
        # Initial log
        self.log_viewer.info("AI Assistant Pro started")
        self.log_viewer.info("Waiting for hotkey...")
    
    def _create_footer(self, parent):
        """Create footer with control buttons."""
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x")
        
        # Left: Toggle button
        self.toggle_btn = AnimatedButton(
            footer,
            text="Disable" if self.is_enabled else "Enable",
            style="secondary",
            icon="⏸" if self.is_enabled else "▶",
            command=self._handle_toggle,
            width=100,
        )
        self.toggle_btn.pack(side="left")
        
        # Right: Settings and more
        right_frame = ctk.CTkFrame(footer, fg_color="transparent")
        right_frame.pack(side="right")
        
        settings_btn = AnimatedButton(
            right_frame,
            text="Settings",
            style="ghost",
            icon="⚙",
            command=self._handle_settings,
            width=100,
        )
        settings_btn.pack(side="left", padx=(0, 8))
        
        quit_btn = AnimatedButton(
            right_frame,
            text="Quit",
            style="ghost",
            command=self._handle_exit,
            width=60,
        )
        quit_btn.pack(side="left")
    
    # Event handlers
    def _handle_capture(self):
        """Handle capture button click."""
        if self.on_capture:
            self.on_capture()
    
    def _handle_toggle(self):
        """Handle toggle button click."""
        self.is_enabled = not self.is_enabled
        
        # Update UI
        self.status_badge.set_status(
            "Active" if self.is_enabled else "Paused",
            "success" if self.is_enabled else "inactive"
        )
        self.toggle_btn.configure(
            text="Disable" if self.is_enabled else "Enable",
        )
        
        if self.on_toggle:
            self.on_toggle(self.is_enabled)
        
        status = "enabled" if self.is_enabled else "disabled"
        self.log_viewer.info(f"Assistant {status}")
    
    def _handle_settings(self):
        """Handle settings button click."""
        if self.on_settings:
            self.on_settings()
    
    def _handle_exit(self):
        """Handle exit button click."""
        if self.on_exit:
            self.on_exit()
        else:
            self.destroy()
    
    def _on_close(self):
        """Handle window close (minimize to tray instead)."""
        self.withdraw()
    
    # Public methods
    def show(self):
        """Show the window."""
        self.deiconify()
        self.lift()
        self.focus_force()
    
    def hide(self):
        """Hide the window."""
        self.withdraw()
    
    def log(self, message: str, level: str = "INFO"):
        """Add message to log viewer."""
        level_map = {
            "INFO": self.log_viewer.info,
            "WARNING": self.log_viewer.warning,
            "ERROR": self.log_viewer.error,
            "SUCCESS": self.log_viewer.success,
            "DEBUG": self.log_viewer.debug,
        }
        log_func = level_map.get(level.upper(), self.log_viewer.info)
        log_func(message)
    
    def set_processing(self, processing: bool, status: str = ""):
        """Update processing state."""
        self.capture_button.set_processing(processing, status)
        
        if processing:
            self.status_card.set_status("Processing", "warning", status or "Analyzing screenshot...")
        else:
            self.status_card.set_status("Ready", "success", "Press hotkey or click capture button")
    
    def update_capture_count(self, count: int):
        """Update captures today stat."""
        self._capture_count = count
        self.captures_stat.set_value(str(count))
    
    def update_queue_count(self, count: int):
        """Update queue count stat."""
        self._queue_count = count
        self.queue_stat.set_value(str(count))
    
    def increment_capture_count(self):
        """Increment capture count by 1."""
        self._capture_count += 1
        self.captures_stat.set_value(str(self._capture_count))
    
    def show_toast(self, message: str, toast_type: str = "info", title: str = None):
        """Show a toast notification."""
        method = getattr(self.toast_manager, toast_type, self.toast_manager.info)
        method(message, title)
    
    def update_hotkey_display(self, hotkey: str):
        """Update hotkey display."""
        self.capture_button.set_status(f"Hotkey: {hotkey}")
