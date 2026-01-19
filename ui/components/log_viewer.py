"""Log viewer component for AI Assistant Pro."""
import customtkinter as ctk
from typing import Literal, Optional
from datetime import datetime
from ui.theme import get_theme


class LogViewer(ctk.CTkFrame):
    """Styled scrollable log viewer with color-coded entries."""
    
    def __init__(
        self,
        parent,
        height: int = 200,
        auto_scroll: bool = True,
        show_timestamps: bool = True,
        show_clear_button: bool = True,
        **kwargs
    ):
        theme = get_theme()
        
        super().__init__(
            parent,
            fg_color=theme.colors.bg_medium,
            corner_radius=theme.dimensions.radius_lg,
            border_width=1,
            border_color=theme.colors.border,
            **kwargs
        )
        
        self.theme = theme
        self.auto_scroll = auto_scroll
        self.show_timestamps = show_timestamps
        self._max_lines = 500
        self._line_count = 0
        
        # Level colors
        self._level_colors = {
            "DEBUG": theme.colors.text_tertiary,
            "INFO": theme.colors.text_primary,
            "WARNING": theme.colors.warning,
            "ERROR": theme.colors.error,
            "SUCCESS": theme.colors.success,
        }
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent", height=36)
        header.pack(fill="x", padx=12, pady=(8, 0))
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="Activity Log",
            text_color=theme.colors.text_secondary,
            font=theme.get_font("sm"),
        )
        title.pack(side="left", pady=4)
        
        if show_clear_button:
            clear_btn = ctk.CTkButton(
                header,
                text="Clear",
                width=60,
                height=26,
                corner_radius=theme.dimensions.radius_sm,
                fg_color="transparent",
                hover_color=theme.colors.bg_hover,
                text_color=theme.colors.text_tertiary,
                font=theme.get_font("xs"),
                command=self.clear,
            )
            clear_btn.pack(side="right")
        
        # Auto-scroll toggle
        self.auto_scroll_var = ctk.BooleanVar(value=auto_scroll)
        auto_scroll_cb = ctk.CTkCheckBox(
            header,
            text="Auto-scroll",
            variable=self.auto_scroll_var,
            width=20,
            height=20,
            checkbox_width=16,
            checkbox_height=16,
            corner_radius=4,
            fg_color=theme.colors.primary,
            hover_color=theme.colors.primary_hover,
            text_color=theme.colors.text_tertiary,
            font=theme.get_font("xs"),
            command=self._toggle_auto_scroll,
        )
        auto_scroll_cb.pack(side="right", padx=(0, 12))
        
        # Text area
        self.textbox = ctk.CTkTextbox(
            self,
            height=height,
            fg_color=theme.colors.bg_light,
            text_color=theme.colors.text_primary,
            font=(theme.fonts.family_mono, theme.fonts.size_sm),
            corner_radius=theme.dimensions.radius_md,
            border_width=0,
            wrap="word",
            state="disabled",
        )
        self.textbox.pack(fill="both", expand=True, padx=12, pady=(4, 12))
        
        # Configure tags for colors
        for level, color in self._level_colors.items():
            self.textbox._textbox.tag_configure(level, foreground=color)
        
        self.textbox._textbox.tag_configure("TIMESTAMP", foreground=theme.colors.text_tertiary)
    
    def _toggle_auto_scroll(self):
        """Toggle auto-scroll setting."""
        self.auto_scroll = self.auto_scroll_var.get()
    
    def log(
        self,
        message: str,
        level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "SUCCESS"] = "INFO",
        timestamp: Optional[str] = None
    ):
        """Add a log entry."""
        if timestamp is None and self.show_timestamps:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.textbox.configure(state="normal")
        
        # Trim old lines if needed
        self._line_count += 1
        if self._line_count > self._max_lines:
            self.textbox._textbox.delete("1.0", "2.0")
            self._line_count = self._max_lines
        
        # Insert timestamp
        if timestamp:
            self.textbox._textbox.insert("end", f"[{timestamp}] ", "TIMESTAMP")
        
        # Insert message with level color
        self.textbox._textbox.insert("end", f"{message}\n", level)
        
        self.textbox.configure(state="disabled")
        
        # Auto-scroll
        if self.auto_scroll:
            self.textbox._textbox.see("end")
    
    def clear(self):
        """Clear all log entries."""
        self.textbox.configure(state="normal")
        self.textbox._textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")
        self._line_count = 0
    
    def info(self, message: str):
        """Log info message."""
        self.log(message, "INFO")
    
    def warning(self, message: str):
        """Log warning message."""
        self.log(message, "WARNING")
    
    def error(self, message: str):
        """Log error message."""
        self.log(message, "ERROR")
    
    def success(self, message: str):
        """Log success message."""
        self.log(message, "SUCCESS")
    
    def debug(self, message: str):
        """Log debug message."""
        self.log(message, "DEBUG")
