"""Settings window for AI Assistant Pro."""
import customtkinter as ctk
from typing import Callable, Optional, TYPE_CHECKING
from ui.theme import get_theme
from ui.components import AnimatedButton, Card, Toast

if TYPE_CHECKING:
    from core.config_manager import ConfigManager


class SettingsWindow(ctk.CTkToplevel):
    """Modern settings window with tabbed interface."""
    
    def __init__(
        self,
        parent,
        config_manager: 'ConfigManager',
        on_save: Optional[Callable[[], None]] = None,
        on_test_api: Optional[Callable[[str], tuple]] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.theme = get_theme()
        self.config = config_manager
        self.on_save = on_save
        self.on_test_api = on_test_api
        
        # Temp storage for unsaved changes
        self._temp_api_keys = list(config_manager.get_all_api_keys())
        
        self._setup_window()
        self._create_ui()
    
    def _setup_window(self):
        """Configure window properties."""
        self.title("Settings")
        self.geometry("550x650")
        self.minsize(500, 600)
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
        x = parent_x + (parent_w - 550) // 2
        y = parent_y + (parent_h - 650) // 2
        self.geometry(f"550x650+{x}+{y}")
    
    def _create_ui(self):
        """Create the settings UI."""
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            header,
            text="Settings",
            text_color=self.theme.colors.text_primary,
            font=(self.theme.fonts.family, 20, "bold"),
        )
        title.pack(side="left")
        
        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            scrollbar_button_color=self.theme.colors.bg_light,
            scrollbar_button_hover_color=self.theme.colors.bg_hover,
        )
        scroll_frame.pack(fill="both", expand=True)
        
        # Sections
        self._create_hotkey_section(scroll_frame)
        self._create_api_section(scroll_frame)
        self._create_prompt_section(scroll_frame)
        self._create_options_section(scroll_frame)
        
        # Footer with buttons
        self._create_footer(container)
    
    def _create_section_header(self, parent, title: str, description: str = ""):
        """Create a section header."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(16, 8))
        
        label = ctk.CTkLabel(
            frame,
            text=title,
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("md", "bold"),
        )
        label.pack(anchor="w")
        
        if description:
            desc = ctk.CTkLabel(
                frame,
                text=description,
                text_color=self.theme.colors.text_tertiary,
                font=self.theme.get_font("sm"),
            )
            desc.pack(anchor="w")
        
        return frame
    
    def _create_hotkey_section(self, parent):
        """Create hotkey configuration section."""
        self._create_section_header(parent, "Hotkeys", "Configure keyboard shortcuts")
        
        card = Card(parent, padding=16)
        card.pack(fill="x", pady=(0, 8))
        
        # Main hotkey
        row1 = ctk.CTkFrame(card.content, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(
            row1,
            text="Analyze Hotkey",
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("sm"),
        ).pack(side="left")
        
        self.hotkey_entry = ctk.CTkEntry(
            row1,
            width=180,
            height=36,
            fg_color=self.theme.colors.bg_light,
            border_color=self.theme.colors.border,
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("sm"),
        )
        self.hotkey_entry.pack(side="right")
        self.hotkey_entry.insert(0, self.config.get_hotkey())
        
        # Capture hotkey
        row2 = ctk.CTkFrame(card.content, fg_color="transparent")
        row2.pack(fill="x")
        
        ctk.CTkLabel(
            row2,
            text="Queue Capture Hotkey",
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("sm"),
        ).pack(side="left")
        
        self.capture_hotkey_entry = ctk.CTkEntry(
            row2,
            width=180,
            height=36,
            fg_color=self.theme.colors.bg_light,
            border_color=self.theme.colors.border,
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("sm"),
        )
        self.capture_hotkey_entry.pack(side="right")
        self.capture_hotkey_entry.insert(0, self.config.get_capture_hotkey())
    
    def _create_api_section(self, parent):
        """Create API keys section."""
        self._create_section_header(parent, "Gemini API", "Manage your API keys")
        
        card = Card(parent, padding=16)
        card.pack(fill="x", pady=(0, 8))
        
        # API keys list
        self.keys_frame = ctk.CTkFrame(card.content, fg_color="transparent")
        self.keys_frame.pack(fill="x", pady=(0, 12))
        
        self._refresh_keys_list()
        
        # Add key button
        add_frame = ctk.CTkFrame(card.content, fg_color="transparent")
        add_frame.pack(fill="x", pady=(0, 12))
        
        self.new_key_entry = ctk.CTkEntry(
            add_frame,
            placeholder_text="Enter new API key...",
            show="•",
            height=36,
            fg_color=self.theme.colors.bg_light,
            border_color=self.theme.colors.border,
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("sm"),
        )
        self.new_key_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        add_btn = AnimatedButton(
            add_frame,
            text="Add",
            style="primary",
            width=70,
            height=36,
            command=self._add_api_key,
        )
        add_btn.pack(side="right")
        
        # Model name
        model_frame = ctk.CTkFrame(card.content, fg_color="transparent")
        model_frame.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(
            model_frame,
            text="Model",
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("sm"),
        ).pack(side="left")
        
        self.model_entry = ctk.CTkEntry(
            model_frame,
            width=220,
            height=36,
            fg_color=self.theme.colors.bg_light,
            border_color=self.theme.colors.border,
            text_color=self.theme.colors.text_primary,
            placeholder_text="e.g. gemini-2.5-flash-preview-05-20",
            font=self.theme.get_font("sm"),
        )
        self.model_entry.pack(side="right")
        self.model_entry.insert(0, self.config.get_model())
        
        # Auto-rotate checkbox
        self.auto_rotate_var = ctk.BooleanVar(value=self.config.is_auto_rotate_enabled())
        auto_rotate_cb = ctk.CTkCheckBox(
            card.content,
            text="Auto-rotate keys on quota error",
            variable=self.auto_rotate_var,
            fg_color=self.theme.colors.primary,
            hover_color=self.theme.colors.primary_hover,
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("sm"),
        )
        auto_rotate_cb.pack(anchor="w")
    
    def _refresh_keys_list(self):
        """Refresh the API keys list display."""
        # Clear existing
        for widget in self.keys_frame.winfo_children():
            widget.destroy()
        
        if not self._temp_api_keys:
            empty_label = ctk.CTkLabel(
                self.keys_frame,
                text="No API keys configured",
                text_color=self.theme.colors.text_tertiary,
                font=self.theme.get_font("sm"),
            )
            empty_label.pack(pady=8)
            return
        
        current_idx = self.config.get('gemini.current_key_index', 0)
        
        for i, key in enumerate(self._temp_api_keys):
            row = ctk.CTkFrame(self.keys_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            # Masked key display
            masked = key[:8] + "..." + key[-4:] if len(key) > 12 else key
            is_active = i == current_idx
            
            indicator = ctk.CTkLabel(
                row,
                text="●" if is_active else "○",
                text_color=self.theme.colors.success if is_active else self.theme.colors.text_tertiary,
                font=self.theme.get_font("xs"),
                width=20,
            )
            indicator.pack(side="left")
            
            key_label = ctk.CTkLabel(
                row,
                text=masked,
                text_color=self.theme.colors.text_primary if is_active else self.theme.colors.text_secondary,
                font=(self.theme.fonts.family_mono, 12),
            )
            key_label.pack(side="left", padx=(4, 0))
            
            if is_active:
                active_badge = ctk.CTkLabel(
                    row,
                    text="Active",
                    text_color=self.theme.colors.success,
                    font=self.theme.get_font("xs"),
                )
                active_badge.pack(side="left", padx=(8, 0))
            
            # Remove button
            remove_btn = ctk.CTkButton(
                row,
                text="×",
                width=24,
                height=24,
                corner_radius=12,
                fg_color="transparent",
                hover_color=self.theme.colors.error,
                text_color=self.theme.colors.text_tertiary,
                font=(self.theme.fonts.family, 14),
                command=lambda k=key: self._remove_api_key(k),
            )
            remove_btn.pack(side="right")
    
    def _add_api_key(self):
        """Add a new API key."""
        key = self.new_key_entry.get().strip()
        if not key:
            return
        
        if key in self._temp_api_keys:
            return
        
        self._temp_api_keys.append(key)
        self.new_key_entry.delete(0, "end")
        self._refresh_keys_list()
    
    def _remove_api_key(self, key: str):
        """Remove an API key."""
        if key in self._temp_api_keys:
            self._temp_api_keys.remove(key)
            self._refresh_keys_list()
    
    def _create_prompt_section(self, parent):
        """Create system prompt section."""
        self._create_section_header(parent, "System Prompt", "Customize AI behavior")
        
        card = Card(parent, padding=16)
        card.pack(fill="x", pady=(0, 8))
        
        self.prompt_text = ctk.CTkTextbox(
            card.content,
            height=100,
            fg_color=self.theme.colors.bg_light,
            border_color=self.theme.colors.border,
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("sm"),
            corner_radius=self.theme.dimensions.radius_md,
            wrap="word",
        )
        self.prompt_text.pack(fill="x")
        self.prompt_text.insert("1.0", self.config.get_system_prompt())
    
    def _create_options_section(self, parent):
        """Create general options section."""
        self._create_section_header(parent, "Options", "General settings")
        
        card = Card(parent, padding=16)
        card.pack(fill="x", pady=(0, 8))
        
        # Auto-paste
        self.auto_paste_var = ctk.BooleanVar(value=self.config.is_auto_paste_enabled())
        ctk.CTkCheckBox(
            card.content,
            text="Auto-paste response",
            variable=self.auto_paste_var,
            fg_color=self.theme.colors.primary,
            hover_color=self.theme.colors.primary_hover,
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("sm"),
        ).pack(anchor="w", pady=(0, 8))
        
        # Restore clipboard
        self.restore_clipboard_var = ctk.BooleanVar(
            value=self.config.get('auto_paste.restore_clipboard', False)
        )
        ctk.CTkCheckBox(
            card.content,
            text="Restore clipboard after paste",
            variable=self.restore_clipboard_var,
            fg_color=self.theme.colors.primary,
            hover_color=self.theme.colors.primary_hover,
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("sm"),
        ).pack(anchor="w", pady=(0, 8))
        
        # Startup
        self.startup_var = ctk.BooleanVar(
            value=self.config.get('startup.launch_on_boot', False)
        )
        ctk.CTkCheckBox(
            card.content,
            text="Launch on Windows startup",
            variable=self.startup_var,
            fg_color=self.theme.colors.primary,
            hover_color=self.theme.colors.primary_hover,
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("sm"),
        ).pack(anchor="w", pady=(0, 12))
        
        # Paste delay
        delay_frame = ctk.CTkFrame(card.content, fg_color="transparent")
        delay_frame.pack(fill="x")
        
        ctk.CTkLabel(
            delay_frame,
            text="Paste delay (ms)",
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("sm"),
        ).pack(side="left")
        
        self.delay_entry = ctk.CTkEntry(
            delay_frame,
            width=80,
            height=32,
            fg_color=self.theme.colors.bg_light,
            border_color=self.theme.colors.border,
            text_color=self.theme.colors.text_primary,
            font=self.theme.get_font("sm"),
        )
        self.delay_entry.pack(side="right")
        self.delay_entry.insert(0, str(self.config.get_paste_delay()))
    
    def _create_footer(self, parent):
        """Create footer with save/cancel buttons."""
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x", pady=(16, 0))
        
        cancel_btn = AnimatedButton(
            footer,
            text="Cancel",
            style="secondary",
            width=100,
            command=self.destroy,
        )
        cancel_btn.pack(side="left")
        
        save_btn = AnimatedButton(
            footer,
            text="Save Changes",
            style="primary",
            width=140,
            command=self._save_settings,
        )
        save_btn.pack(side="right")
    
    def _save_settings(self):
        """Save all settings."""
        # Hotkeys
        self.config.set('hotkey', self.hotkey_entry.get().strip())
        self.config.set('capture_hotkey', self.capture_hotkey_entry.get().strip())
        
        # API keys and model
        self.config.set('gemini.api_keys', self._temp_api_keys)
        self.config.set('gemini.auto_rotate_on_quota_error', self.auto_rotate_var.get())
        
        # Model name
        model_name = self.model_entry.get().strip()
        if model_name:
            self.config.set('gemini.model', model_name)
        
        # Prompt
        self.config.set('gemini.system_prompt', self.prompt_text.get("1.0", "end").strip())
        
        # Options
        self.config.set('auto_paste.enabled', self.auto_paste_var.get())
        self.config.set('auto_paste.restore_clipboard', self.restore_clipboard_var.get())
        self.config.set('startup.launch_on_boot', self.startup_var.get())
        
        try:
            delay = int(self.delay_entry.get())
            self.config.set('auto_paste.delay_ms', delay)
        except ValueError:
            pass
        
        if self.on_save:
            self.on_save()
        
        self.destroy()
