"""
Study Tracker - Modern UI Styling
"""

import tkinter as tk
from tkinter import ttk

# ============================================
# COLOR PALETTE
# ============================================

class Colors:
    """Modern color scheme"""
    PRIMARY = "#1a73e8"
    PRIMARY_DARK = "#1557b0"
    PRIMARY_LIGHT = "#4285f4"
    
    SECONDARY = "#34a853"
    WARNING = "#fbbc04"
    DANGER = "#ea4335"
    
    WHITE = "#ffffff"
    LIGHT_GRAY = "#f8f9fa"
    GRAY = "#e8eaed"
    DARK_GRAY = "#5f6368"
    BLACK = "#202124"
    
    BG_PRIMARY = "#ffffff"
    BG_SECONDARY = "#f8f9fa"
    BG_SIDEBAR = "#f1f3f4"
    
    TEXT_PRIMARY = "#202124"
    TEXT_SECONDARY = "#5f6368"
    TEXT_LIGHT = "#80868b"


# ============================================
# FONTS
# ============================================

class Fonts:
    """Font configurations"""
    FAMILY = "Segoe UI"
    
    TITLE = ("Segoe UI", 24, "bold")
    HEADING_1 = ("Segoe UI", 20, "bold")
    HEADING_2 = ("Segoe UI", 16, "bold")
    HEADING_3 = ("Segoe UI", 14, "bold")
    BODY = ("Segoe UI", 11)
    BODY_BOLD = ("Segoe UI", 11, "bold")
    SMALL = ("Segoe UI", 9)
    BUTTON = ("Segoe UI", 11, "bold")


# ============================================
# CUSTOM WIDGETS
# ============================================

class ModernButton(tk.Button):
    """Beautiful button with hover effects"""
    def __init__(self, parent, text, command, style="primary", **kwargs):
        if style == "primary":
            bg = Colors.PRIMARY
            fg = Colors.WHITE
            hover_bg = Colors.PRIMARY_DARK
        elif style == "success":
            bg = Colors.SECONDARY
            fg = Colors.WHITE
            hover_bg = "#2d8e47"
        elif style == "danger":
            bg = Colors.DANGER
            fg = Colors.WHITE
            hover_bg = "#c5221f"
        else:
            bg = Colors.PRIMARY
            fg = Colors.WHITE
            hover_bg = Colors.PRIMARY_DARK
        
        super().__init__(
            parent,
            text=text,
            command=command,
            font=Fonts.BUTTON,
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=Colors.WHITE,
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10,
            **kwargs
        )
        
        self.default_bg = bg
        self.hover_bg = hover_bg
        
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
    
    def _on_hover(self, event):
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        self.config(bg=self.default_bg)


class Card(tk.Frame):
    """Modern card component"""
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg=Colors.WHITE,
            relief=tk.FLAT,
            **kwargs
        )
        self.config(highlightbackground=Colors.GRAY, highlightthickness=1)


class SectionHeader(tk.Label):
    """Section header with consistent styling"""
    def __init__(self, parent, text, **kwargs):
        super().__init__(
            parent,
            text=text,
            font=Fonts.HEADING_2,
            bg=Colors.BG_PRIMARY,
            fg=Colors.TEXT_PRIMARY,
            anchor=tk.W,
            **kwargs
        )


# ============================================
# ICONS
# ============================================

class Icons:
    """Emoji icons"""
    COURSES = "📚"
    LOG = "⏱️"
    SCHEDULE = "📅"
    STATS = "📊"
    EXAM = "🎯"
    ADD = "➕"
    EDIT = "✏️"
    DELETE = "🗑️"
    SAVE = "💾"
    REFRESH = "🔄"
    SUCCESS = "✅"
    WARNING = "⚠️"
    INFO = "ℹ️"
    CALENDAR = "📆"
    CHART = "📈"
    STAR = "⭐"
    PRIORITY_HIGH = "🔴"
    PRIORITY_MED = "🟡"
    PRIORITY_LOW = "🟢"


# ============================================
# STYLING FUNCTIONS
# ============================================

def configure_styles():
    """Configure ttk styles for the application"""
    style = ttk.Style()
    style.theme_use('clam')
    
    # TFrame
    style.configure("TFrame", background=Colors.BG_PRIMARY)
    style.configure("Sidebar.TFrame", background=Colors.BG_SIDEBAR)
    
    # TLabel
    style.configure(
        "TLabel",
        background=Colors.BG_PRIMARY,
        foreground=Colors.TEXT_PRIMARY,
        font=Fonts.BODY
    )
    
    style.configure(
        "Sidebar.TLabel",
        background=Colors.BG_SIDEBAR,
        foreground=Colors.TEXT_PRIMARY,
        font=Fonts.BODY
    )
    
    # TButton
    style.configure(
        "TButton",
        font=Fonts.BUTTON,
        borderwidth=0,
        focuscolor='none',
        padding=10
    )
    
    style.configure(
        "Sidebar.TButton",
        font=Fonts.BODY_BOLD,
        background=Colors.BG_SIDEBAR,
        borderwidth=0,
        focuscolor='none',
        padding=12
    )
    
    style.map(
        "Sidebar.TButton",
        background=[('active', Colors.PRIMARY_LIGHT), ('!active', Colors.BG_SIDEBAR)],
        foreground=[('active', Colors.WHITE), ('!active', Colors.TEXT_PRIMARY)]
    )
    
    # TEntry
    style.configure(
        "TEntry",
        fieldbackground=Colors.WHITE,
        borderwidth=1,
        relief=tk.SOLID,
        padding=8
    )
    
    # TLabelframe
    style.configure(
        "TLabelframe",
        background=Colors.BG_PRIMARY,
        borderwidth=1
    )
    
    style.configure(
        "TLabelframe.Label",
        font=Fonts.HEADING_3,
        foreground=Colors.PRIMARY
    )
