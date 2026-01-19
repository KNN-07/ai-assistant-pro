"""Status indicator components for AI Assistant Pro."""
import customtkinter as ctk
from typing import Literal, Optional
from ui.theme import get_theme


class StatusIndicator(ctk.CTkFrame):
    """Small colored status dot with optional pulse animation."""
    
    def __init__(
        self,
        parent,
        status: Literal["success", "warning", "error", "info", "inactive"] = "success",
        size: int = 10,
        pulse: bool = False,
        **kwargs
    ):
        theme = get_theme()
        
        super().__init__(
            parent,
            fg_color="transparent",
            width=size + 4,
            height=size + 4,
            **kwargs
        )
        
        self.theme = theme
        self._size = size
        self._pulse = pulse
        self._pulse_state = 0
        
        # Status colors
        self._colors = {
            "success": theme.colors.success,
            "warning": theme.colors.warning,
            "error": theme.colors.error,
            "info": theme.colors.info,
            "inactive": theme.colors.text_tertiary,
        }
        
        self._current_color = self._colors.get(status, theme.colors.success)
        
        # Dot
        self.dot = ctk.CTkFrame(
            self,
            width=size,
            height=size,
            corner_radius=size // 2,
            fg_color=self._current_color,
        )
        self.dot.place(relx=0.5, rely=0.5, anchor="center")
        
        if pulse:
            self._animate_pulse()
    
    def _animate_pulse(self):
        """Animate pulse effect."""
        if not self._pulse:
            return
            
        self._pulse_state = (self._pulse_state + 1) % 20
        
        # Scale effect simulation via size change
        if self._pulse_state < 10:
            scale = 1.0 + (self._pulse_state * 0.02)
        else:
            scale = 1.2 - ((self._pulse_state - 10) * 0.02)
        
        new_size = int(self._size * scale)
        self.dot.configure(width=new_size, height=new_size, corner_radius=new_size // 2)
        
        self.after(80, self._animate_pulse)
    
    def set_status(self, status: Literal["success", "warning", "error", "info", "inactive"]):
        """Update status color."""
        self._current_color = self._colors.get(status, self.theme.colors.success)
        self.dot.configure(fg_color=self._current_color)
    
    def set_pulse(self, pulse: bool):
        """Enable or disable pulse animation."""
        was_pulsing = self._pulse
        self._pulse = pulse
        if pulse and not was_pulsing:
            self._animate_pulse()


class StatusBadge(ctk.CTkFrame):
    """Pill-shaped badge with status indicator and text."""
    
    def __init__(
        self,
        parent,
        text: str = "Active",
        status: Literal["success", "warning", "error", "info", "inactive"] = "success",
        **kwargs
    ):
        theme = get_theme()
        
        # Status colors and icons
        self._status_config = {
            "success": {"color": theme.colors.success, "icon": "●"},
            "warning": {"color": theme.colors.warning, "icon": "●"},
            "error": {"color": theme.colors.error, "icon": "●"},
            "info": {"color": theme.colors.info, "icon": "●"},
            "inactive": {"color": theme.colors.text_tertiary, "icon": "○"},
        }
        
        config = self._status_config.get(status, self._status_config["success"])
        
        super().__init__(
            parent,
            fg_color=theme.colors.bg_light,
            corner_radius=theme.dimensions.radius_full,
            **kwargs
        )
        
        self.theme = theme
        
        # Inner container
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(padx=12, pady=6)
        
        # Icon
        self.icon_label = ctk.CTkLabel(
            inner,
            text=config["icon"],
            text_color=config["color"],
            font=(theme.fonts.family, 10),
        )
        self.icon_label.pack(side="left", padx=(0, 6))
        
        # Text
        self.text_label = ctk.CTkLabel(
            inner,
            text=text,
            text_color=theme.colors.text_primary,
            font=theme.get_font("sm", "bold"),
        )
        self.text_label.pack(side="left")
    
    def set_status(
        self, 
        text: str, 
        status: Literal["success", "warning", "error", "info", "inactive"] = "success"
    ):
        """Update badge status and text."""
        config = self._status_config.get(status, self._status_config["success"])
        self.icon_label.configure(text=config["icon"], text_color=config["color"])
        self.text_label.configure(text=text)
