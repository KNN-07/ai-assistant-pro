"""Floating widget for quick capture access."""
import customtkinter as ctk
from typing import Callable, Optional
from ui.theme import get_theme


class FloatingWidget(ctk.CTkToplevel):
    """Compact floating widget for quick access to capture."""
    
    def __init__(
        self,
        parent,
        on_capture: Optional[Callable[[], None]] = None,
        on_toggle: Optional[Callable[[bool], None]] = None,
        position: tuple[int, int] = (50, 50),
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.theme = get_theme()
        self.on_capture = on_capture
        self.on_toggle = on_toggle
        self.is_enabled = True
        self._queue_count = 0
        
        # Window properties
        self.overrideredirect(True)  # Borderless
        self.attributes("-topmost", True)  # Always on top
        self.attributes("-alpha", 0.95)  # Slight transparency
        self.configure(fg_color=self.theme.colors.bg_medium)
        
        # Size
        self.geometry(f"160x50+{position[0]}+{position[1]}")
        
        # Dragging support
        self._drag_data = {"x": 0, "y": 0}
        
        self._create_ui()
        self._bind_drag()
    
    def _create_ui(self):
        """Create the widget UI."""
        # Main container with rounded corners simulation
        container = ctk.CTkFrame(
            self,
            fg_color=self.theme.colors.bg_medium,
            corner_radius=12,
            border_width=1,
            border_color=self.theme.colors.border,
        )
        container.pack(fill="both", expand=True, padx=2, pady=2)
        
        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=8, pady=6)
        
        # Status indicator
        self.status_dot = ctk.CTkLabel(
            inner,
            text="●",
            text_color=self.theme.colors.success,
            font=(self.theme.fonts.family, 10),
            width=16,
        )
        self.status_dot.pack(side="left")
        
        # Queue count
        self.queue_label = ctk.CTkLabel(
            inner,
            text="",
            text_color=self.theme.colors.warning,
            font=self.theme.get_font("xs"),
        )
        self.queue_label.pack(side="left", padx=(4, 0))
        
        # Capture button
        self.capture_btn = ctk.CTkButton(
            inner,
            text="⚡",
            width=32,
            height=32,
            corner_radius=16,
            fg_color=self.theme.colors.primary,
            hover_color=self.theme.colors.primary_hover,
            text_color=self.theme.colors.text_primary,
            font=(self.theme.fonts.family, 14),
            command=self._handle_capture,
        )
        self.capture_btn.pack(side="right")
        
        # Toggle button
        self.toggle_btn = ctk.CTkButton(
            inner,
            text="⏸",
            width=28,
            height=28,
            corner_radius=14,
            fg_color="transparent",
            hover_color=self.theme.colors.bg_hover,
            text_color=self.theme.colors.text_secondary,
            font=(self.theme.fonts.family, 12),
            command=self._handle_toggle,
        )
        self.toggle_btn.pack(side="right", padx=(0, 4))
    
    def _bind_drag(self):
        """Bind drag events for moving the widget."""
        self.bind("<Button-1>", self._on_drag_start)
        self.bind("<B1-Motion>", self._on_drag_motion)
        
        # Also bind to children
        for widget in self.winfo_children():
            widget.bind("<Button-1>", self._on_drag_start)
            widget.bind("<B1-Motion>", self._on_drag_motion)
    
    def _on_drag_start(self, event):
        """Record starting position for drag."""
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
    
    def _on_drag_motion(self, event):
        """Handle drag motion."""
        x = self.winfo_x() + (event.x - self._drag_data["x"])
        y = self.winfo_y() + (event.y - self._drag_data["y"])
        self.geometry(f"+{x}+{y}")
    
    def _handle_capture(self):
        """Handle capture button click."""
        if self.on_capture:
            self.on_capture()
    
    def _handle_toggle(self):
        """Handle toggle button click."""
        self.is_enabled = not self.is_enabled
        
        if self.is_enabled:
            self.status_dot.configure(text_color=self.theme.colors.success)
            self.toggle_btn.configure(text="⏸")
            self.capture_btn.configure(
                fg_color=self.theme.colors.primary,
                hover_color=self.theme.colors.primary_hover,
            )
        else:
            self.status_dot.configure(text_color=self.theme.colors.text_tertiary)
            self.toggle_btn.configure(text="▶")
            self.capture_btn.configure(
                fg_color=self.theme.colors.bg_light,
                hover_color=self.theme.colors.bg_hover,
            )
        
        if self.on_toggle:
            self.on_toggle(self.is_enabled)
    
    def set_processing(self, processing: bool):
        """Update processing state."""
        if processing:
            self.capture_btn.configure(
                text="◐",
                fg_color=self.theme.colors.warning,
            )
        else:
            self.capture_btn.configure(
                text="⚡",
                fg_color=self.theme.colors.primary,
            )
    
    def update_queue_count(self, count: int):
        """Update queue count display."""
        self._queue_count = count
        if count > 0:
            self.queue_label.configure(text=f"({count})")
        else:
            self.queue_label.configure(text="")
    
    def get_position(self) -> tuple[int, int]:
        """Get current widget position."""
        return (self.winfo_x(), self.winfo_y())
