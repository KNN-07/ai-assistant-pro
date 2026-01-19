"""Toast notification components for AI Assistant Pro."""
import customtkinter as ctk
from typing import Callable, Optional, Literal, List
from dataclasses import dataclass
from ui.theme import get_theme


@dataclass
class ToastData:
    """Data for a toast notification."""
    message: str
    toast_type: Literal["success", "error", "warning", "info"]
    duration: int  # milliseconds
    title: Optional[str] = None


class Toast(ctk.CTkFrame):
    """Individual toast notification."""
    
    def __init__(
        self,
        parent,
        message: str,
        toast_type: Literal["success", "error", "warning", "info"] = "info",
        title: Optional[str] = None,
        duration: int = 3000,
        on_dismiss: Optional[Callable] = None,
        **kwargs
    ):
        theme = get_theme()
        
        # Type configurations
        type_config = {
            "success": {"color": theme.colors.success, "icon": "✓"},
            "error": {"color": theme.colors.error, "icon": "✕"},
            "warning": {"color": theme.colors.warning, "icon": "⚠"},
            "info": {"color": theme.colors.info, "icon": "ℹ"},
        }
        
        config = type_config.get(toast_type, type_config["info"])
        
        super().__init__(
            parent,
            fg_color=theme.colors.bg_medium,
            corner_radius=theme.dimensions.radius_md,
            border_width=1,
            border_color=config["color"],
            **kwargs
        )
        
        self.theme = theme
        self.on_dismiss = on_dismiss
        self._duration = duration
        self._destroyed = False
        self._dismiss_timer_id = None
        
        # Bind destroy event
        self.bind("<Destroy>", self._on_destroy)
        
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=12, pady=10)
        
        # Left side: icon
        icon_label = ctk.CTkLabel(
            container,
            text=config["icon"],
            text_color=config["color"],
            font=(theme.fonts.family, 16, "bold"),
            width=24,
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        # Middle: text content
        text_frame = ctk.CTkFrame(container, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)
        
        if title:
            title_label = ctk.CTkLabel(
                text_frame,
                text=title,
                text_color=theme.colors.text_primary,
                font=theme.get_font("sm", "bold"),
                anchor="w",
            )
            title_label.pack(fill="x")
        
        message_label = ctk.CTkLabel(
            text_frame,
            text=message,
            text_color=theme.colors.text_secondary if title else theme.colors.text_primary,
            font=theme.get_font("sm"),
            anchor="w",
            wraplength=250,
        )
        message_label.pack(fill="x")
        
        # Right side: dismiss button
        dismiss_btn = ctk.CTkButton(
            container,
            text="×",
            width=24,
            height=24,
            corner_radius=12,
            fg_color="transparent",
            hover_color=theme.colors.bg_hover,
            text_color=theme.colors.text_tertiary,
            font=(theme.fonts.family, 14),
            command=self._dismiss,
        )
        dismiss_btn.pack(side="right", padx=(10, 0))
        
        # Auto-dismiss timer
        if duration > 0:
            self._dismiss_timer_id = self.after(duration, self._dismiss)
    
    def _on_destroy(self, event=None):
        """Handle widget destruction."""
        if event is not None and event.widget == self:
            self._destroyed = True
            if self._dismiss_timer_id:
                try:
                    self.after_cancel(self._dismiss_timer_id)
                except Exception:
                    pass
                self._dismiss_timer_id = None
    
    def _dismiss(self):
        """Dismiss this toast."""
        if self._destroyed:
            return
        self._destroyed = True
        if self.on_dismiss:
            try:
                self.on_dismiss(self)
            except Exception:
                pass
        try:
            self.destroy()
        except Exception:
            pass


class ToastManager:
    """Manages toast notifications with stacking."""
    
    def __init__(self, parent: ctk.CTk, position: Literal["top-right", "bottom-right", "top-left", "bottom-left"] = "top-right"):
        self.parent = parent
        self.position = position
        self.toasts: List[Toast] = []
        self.theme = get_theme()
        
        # Container for toasts
        self.container = ctk.CTkFrame(parent, fg_color="transparent")
        self._position_container()
        
        # Bind to window resize
        parent.bind("<Configure>", lambda e: self._position_container())
    
    def _position_container(self):
        """Position the toast container based on setting."""
        padding = 20
        
        if "right" in self.position:
            x = self.parent.winfo_width() - padding
            anchor = "ne" if "top" in self.position else "se"
        else:
            x = padding
            anchor = "nw" if "top" in self.position else "sw"
        
        if "top" in self.position:
            y = padding
        else:
            y = self.parent.winfo_height() - padding
        
        self.container.place(x=x, y=y, anchor=anchor)
    
    def show(
        self,
        message: str,
        toast_type: Literal["success", "error", "warning", "info"] = "info",
        title: Optional[str] = None,
        duration: int = 3000,
    ) -> Toast:
        """Show a new toast notification."""
        toast = Toast(
            self.container,
            message=message,
            toast_type=toast_type,
            title=title,
            duration=duration,
            on_dismiss=self._on_toast_dismiss,
        )
        
        # Stack toasts
        toast.pack(pady=(0, 8), fill="x")
        self.toasts.append(toast)
        
        # Limit visible toasts
        if len(self.toasts) > 5:
            old_toast = self.toasts.pop(0)
            old_toast.destroy()
        
        return toast
    
    def _on_toast_dismiss(self, toast: Toast):
        """Handle toast dismissal."""
        if toast in self.toasts:
            self.toasts.remove(toast)
    
    def success(self, message: str, title: Optional[str] = None, duration: int = 3000) -> Toast:
        """Show success toast."""
        return self.show(message, "success", title, duration)
    
    def error(self, message: str, title: Optional[str] = None, duration: int = 5000) -> Toast:
        """Show error toast."""
        return self.show(message, "error", title, duration)
    
    def warning(self, message: str, title: Optional[str] = None, duration: int = 4000) -> Toast:
        """Show warning toast."""
        return self.show(message, "warning", title, duration)
    
    def info(self, message: str, title: Optional[str] = None, duration: int = 3000) -> Toast:
        """Show info toast."""
        return self.show(message, "info", title, duration)
    
    def clear_all(self):
        """Dismiss all toasts."""
        for toast in self.toasts[:]:
            try:
                toast.destroy()
            except Exception:
                pass
        self.toasts.clear()
