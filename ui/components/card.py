"""Card components for AI Assistant Pro."""
import customtkinter as ctk
from typing import Optional, Literal
from ui.theme import get_theme


class Card(ctk.CTkFrame):
    """Container card with rounded corners and subtle styling."""
    
    def __init__(
        self,
        parent,
        title: Optional[str] = None,
        padding: int = 16,
        **kwargs
    ):
        theme = get_theme()
        
        # Remove our custom args before passing to parent
        super().__init__(
            parent,
            fg_color=theme.colors.bg_medium,
            corner_radius=theme.dimensions.radius_lg,
            border_width=1,
            border_color=theme.colors.border,
            **kwargs
        )
        
        self.theme = theme
        self._padding = padding
        
        # Content frame with padding
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=padding, pady=padding)
        
        # Optional title
        if title:
            self.title_label = ctk.CTkLabel(
                self.content,
                text=title,
                text_color=theme.colors.text_primary,
                font=theme.get_font("md", "bold"),
                anchor="w",
            )
            self.title_label.pack(fill="x", pady=(0, 12))


class StatsCard(ctk.CTkFrame):
    """Card displaying a statistic with label."""
    
    def __init__(
        self,
        parent,
        value: str = "0",
        label: str = "Label",
        icon: str = "",
        color: Optional[str] = None,
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
        self._color = color or theme.colors.primary
        
        # Inner padding
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Icon and label row
        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x")
        
        if icon:
            icon_label = ctk.CTkLabel(
                top_row,
                text=icon,
                text_color=self._color,
                font=(theme.fonts.family, 16),
            )
            icon_label.pack(side="left", padx=(0, 8))
        
        self.label_widget = ctk.CTkLabel(
            top_row,
            text=label,
            text_color=theme.colors.text_secondary,
            font=theme.get_font("sm"),
            anchor="w",
        )
        self.label_widget.pack(side="left", fill="x", expand=True)
        
        # Value
        self.value_widget = ctk.CTkLabel(
            inner,
            text=value,
            text_color=theme.colors.text_primary,
            font=(theme.fonts.family, 28, "bold"),
            anchor="w",
        )
        self.value_widget.pack(fill="x", pady=(8, 0))
    
    def set_value(self, value: str):
        """Update the displayed value."""
        self.value_widget.configure(text=value)
    
    def set_label(self, label: str):
        """Update the label."""
        self.label_widget.configure(text=label)


class StatusCard(ctk.CTkFrame):
    """Card showing current status with indicator."""
    
    def __init__(
        self,
        parent,
        title: str = "Status",
        status: str = "Active",
        status_type: Literal["success", "warning", "error", "info"] = "success",
        description: str = "",
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
        
        # Status colors
        self._status_colors = {
            "success": theme.colors.success,
            "warning": theme.colors.warning,
            "error": theme.colors.error,
            "info": theme.colors.info,
        }
        
        # Inner padding
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Title row
        title_row = ctk.CTkFrame(inner, fg_color="transparent")
        title_row.pack(fill="x")
        
        self.title_widget = ctk.CTkLabel(
            title_row,
            text=title,
            text_color=theme.colors.text_secondary,
            font=theme.get_font("sm"),
            anchor="w",
        )
        self.title_widget.pack(side="left")
        
        # Status row
        status_row = ctk.CTkFrame(inner, fg_color="transparent")
        status_row.pack(fill="x", pady=(8, 0))
        
        # Status dot
        self.dot = ctk.CTkLabel(
            status_row,
            text="●",
            text_color=self._status_colors.get(status_type, theme.colors.success),
            font=(theme.fonts.family, 14),
        )
        self.dot.pack(side="left", padx=(0, 8))
        
        # Status text
        self.status_widget = ctk.CTkLabel(
            status_row,
            text=status,
            text_color=theme.colors.text_primary,
            font=theme.get_font("lg", "bold"),
            anchor="w",
        )
        self.status_widget.pack(side="left")
        
        # Description
        if description:
            self.desc_widget = ctk.CTkLabel(
                inner,
                text=description,
                text_color=theme.colors.text_tertiary,
                font=theme.get_font("sm"),
                anchor="w",
            )
            self.desc_widget.pack(fill="x", pady=(8, 0))
        else:
            self.desc_widget = None
    
    def set_status(
        self, 
        status: str, 
        status_type: Literal["success", "warning", "error", "info"] = "success",
        description: str = ""
    ):
        """Update the status display."""
        color = self._status_colors.get(status_type, self.theme.colors.success)
        self.dot.configure(text_color=color)
        self.status_widget.configure(text=status)
        
        if self.desc_widget and description:
            self.desc_widget.configure(text=description)
