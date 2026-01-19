"""API Key management dialog."""
import customtkinter as ctk
from typing import Callable, Optional
from ui.theme import get_theme


class APIKeyDialog(ctk.CTkToplevel):
    """Dialog for adding/testing API keys."""
    
    def __init__(
        self,
        parent,
        on_add: Optional[Callable[[str], None]] = None,
        on_test: Optional[Callable[[str], tuple[bool, str]]] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.theme = get_theme()
        self.on_add = on_add
        self.on_test = on_test
        
        self._setup_window()
        self._create_ui()
    
    def _setup_window(self):
        """Configure window properties."""
        self.title("Add API Key")
        self.geometry("450x200")
        self.resizable(False, False)
        self.configure(fg_color=self.theme.colors.bg_dark)
        
        # Make modal
        self.transient(self.master)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_w = self.master.winfo_width()
        parent_h = self.master.winfo_height()
        x = parent_x + (parent_w - 450) // 2
        y = parent_y + (parent_h - 200) // 2
        self.geometry(f"450x200+{x}+{y}")
    
    def _create_ui(self):
        """Create dialog UI."""
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=24)
        
        # Title
        title = ctk.CTkLabel(
            container,
            text="Add Gemini API Key",
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("lg", "bold"),
        )
        title.pack(anchor="w")
        
        # Description
        desc = ctk.CTkLabel(
            container,
            text="Get your API key from Google AI Studio",
            text_color=self.theme.colors.text_tertiary,
            font=self.theme.get_font("sm"),
        )
        desc.pack(anchor="w", pady=(4, 16))
        
        # Entry
        self.key_entry = ctk.CTkEntry(
            container,
            placeholder_text="Enter your API key...",
            show="•",
            height=40,
            fg_color=self.theme.colors.bg_medium,
            border_color=self.theme.colors.border,
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("md"),
        )
        self.key_entry.pack(fill="x", pady=(0, 8))
        self.key_entry.focus()
        
        # Status label
        self.status_label = ctk.CTkLabel(
            container,
            text="",
            text_color=self.theme.colors.text_secondary,
            font=self.theme.get_font("sm"),
        )
        self.status_label.pack(anchor="w", pady=(0, 16))
        
        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=80,
            height=36,
            corner_radius=self.theme.dimensions.radius_md,
            fg_color="transparent",
            hover_color=self.theme.colors.bg_hover,
            text_color=self.theme.colors.text_primary,
            border_width=1,
            border_color=self.theme.colors.border,
            font=self.theme.get_font("sm"),
            command=self.destroy,
        )
        cancel_btn.pack(side="left")
        
        test_btn = ctk.CTkButton(
            btn_frame,
            text="Test",
            width=80,
            height=36,
            corner_radius=self.theme.dimensions.radius_md,
            fg_color=self.theme.colors.bg_light,
            hover_color=self.theme.colors.bg_hover,
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("sm"),
            command=self._test_key,
        )
        test_btn.pack(side="right", padx=(8, 0))
        
        add_btn = ctk.CTkButton(
            btn_frame,
            text="Add Key",
            width=100,
            height=36,
            corner_radius=self.theme.dimensions.radius_md,
            fg_color=self.theme.colors.primary,
            hover_color=self.theme.colors.primary_hover,
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("sm", "bold"),
            command=self._add_key,
        )
        add_btn.pack(side="right")
        
        # Bind enter key
        self.key_entry.bind("<Return>", lambda e: self._add_key())
    
    def _test_key(self):
        """Test the entered API key."""
        key = self.key_entry.get().strip()
        if not key:
            self._show_status("Please enter an API key", "error")
            return
        
        self._show_status("Testing...", "info")
        
        if self.on_test:
            success, message = self.on_test(key)
            if success:
                self._show_status("✓ API key is valid!", "success")
            else:
                self._show_status(f"✕ {message}", "error")
    
    def _add_key(self):
        """Add the entered API key."""
        key = self.key_entry.get().strip()
        if not key:
            self._show_status("Please enter an API key", "error")
            return
        
        if self.on_add:
            self.on_add(key)
        
        self.destroy()
    
    def _show_status(self, message: str, status_type: str = "info"):
        """Update status message."""
        colors = {
            "info": self.theme.colors.text_secondary,
            "success": self.theme.colors.success,
            "error": self.theme.colors.error,
        }
        self.status_label.configure(
            text=message,
            text_color=colors.get(status_type, self.theme.colors.text_secondary)
        )
