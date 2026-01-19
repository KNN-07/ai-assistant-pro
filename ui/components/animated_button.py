"""Animated button components for AI Assistant Pro."""
import customtkinter as ctk
from typing import Callable, Optional, Literal
from ui.theme import get_theme


class AnimatedButton(ctk.CTkButton):
    """Button with hover animations and smooth transitions."""
    
    def __init__(
        self,
        parent,
        text: str = "",
        command: Optional[Callable] = None,
        style: Literal["primary", "secondary", "ghost", "danger"] = "primary",
        icon: str = "",
        width: int = 140,
        height: int = 40,
        **kwargs
    ):
        theme = get_theme()
        
        # Style configurations
        styles = {
            "primary": {
                "fg_color": theme.colors.primary,
                "hover_color": theme.colors.primary_hover,
                "text_color": theme.colors.text_primary,
                "border_width": 0,
            },
            "secondary": {
                "fg_color": "transparent",
                "hover_color": theme.colors.bg_hover,
                "text_color": theme.colors.text_primary,
                "border_width": 1,
                "border_color": theme.colors.border,
            },
            "ghost": {
                "fg_color": "transparent",
                "hover_color": theme.colors.bg_hover,
                "text_color": theme.colors.text_secondary,
                "border_width": 0,
            },
            "danger": {
                "fg_color": theme.colors.error,
                "hover_color": "#dc2626",
                "text_color": theme.colors.text_primary,
                "border_width": 0,
            },
        }
        
        config = styles.get(style, styles["primary"])
        display_text = f"{icon} {text}".strip() if icon else text
        
        super().__init__(
            parent,
            text=display_text,
            command=command,
            width=width,
            height=height,
            corner_radius=theme.dimensions.radius_md,
            font=theme.get_font("md", "bold" if style == "primary" else "normal"),
            **config,
            **kwargs
        )
        
        self._original_fg = config["fg_color"]
        self._style = style


class CaptureButton(ctk.CTkFrame):
    """Large circular capture button with pulse animation."""
    
    def __init__(
        self,
        parent,
        command: Optional[Callable] = None,
        size: int = 120,
        **kwargs
    ):
        theme = get_theme()
        
        super().__init__(
            parent,
            fg_color="transparent",
            width=size + 20,
            height=size + 20,
            **kwargs
        )
        
        self.command = command
        self.size = size
        self.theme = theme
        self._is_processing = False
        self._pulse_state = 0
        self._spinner_angle = 0
        self._destroyed = False
        self._after_id = None
        
        # Outer glow ring
        self.glow_ring = ctk.CTkFrame(
            self,
            width=size + 16,
            height=size + 16,
            corner_radius=(size + 16) // 2,
            fg_color=theme.colors.primary,
        )
        self.glow_ring.place(relx=0.5, rely=0.5, anchor="center")
        
        # Main button
        self.button = ctk.CTkButton(
            self,
            text="⚡",
            width=size,
            height=size,
            corner_radius=size // 2,
            fg_color=theme.colors.primary,
            hover_color=theme.colors.primary_hover,
            text_color=theme.colors.text_primary,
            font=(theme.fonts.family, 32, "bold"),
            command=self._on_click,
        )
        self.button.place(relx=0.5, rely=0.5, anchor="center")
        
        # Status label below
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            text_color=theme.colors.text_secondary,
            font=theme.get_font("sm"),
        )
        self.status_label.place(relx=0.5, rely=1.0, anchor="s", y=25)
        
        # Bind destroy event to stop animation
        self.bind("<Destroy>", self._on_destroy)
        
        # Start pulse animation
        self._animate_pulse()
    
    def _on_destroy(self, event=None):
        """Handle widget destruction."""
        self._destroyed = True
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
    
    def _on_click(self):
        if self.command and not self._is_processing:
            self.command()
    
    def _animate_pulse(self):
        """Animate the glow ring pulsing."""
        # Check if widget still exists
        if self._destroyed:
            return
        
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return
        
        try:
            if self._is_processing:
                # Spinner animation
                self._spinner_angle = (self._spinner_angle + 30) % 360
                spinner_chars = ["◐", "◓", "◑", "◒"]
                self.button.configure(text=spinner_chars[self._spinner_angle // 90])
            else:
                # Pulse animation - subtle opacity change via color
                self._pulse_state = (self._pulse_state + 1) % 20
                
                # Blend primary color with background
                self.glow_ring.configure(
                    fg_color=self.theme.colors.primary if self._pulse_state < 10 
                    else self.theme.colors.primary_hover
                )
            
            self._after_id = self.after(100, self._animate_pulse)
        except Exception:
            # Widget destroyed or error, stop animation
            pass
    
    def set_processing(self, processing: bool, status: str = ""):
        """Set processing state."""
        if self._destroyed:
            return
            
        self._is_processing = processing
        
        try:
            if processing:
                self.button.configure(
                    fg_color=self.theme.colors.warning,
                    hover_color=self.theme.colors.warning,
                )
                self.status_label.configure(text=status or "Processing...")
            else:
                self.button.configure(
                    text="⚡",
                    fg_color=self.theme.colors.primary,
                    hover_color=self.theme.colors.primary_hover,
                )
                self.status_label.configure(text=status or "Ready")
        except Exception:
            pass
    
    def set_status(self, text: str):
        """Update status text."""
        if self._destroyed:
            return
        try:
            self.status_label.configure(text=text)
        except Exception:
            pass
    
    def destroy(self):
        """Override destroy to cleanup."""
        self._on_destroy()
        super().destroy()
