"""Theme configuration for AI Assistant Pro using CustomTkinter."""
from dataclasses import dataclass
from typing import Optional, Literal
import customtkinter as ctk


@dataclass(frozen=True)
class ThemeColors:
    """Color palette for the application."""
    # Primary colors
    primary: str = "#6366f1"           # Indigo - main accent
    primary_hover: str = "#818cf8"     # Lighter indigo for hover
    primary_pressed: str = "#4f46e5"   # Darker indigo for pressed
    
    # Secondary colors
    secondary: str = "#10b981"         # Emerald - success/active
    secondary_hover: str = "#34d399"
    
    # Background colors (dark theme)
    bg_darkest: str = "#0f0f14"        # Deepest background
    bg_dark: str = "#16161e"           # Main background
    bg_medium: str = "#1e1e2e"         # Card background
    bg_light: str = "#2a2a3c"          # Elevated elements
    bg_hover: str = "#363648"          # Hover state
    
    # Background colors (light theme)
    bg_light_main: str = "#ffffff"
    bg_light_secondary: str = "#f8f9fa"
    bg_light_card: str = "#ffffff"
    bg_light_hover: str = "#f1f3f5"
    
    # Text colors
    text_primary: str = "#ffffff"      # Main text
    text_secondary: str = "#cbd5e1"    # Muted text (lighter for better contrast)
    text_tertiary: str = "#94a3b8"     # Even more muted (lighter for better contrast)
    text_dark: str = "#1f2937"         # Text for light theme
    
    # Status colors
    success: str = "#34d399"           # Emerald-400 (brighter green)
    error: str = "#f87171"             # Red-400 (softer red)
    warning: str = "#fbbf24"           # Amber-400 (warmer yellow)
    info: str = "#60a5fa"              # Blue-400 (softer blue)
    
    # Border colors
    border: str = "#3f3f4e"            # Lighter border for visibility
    border_light: str = "#4b4b5c"
    border_focus: str = "#818cf8"
    
    # Gradients (as tuples of colors)
    gradient_primary: tuple = ("#6366f1", "#8b5cf6")  # Indigo to Purple
    gradient_success: tuple = ("#10b981", "#22c55e")  # Emerald to Green
    gradient_warm: tuple = ("#f59e0b", "#ef4444")     # Amber to Red


@dataclass(frozen=True)  
class ThemeFonts:
    """Font configuration."""
    family: str = "Segoe UI"
    family_mono: str = "Cascadia Code"
    
    size_xs: int = 11
    size_sm: int = 12
    size_md: int = 14
    size_lg: int = 16
    size_xl: int = 20
    size_xxl: int = 28
    
    weight_normal: str = "normal"
    weight_medium: str = "normal"  # CTk doesn't support medium
    weight_bold: str = "bold"


@dataclass(frozen=True)
class ThemeDimensions:
    """Size and spacing configuration."""
    # Border radius
    radius_sm: int = 8
    radius_md: int = 12
    radius_lg: int = 20
    radius_xl: int = 28
    radius_full: int = 999  # For pills
    
    # Spacing (padding/margin)
    space_xs: int = 6
    space_sm: int = 10
    space_md: int = 16
    space_lg: int = 24
    space_xl: int = 32
    space_xxl: int = 48
    
    # Component sizes
    button_height: int = 44
    button_height_sm: int = 36
    button_height_lg: int = 56
    input_height: int = 44
    card_min_width: int = 320


@dataclass(frozen=True)
class ThemeAnimations:
    """Animation configuration."""
    duration_fast: int = 100      # ms
    duration_normal: int = 200    # ms
    duration_slow: int = 400      # ms
    
    hover_scale: float = 1.02     # Scale on hover
    press_scale: float = 0.98     # Scale on press


class Theme:
    """Complete theme configuration and utilities."""
    
    def __init__(self, mode: Literal["dark", "light", "system"] = "dark"):
        """
        Initialize theme.
        
        Args:
            mode: Theme mode - dark, light, or system
        """
        self.mode = mode
        self.colors = ThemeColors()
        self.fonts = ThemeFonts()
        self.dimensions = ThemeDimensions()
        self.animations = ThemeAnimations()
        
        # Configure CustomTkinter
        ctk.set_appearance_mode(mode)
        ctk.set_default_color_theme("blue")
    
    @property
    def is_dark(self) -> bool:
        """Check if current theme is dark."""
        if self.mode == "system":
            return ctk.get_appearance_mode() == "Dark"
        return self.mode == "dark"
    
    def get_bg(self, level: Literal["darkest", "dark", "medium", "light"] = "dark") -> str:
        """Get background color based on current theme and level."""
        if self.is_dark:
            return getattr(self.colors, f"bg_{level}")
        else:
            mapping = {
                "darkest": self.colors.bg_light_main,
                "dark": self.colors.bg_light_main,
                "medium": self.colors.bg_light_card,
                "light": self.colors.bg_light_secondary
            }
            return mapping.get(level, self.colors.bg_light_main)
    
    def get_text(self, level: Literal["primary", "secondary", "tertiary"] = "primary") -> str:
        """Get text color based on current theme and importance."""
        if self.is_dark:
            return getattr(self.colors, f"text_{level}")
        else:
            return self.colors.text_dark if level == "primary" else self.colors.text_secondary
    
    def get_font(
        self, 
        size: Literal["xs", "sm", "md", "lg", "xl", "xxl"] = "md",
        weight: Literal["normal", "bold"] = "normal",
        mono: bool = False
    ) -> tuple:
        """Get font tuple for CTk widgets."""
        family = self.fonts.family_mono if mono else self.fonts.family
        font_size = getattr(self.fonts, f"size_{size}")
        return (family, font_size, weight)
    
    def configure_ctk_widget(self, widget_type: str) -> dict:
        """Get default configuration for a widget type."""
        configs = {
            "button_primary": {
                "fg_color": self.colors.primary,
                "hover_color": self.colors.primary_hover,
                "text_color": self.colors.text_primary,
                "corner_radius": self.dimensions.radius_md,
                "height": self.dimensions.button_height,
                "font": self.get_font("md", "bold"),
            },
            "button_secondary": {
                "fg_color": "transparent",
                "hover_color": self.colors.bg_hover,
                "text_color": self.colors.text_primary,
                "border_width": 1,
                "border_color": self.colors.border,
                "corner_radius": self.dimensions.radius_md,
                "height": self.dimensions.button_height,
                "font": self.get_font("md"),
            },
            "button_ghost": {
                "fg_color": "transparent",
                "hover_color": self.colors.bg_hover,
                "text_color": self.colors.text_secondary,
                "corner_radius": self.dimensions.radius_md,
                "height": self.dimensions.button_height_sm,
                "font": self.get_font("sm"),
            },
            "card": {
                "fg_color": self.colors.bg_medium,
                "corner_radius": self.dimensions.radius_lg,
            },
            "entry": {
                "fg_color": self.colors.bg_light,
                "border_color": self.colors.border,
                "text_color": self.colors.text_primary,
                "placeholder_text_color": self.colors.text_tertiary,
                "corner_radius": self.dimensions.radius_md,
                "height": self.dimensions.input_height,
                "font": self.get_font("md"),
            },
            "textbox": {
                "fg_color": self.colors.bg_light,
                "border_color": self.colors.border,
                "text_color": self.colors.text_primary,
                "corner_radius": self.dimensions.radius_md,
                "font": self.get_font("md", mono=True),
            },
            "label_title": {
                "text_color": self.colors.text_primary,
                "font": self.get_font("xl", "bold"),
            },
            "label_subtitle": {
                "text_color": self.colors.text_secondary,
                "font": self.get_font("sm"),
            },
        }
        return configs.get(widget_type, {})
    
    def set_mode(self, mode: Literal["dark", "light", "system"]) -> None:
        """Change theme mode."""
        self.mode = mode
        ctk.set_appearance_mode(mode)


# Global theme instance
_theme: Optional[Theme] = None


def get_theme() -> Theme:
    """Get the global theme instance."""
    global _theme
    if _theme is None:
        _theme = Theme()
    return _theme


def set_theme_mode(mode: Literal["dark", "light", "system"]) -> None:
    """Set the global theme mode."""
    get_theme().set_mode(mode)
