"""Tkinter GUI to search for files and folders by name."""

import csv
import datetime
import fnmatch
import os
import shutil
import time
import tkinter as tk
from dataclasses import dataclass
from queue import Empty, Queue
from threading import Lock, Thread
from tkinter import filedialog, messagebox, simpledialog, ttk


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Result tuple shape: (Type, Name, Path, Size, Modified)
COLUMNS = ('Type', 'Name', 'Path', 'Size', 'Modified')
PATH_COL = COLUMNS.index('Path')

DEFAULT_EXCLUDED_DIRS = ('#recycle', 'bt')
SIZE_UNITS = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')

COLORS = {
    'bg':           '#f5f6f8',
    'surface':      '#ffffff',
    'surface_alt':  '#fafbfc',
    'primary':      '#2563eb',
    'primary_hov':  '#1d4ed8',
    'danger':       '#dc2626',
    'text':         '#1f2937',
    'text_muted':   '#6b7280',
    'border':       '#e5e7eb',
    'selection':    '#dbeafe',
    'selection_fg': '#1e3a8a',
    'header_bg':    '#1f2937',
    'header_fg':    '#f9fafb',
}


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def format_size(size_bytes):
    """Render a byte count as a human-readable string."""
    size = float(size_bytes)
    for unit in SIZE_UNITS[:-1]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} {SIZE_UNITS[-1]}"


def parse_size(size_str):
    """Inverse of format_size; returns bytes or -1 if unparseable."""
    if not size_str or size_str == 'Unknown':
        return -1
    try:
        num, unit = size_str.split()
        return float(num) * (1024 ** SIZE_UNITS.index(unit))
    except (ValueError, KeyError):
        return -1


def format_mtime(path):
    """Modified-time string for the path, or '' if it can't be read."""
    try:
        return time.strftime('%Y-%m-%d %H:%M:%S',
                             time.localtime(os.path.getmtime(path)))
    except OSError:
        return ''


def expand_pattern(raw):
    """Wrap a user pattern with leading/trailing * so 'foo' becomes '*foo*'."""
    pattern = (raw or '').strip()
    if not pattern:
        return pattern
    if not pattern.startswith('*'):
        pattern = '*' + pattern
    if not pattern.endswith('*'):
        pattern = pattern + '*'
    return pattern


def name_matches(name, pattern, case_sensitive):
    if not pattern:
        return False
    if case_sensitive:
        return fnmatch.fnmatchcase(name, pattern)
    return fnmatch.fnmatch(name.lower(), pattern.lower())


# ---------------------------------------------------------------------------
# Search parameter bundle
# ---------------------------------------------------------------------------

@dataclass
class SearchOptions:
    path: str
    pattern: str
    search_type: str          # 'files' | 'folders' | 'both'
    case_sensitive: bool
    recursive: bool
    excluded_dirs: set        # lowercase folder names

    @property
    def wants_files(self):
        return self.search_type in ('files', 'both')

    @property
    def wants_folders(self):
        return self.search_type in ('folders', 'both')


# ---------------------------------------------------------------------------
# Main GUI
# ---------------------------------------------------------------------------

class FileSearchGUI:
    BATCH_SIZE = 100
    WALK_STATUS_EVERY = 500
    TOPLEVEL_STATUS_EVERY = 20
    QUEUE_POLL_MS = 100

    def __init__(self, root):
        self.root = root
        self.colors = COLORS

        self.search_results = []
        self.is_searching = False
        self.result_queue = Queue()
        self.display_lock = Lock()
        self.sort_column = None
        self.sort_reverse = False

        self._init_window()
        self._setup_theme()
        self._build_ui()
        self._bind_shortcuts()
        self.process_result_queue()

    # ========================================================================
    # Window / theme / shortcuts
    # ========================================================================

    def _init_window(self):
        self.root.title("File Search")
        self.root.geometry("1180x920")
        self.root.minsize(960, 700)
        self.root.resizable(True, True)
        self.root.configure(bg=self.colors['bg'])

    def _bind_shortcuts(self):
        bindings = (
            ('<F5>',        lambda e: self.start_search()),
            ('<Return>',    lambda e: self.start_search() if not self.is_searching else None),
            ('<Escape>',    lambda e: self.stop_search() if self.is_searching else None),
            ('<Control-l>', lambda e: self.dir_entry.focus()),
            ('<Control-a>', self._handle_ctrl_a),
            ('<Control-A>', self._handle_ctrl_a),
        )
        for sequence, handler in bindings:
            self.root.bind(sequence, handler)

    def _setup_theme(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        self._style_base(style)
        self._style_labels(style)
        self._style_cards(style)
        self._style_inputs(style)
        self._style_buttons(style)
        self._style_treeview(style)
        self._style_misc(style)

    def _style_base(self, style):
        c = self.colors
        style.configure('.', background=c['bg'], foreground=c['text'],
                        font=('Segoe UI', 10))
        style.configure('TFrame', background=c['bg'])
        style.configure('Card.TFrame', background=c['surface'], relief='flat')
        style.configure('TCheckbutton', background=c['bg'], foreground=c['text'])
        style.configure('TRadiobutton', background=c['bg'], foreground=c['text'])
        style.map('TCheckbutton', background=[('active', c['bg'])])
        style.map('TRadiobutton', background=[('active', c['bg'])])

    def _style_labels(self, style):
        c = self.colors
        style.configure('TLabel', background=c['bg'], foreground=c['text'])
        style.configure('Title.TLabel',    font=('Segoe UI Semibold', 18),
                        foreground=c['text'], background=c['bg'])
        style.configure('Subtitle.TLabel', font=('Segoe UI', 9),
                        foreground=c['text_muted'], background=c['bg'])
        # Used inside cards (surface background)
        style.configure('Section.TLabel',  font=('Segoe UI Semibold', 10),
                        foreground=c['text'], background=c['surface'])
        style.configure('Hint.TLabel',     font=('Segoe UI', 9),
                        foreground=c['text_muted'], background=c['surface'])
        style.configure('Muted.TLabel',    font=('Segoe UI', 9),
                        foreground=c['text_muted'], background=c['bg'])

    def _style_cards(self, style):
        c = self.colors
        # Raised bevel for a subtle elevated-card 3D feel
        style.configure('Card.TLabelframe',
                        background=c['surface'],
                        bordercolor=c['border'],
                        lightcolor='#ffffff',
                        darkcolor='#cbd5e1',
                        relief='raised', borderwidth=1)
        style.configure('Card.TLabelframe.Label',
                        font=('Segoe UI Semibold', 10),
                        foreground=c['text'], background=c['surface'])
        # Manual drop-shadow color (used by tk.Frame wrappers)
        style.configure('Shadow.TFrame', background='#d1d5db')

    def _style_inputs(self, style):
        c = self.colors
        style.configure('TEntry',
                        fieldbackground=c['surface'], background=c['surface'],
                        foreground=c['text'], bordercolor=c['border'],
                        lightcolor=c['border'], darkcolor=c['border'],
                        padding=6)
        style.map('TEntry',
                  bordercolor=[('focus', c['primary'])],
                  lightcolor=[('focus', c['primary'])],
                  darkcolor=[('focus', c['primary'])])

    def _style_buttons(self, style):
        c = self.colors
        style.configure('TButton',
                        font=('Segoe UI', 9),
                        background=c['surface'], foreground=c['text'],
                        bordercolor=c['border'], focusthickness=0,
                        padding=(12, 6), relief='flat')
        style.map('TButton',
                  background=[('active', '#eef2f7'), ('pressed', '#e2e8f0')],
                  bordercolor=[('active', c['primary']), ('focus', c['primary'])])

        style.configure('Primary.TButton',
                        font=('Segoe UI Semibold', 10),
                        background=c['primary'], foreground='#ffffff',
                        bordercolor=c['primary'], padding=(16, 8), relief='flat')
        style.map('Primary.TButton',
                  background=[('active', c['primary_hov']), ('disabled', '#9ca3af')],
                  bordercolor=[('active', c['primary_hov']), ('disabled', '#9ca3af')],
                  foreground=[('disabled', '#f3f4f6')])

        style.configure('Danger.TButton',
                        font=('Segoe UI Semibold', 10),
                        background=c['surface'], foreground=c['danger'],
                        bordercolor=c['danger'], padding=(14, 7), relief='flat')
        style.map('Danger.TButton',
                  background=[('active', '#fee2e2'), ('disabled', c['surface'])],
                  foreground=[('disabled', '#d1d5db')],
                  bordercolor=[('disabled', c['border'])])

        style.configure('Chip.TButton', font=('Segoe UI', 9), padding=(8, 3))

    def _style_treeview(self, style):
        c = self.colors
        style.configure('Treeview',
                        font=('Segoe UI', 10),
                        background=c['surface'], fieldbackground=c['surface'],
                        foreground=c['text'], bordercolor=c['border'],
                        rowheight=28, relief='flat')
        style.map('Treeview',
                  background=[('selected', c['selection'])],
                  foreground=[('selected', c['selection_fg'])])
        style.configure('Treeview.Heading',
                        font=('Segoe UI Semibold', 9),
                        background=c['header_bg'], foreground=c['header_fg'],
                        relief='flat', padding=(8, 6),
                        bordercolor=c['header_bg'])
        style.map('Treeview.Heading',
                  background=[('active', '#374151')],
                  relief=[('pressed', 'flat')])

    def _style_misc(self, style):
        c = self.colors
        style.configure('Horizontal.TProgressbar',
                        troughcolor=c['border'], background=c['primary'],
                        bordercolor=c['border'],
                        lightcolor=c['primary'], darkcolor=c['primary'])
        style.configure('Vertical.TScrollbar',
                        background=c['surface'], troughcolor=c['bg'],
                        bordercolor=c['border'], arrowcolor=c['text_muted'])
        style.configure('Horizontal.TScrollbar',
                        background=c['surface'], troughcolor=c['bg'],
                        bordercolor=c['border'], arrowcolor=c['text_muted'])
        style.configure('TSeparator', background=c['border'])

    # ========================================================================
    # UI builders
    # ========================================================================

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=(18, 16, 18, 14))
        main.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(5, weight=1)

        self._build_banner(main, row=0)
        self._build_location_card(main, row=1)
        self._build_criteria_card(main, row=2)
        self._build_action_row(main, row=3)
        self._build_progress_row(main, row=4)
        self._build_results_card(main, row=5)
        self._build_status_bar(main, row=6)

    # ----- banner -----------------------------------------------------------

    BANNER_HEIGHT = 110
    BANNER_TOP_COLOR = '#1e293b'      # slate-800
    BANNER_BOTTOM_COLOR = '#334155'   # slate-700
    BANNER_HIGHLIGHT = '#475569'      # slate-600 (top edge)
    BANNER_LOWLIGHT = '#0f172a'       # slate-900 (bottom edge before stripe)

    def _build_banner(self, parent, row):
        """Canvas banner with gradient + magnifier glyph + title.

        If a banner.png / header.png / banner.gif exists next to this script,
        it is shown instead (PIL is used for .jpg if available).
        """
        wrapper = tk.Frame(parent, bg='#d1d5db', bd=0)
        wrapper.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 14))
        wrapper.columnconfigure(0, weight=1)

        self.banner_canvas = tk.Canvas(
            wrapper, height=self.BANNER_HEIGHT,
            bd=0, highlightthickness=0,
            bg=self.BANNER_TOP_COLOR,
        )
        # 2px right/bottom shadow exposed through the wrapper
        self.banner_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E),
                                padx=(0, 2), pady=(0, 2))

        self._banner_image = None
        self._try_load_banner_image()
        self.banner_canvas.bind('<Configure>', self._render_banner)

    def _try_load_banner_image(self):
        here = os.path.dirname(os.path.abspath(__file__))
        for name in ('banner.png', 'header.png', 'banner.gif'):
            path = os.path.join(here, name)
            if os.path.exists(path):
                try:
                    self._banner_image = tk.PhotoImage(file=path)
                    return
                except tk.TclError:
                    continue
        # JPEG support via PIL if available
        for name in ('banner.jpg', 'banner.jpeg'):
            path = os.path.join(here, name)
            if not os.path.exists(path):
                continue
            try:
                from PIL import Image, ImageTk  # type: ignore
                self._banner_image = ImageTk.PhotoImage(Image.open(path))
                return
            except ImportError:
                return

    def _render_banner(self, event=None):
        canvas = self.banner_canvas
        canvas.delete('all')
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width < 2 or height < 2:
            return

        if self._banner_image is not None:
            canvas.create_image(width // 2, height // 2,
                                image=self._banner_image, anchor=tk.CENTER)
            return

        self._draw_gradient(canvas, self.BANNER_TOP_COLOR,
                            self.BANNER_BOTTOM_COLOR, width, height)

        # Top highlight and bottom lowlight — gives a subtle 3D bevel
        canvas.create_line(0, 0, width, 0, fill=self.BANNER_HIGHLIGHT)
        canvas.create_line(0, height - 4, width, height - 4,
                           fill=self.BANNER_LOWLIGHT)
        # Accent stripe at the very bottom
        canvas.create_rectangle(0, height - 3, width, height,
                                fill=self.colors['primary'], outline='')

        self._draw_magnifier(canvas, cx=60, cy=height // 2 - 1, radius=28)

        # Title text + drop-shadow underlay for a slight engraved feel
        title_x, title_y = 120, height // 2 - 10
        canvas.create_text(title_x + 1, title_y + 1, anchor=tk.W,
                           text='File Search',
                           fill='#0b1220',
                           font=('Segoe UI Semibold', 22))
        canvas.create_text(title_x, title_y, anchor=tk.W,
                           text='File Search',
                           fill='#ffffff',
                           font=('Segoe UI Semibold', 22))
        canvas.create_text(title_x, title_y + 28, anchor=tk.W,
                           text='Quickly find files and folders across any drive.',
                           fill='#cbd5e1',
                           font=('Segoe UI', 10))

    def _draw_magnifier(self, canvas, cx, cy, radius):
        # Outer ring
        canvas.create_oval(cx - radius, cy - radius,
                           cx + radius, cy + radius,
                           outline='#ffffff', width=4)
        # Inner arc highlight to fake a glassy lens
        canvas.create_arc(cx - radius + 5, cy - radius + 5,
                          cx + radius - 5, cy + radius - 5,
                          start=55, extent=65, style=tk.ARC,
                          outline=self.colors['selection'], width=2)
        # Handle
        hx1 = cx + radius * 0.7
        hy1 = cy + radius * 0.7
        hx2 = hx1 + 20
        hy2 = hy1 + 20
        # Shadow under handle for a 3D edge
        canvas.create_line(hx1 + 1, hy1 + 1, hx2 + 1, hy2 + 1,
                           fill='#0b1220', width=6, capstyle=tk.ROUND)
        canvas.create_line(hx1, hy1, hx2, hy2,
                           fill='#ffffff', width=5, capstyle=tk.ROUND)

    @staticmethod
    def _draw_gradient(canvas, top_color, bottom_color, width, height, steps=80):
        r1, g1, b1 = canvas.winfo_rgb(top_color)
        r2, g2, b2 = canvas.winfo_rgb(bottom_color)
        last_steps = max(steps - 1, 1)
        for i in range(steps):
            ratio = i / last_steps
            r = int((r1 + (r2 - r1) * ratio) / 256)
            g = int((g1 + (g2 - g1) * ratio) / 256)
            b = int((b1 + (b2 - b1) * ratio) / 256)
            color = f'#{r:02x}{g:02x}{b:02x}'
            y1 = int(height * i / steps)
            y2 = int(height * (i + 1) / steps) + 1
            canvas.create_rectangle(0, y1, width, y2,
                                    fill=color, outline=color)

    def _build_location_card(self, parent, row):
        card = ttk.LabelFrame(parent, text="  Search Location  ",
                              style='Card.TLabelframe', padding=(14, 10, 14, 12))
        card.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="Directory",
                  style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.dir_path = tk.StringVar(value="A:/")
        self.dir_entry = ttk.Entry(card, textvariable=self.dir_path, font=('Segoe UI', 10))
        self.dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 8), ipady=2)
        ttk.Button(card, text="Browse…",
                   command=self.browse_directory).grid(row=0, column=2)

    def _build_criteria_card(self, parent, row):
        card = ttk.LabelFrame(parent, text="  Search Criteria  ",
                              style='Card.TLabelframe', padding=(14, 10, 14, 12))
        card.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        card.columnconfigure(1, weight=1)

        self._build_pattern_row(card, row=0)
        self._build_search_type_row(card, row=1)
        self._build_options_row(card, row=2)
        self._build_exclude_row(card, row=3)

    def _build_pattern_row(self, card, row):
        ttk.Label(card, text="Pattern",
                  style='Section.TLabel').grid(row=row, column=0, sticky=tk.W,
                                               padx=(0, 10), pady=6)
        self.pattern = tk.StringVar(value="*")
        ttk.Entry(card, textvariable=self.pattern,
                  font=('Segoe UI', 10)).grid(row=row, column=1, sticky=(tk.W, tk.E),
                                              padx=(0, 8), pady=6, ipady=2)
        chips = ttk.Frame(card)
        chips.grid(row=row, column=2, sticky=tk.W)
        for label, value in (("*.txt", "*.txt"), ("*.pdf", "*.pdf"), ("All", "*")):
            ttk.Button(chips, text=label, width=6, style='Chip.TButton',
                       command=lambda v=value: self.pattern.set(v)).pack(side=tk.LEFT, padx=2)

    def _build_search_type_row(self, card, row):
        ttk.Label(card, text="Search For",
                  style='Section.TLabel').grid(row=row, column=0, sticky=tk.W,
                                               padx=(0, 10), pady=6)
        radios = ttk.Frame(card)
        radios.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=6)
        self.search_type = tk.StringVar(value="both")
        for text, value in (("Files only", "files"),
                            ("Folders only", "folders"),
                            ("Both", "both")):
            ttk.Radiobutton(radios, text=text, variable=self.search_type,
                            value=value).pack(side=tk.LEFT, padx=(0, 16))

    def _build_options_row(self, card, row):
        ttk.Label(card, text="Options",
                  style='Section.TLabel').grid(row=row, column=0, sticky=tk.W,
                                               padx=(0, 10), pady=6)
        opts = ttk.Frame(card)
        opts.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=6)
        self.case_sensitive = tk.BooleanVar()
        self.subfolders = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts, text="Case sensitive",
                        variable=self.case_sensitive).pack(side=tk.LEFT, padx=(0, 16))
        ttk.Checkbutton(opts, text="Include subfolders",
                        variable=self.subfolders).pack(side=tk.LEFT)

    def _build_exclude_row(self, card, row):
        ttk.Label(card, text="Exclude",
                  style='Section.TLabel').grid(row=row, column=0, sticky=(tk.N, tk.W),
                                               padx=(0, 10), pady=6)

        container = ttk.Frame(card)
        container.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=6)
        container.columnconfigure(0, weight=1)

        # Listbox with thin border (drawn by a wrapping Frame)
        list_frame = tk.Frame(container, bg=self.colors['border'],
                              bd=0, highlightthickness=0)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.excluded_listbox = tk.Listbox(
            list_frame, height=4,
            selectmode=tk.EXTENDED,
            activestyle='none',
            relief='flat', borderwidth=0,
            bg=self.colors['surface'], fg=self.colors['text'],
            selectbackground=self.colors['primary'],
            selectforeground='#ffffff',
            highlightthickness=0,
            font=('Segoe UI', 10),
            exportselection=False,
        )
        self.excluded_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                                   padx=1, pady=1)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                  command=self.excluded_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.excluded_listbox.configure(yscrollcommand=scrollbar.set)

        for name in DEFAULT_EXCLUDED_DIRS:
            self.excluded_listbox.insert(tk.END, name)
        self.excluded_listbox.select_set(0, tk.END)

        # Action buttons
        btns = ttk.Frame(container)
        btns.grid(row=0, column=1, sticky=(tk.N, tk.W), padx=(8, 0))
        ttk.Button(btns, text="Add…",
                   command=self._add_excluded_dir).pack(fill=tk.X, pady=(0, 4))
        ttk.Button(btns, text="Remove",
                   command=self._remove_excluded_dir).pack(fill=tk.X)

        ttk.Label(container,
                  text="Selected names are skipped during search (case-insensitive). "
                       "Click Add… to pick a folder.",
                  style='Hint.TLabel').grid(row=1, column=0, columnspan=2,
                                            sticky=tk.W, pady=(4, 0))

    def _build_action_row(self, parent, row):
        bar = ttk.Frame(parent)
        bar.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        bar.columnconfigure(2, weight=1)

        self.search_btn = ttk.Button(bar, text="Start Search",
                                     command=self.start_search, style='Primary.TButton')
        self.search_btn.grid(row=0, column=0, padx=(0, 8))

        self.stop_btn = ttk.Button(bar, text="Stop", command=self.stop_search,
                                   state=tk.DISABLED, style='Danger.TButton')
        self.stop_btn.grid(row=0, column=1, padx=(0, 8))

        ttk.Button(bar, text="Clear Results",
                   command=self.clear_results).grid(row=0, column=2, sticky=tk.W)
        ttk.Button(bar, text="Export…",
                   command=self.export_results).grid(row=0, column=3, padx=(8, 0))

        self.stop_on_open = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="Stop search when opening an item",
                        variable=self.stop_on_open).grid(row=0, column=4, padx=(16, 0))

    def _build_progress_row(self, parent, row):
        bar = ttk.Frame(parent)
        bar.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        bar.columnconfigure(0, weight=1)

        self.progress = ttk.Progressbar(bar, mode='indeterminate',
                                        style='Horizontal.TProgressbar')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 12))
        self.progress.grid_remove()  # hidden while idle

        self.result_count_label = ttk.Label(bar, text="Found: 0 items",
                                            style='Muted.TLabel')
        self.result_count_label.grid(row=0, column=1, sticky=tk.E)

    def _build_results_card(self, parent, row):
        card = ttk.LabelFrame(parent, text="  Search Results  ",
                              style='Card.TLabelframe', padding=(10, 8, 10, 10))
        card.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        card.columnconfigure(0, weight=1)
        card.rowconfigure(1, weight=1)

        ttk.Label(card,
                  text="Click a column header to sort  •  Double-click to open  •  "
                       "Ctrl+A: Select all  •  F2: Rename  •  Del: Delete",
                  style='Hint.TLabel').grid(row=0, column=0, sticky=tk.W,
                                            padx=2, pady=(0, 8))

        container = ttk.Frame(card, style='Card.TFrame')
        container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(container, columns=COLUMNS,
                                 show='headings', height=20, selectmode='extended')
        for col in COLUMNS:
            self.tree.heading(col, text=col,
                              command=lambda c=col: self.sort_by_column(c))
        self.tree.column('Type',     width=80,  anchor=tk.W, stretch=False)
        self.tree.column('Name',     width=240, anchor=tk.W)
        self.tree.column('Path',     width=420, anchor=tk.W)
        self.tree.column('Size',     width=100, anchor=tk.E, stretch=False)
        self.tree.column('Modified', width=160, anchor=tk.W, stretch=False)

        self.tree.tag_configure('odd',  background=self.colors['surface'])
        self.tree.tag_configure('even', background=self.colors['surface_alt'])

        vsb = ttk.Scrollbar(container, orient=tk.VERTICAL,
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(container, orient=tk.HORIZONTAL,
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.tree.bind('<Double-Button-1>', self.open_item)
        self.tree.bind('<Button-3>',        self.show_context_menu)
        self.tree.bind('<F2>',              lambda e: self.rename_selected_item())
        self.tree.bind('<Delete>',          lambda e: self.delete_selected_items())

        self.context_menu = self._build_context_menu()

    def _build_context_menu(self):
        menu = tk.Menu(self.root, tearoff=0,
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       activebackground=self.colors['primary'],
                       activeforeground='#ffffff', bd=0)
        menu.add_command(label="Open",                   command=self.open_selected_item)
        menu.add_command(label="Open Containing Folder", command=self.open_containing_folder)
        menu.add_separator()
        menu.add_command(label="Select All\tCtrl+A",     command=self.select_all_results)
        menu.add_command(label="Copy Path",              command=self.copy_path)
        menu.add_separator()
        menu.add_command(label="Rename…\tF2",       command=self.rename_selected_item)
        menu.add_command(label="Delete\tDel",            command=self.delete_selected_items)
        return menu

    def _build_status_bar(self, parent, row):
        self.status_var = tk.StringVar(
            value="Ready  •  F5 Search  •  Esc Stop  •  Enter Start Search")
        # Grooved bevel — gives a subtle sunken 3D appearance
        tk.Label(parent, textvariable=self.status_var,
                 anchor=tk.W,
                 bg=self.colors['surface'], fg=self.colors['text_muted'],
                 bd=2, relief=tk.GROOVE, padx=10, pady=5,
                 font=('Segoe UI', 9),
        ).grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

    # ========================================================================
    # Excluded directories — UI handlers
    # ========================================================================

    def _excluded_dirs_in_use(self):
        """Set of lowercase folder names currently selected in the exclude list."""
        return {self.excluded_listbox.get(i).strip().lower()
                for i in self.excluded_listbox.curselection()
                if self.excluded_listbox.get(i).strip()}

    def _existing_excluded_entries(self):
        return [self.excluded_listbox.get(i)
                for i in range(self.excluded_listbox.size())]

    def _add_excluded_dir(self):
        start = self.dir_path.get() if os.path.isdir(self.dir_path.get()) else None
        folder = filedialog.askdirectory(title="Choose a folder to exclude",
                                         initialdir=start, mustexist=True)
        if not folder:
            return
        name = os.path.basename(folder.rstrip('/\\')) or folder
        if any(e.lower() == name.lower() for e in self._existing_excluded_entries()):
            messagebox.showinfo("Add exclusion",
                                f"'{name}' is already in the list.")
            return
        self.excluded_listbox.insert(tk.END, name)
        self.excluded_listbox.select_set(tk.END)

    def _remove_excluded_dir(self):
        indices = list(self.excluded_listbox.curselection())
        if not indices:
            messagebox.showinfo("Remove exclusion",
                                "Select one or more entries to remove.")
            return
        for i in reversed(indices):
            self.excluded_listbox.delete(i)

    # ========================================================================
    # Search lifecycle
    # ========================================================================

    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select Directory to Search")
        if directory:
            self.dir_path.set(directory)

    def _build_search_options(self):
        pattern = expand_pattern(self.pattern.get())
        # Reflect the auto-wildcarded pattern back to the user
        self.root.after(0, lambda: self.pattern.set(pattern))
        return SearchOptions(
            path=self.dir_path.get(),
            pattern=pattern,
            search_type=self.search_type.get(),
            case_sensitive=self.case_sensitive.get(),
            recursive=self.subfolders.get(),
            excluded_dirs=self._excluded_dirs_in_use(),
        )

    def start_search(self):
        if not self.dir_path.get():
            messagebox.showerror("Error", "Please select a directory to search")
            return
        try:
            os.listdir(self.dir_path.get())
        except OSError as e:
            messagebox.showerror("Error", f"Cannot access directory: {e}")
            return

        self.clear_results()
        self.search_results = []
        self.is_searching = True
        self.result_count_label.config(text="Found: 0 items")
        self.search_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.grid()
        self.progress.start()

        self.search_thread = Thread(target=self._run_search, daemon=True)
        self.search_thread.start()

    def _run_search(self):
        try:
            opts = self._build_search_options()
            self.update_status(f"Searching in {opts.path}...")
            if opts.recursive:
                self._collect_recursive(opts)
            else:
                self._collect_top_level(opts)

            self.update_status("Search complete")
            self.update_result_count(len(self.search_results))
            self.root.after(0, self.search_complete)
        except Exception as e:  # noqa: BLE001 — top-level reporter
            self.root.after(0, self.show_error, f"Search error: {e}")

    def stop_search(self):
        self.is_searching = False
        self.update_status("Search stopped by user")
        self.progress.stop()
        self.progress.grid_remove()
        self.search_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def search_complete(self):
        self.progress.stop()
        self.progress.grid_remove()
        self.search_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.is_searching = False
        if not self.search_results:
            self.update_status("No results found")

    # ========================================================================
    # Collectors
    # ========================================================================

    def _collect_recursive(self, opts):
        processed = 0
        next_status = self.WALK_STATUS_EVERY
        batch = []

        for root, dirs, files in os.walk(opts.path):
            if not self.is_searching:
                break

            # Prune excluded directories so os.walk does not descend into them
            dirs[:] = [d for d in dirs if d.lower() not in opts.excluded_dirs]

            if opts.wants_folders:
                for name in dirs:
                    if not self.is_searching:
                        break
                    if name_matches(name, opts.pattern, opts.case_sensitive):
                        self._emit(self._folder_result(root, name), batch)

            if opts.wants_files:
                for name in files:
                    if not self.is_searching:
                        break
                    if name_matches(name, opts.pattern, opts.case_sensitive):
                        self._emit(self._file_result(root, name), batch)

            if len(batch) >= self.BATCH_SIZE:
                self._flush_batch(batch)

            processed += len(dirs) + len(files)
            if processed >= next_status:
                self._report_progress(processed)
                next_status = processed + self.WALK_STATUS_EVERY

        self._flush_batch(batch)

    def _collect_top_level(self, opts):
        try:
            items = os.listdir(opts.path)
        except PermissionError:
            return

        total = len(items)
        batch = []
        for i, name in enumerate(items, start=1):
            if not self.is_searching:
                break
            full_path = os.path.join(opts.path, name)
            is_dir = os.path.isdir(full_path)

            if is_dir and name.lower() in opts.excluded_dirs:
                continue

            if is_dir:
                if opts.wants_folders and name_matches(name, opts.pattern, opts.case_sensitive):
                    self._emit(self._folder_result(opts.path, name), batch)
            elif opts.wants_files and os.path.isfile(full_path):
                if name_matches(name, opts.pattern, opts.case_sensitive):
                    self._emit(self._file_result(opts.path, name), batch)

            if i % self.TOPLEVEL_STATUS_EVERY == 0:
                self.update_status(
                    f"Searching... processed {i}/{total} items, "
                    f"found {len(self.search_results)} matches")
                self.update_result_count(len(self.search_results))

        self._flush_batch(batch)

    def _report_progress(self, processed):
        self.update_status(
            f"Searching... processed {processed} items, "
            f"found {len(self.search_results)} matches")
        self.update_result_count(len(self.search_results))

    # ========================================================================
    # Result construction & queueing
    # ========================================================================

    def _folder_result(self, root, name):
        full_path = os.path.join(root, name)
        return ('Folder', name, full_path, '', format_mtime(full_path))

    def _file_result(self, root, name):
        full_path = os.path.join(root, name)
        try:
            st = os.stat(full_path)
            size = format_size(st.st_size)
            mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime))
        except OSError:
            size, mtime = '', ''
        return ('File', name, full_path, size, mtime)

    def _emit(self, result, batch):
        self.search_results.append(result)
        batch.append(result)

    def _flush_batch(self, batch):
        for item in batch:
            self.result_queue.put(item)
        batch.clear()

    # ========================================================================
    # Result display
    # ========================================================================

    def process_result_queue(self):
        try:
            while True:
                result = self.result_queue.get_nowait()
                self._insert_result(result)
                self.update_result_count(len(self.search_results))
        except Empty:
            pass
        finally:
            self.root.after(self.QUEUE_POLL_MS, self.process_result_queue)

    def _row_tag(self, index=None):
        if index is None:
            index = len(self.tree.get_children())
        return 'even' if index % 2 == 0 else 'odd'

    def _insert_result(self, result):
        with self.display_lock:
            item_id = self.tree.insert('', 'end', values=result,
                                       tags=(self._row_tag(),))
            if self.tree.yview()[1] > 0.9:
                self.tree.see(item_id)

    def update_result_count(self, count):
        self.root.after(0, lambda: self.result_count_label.config(
            text=f"Found: {count} items"))

    def clear_results(self):
        with self.display_lock:
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.search_results = []
            self.update_result_count(0)
            self.update_status("Results cleared")
            self.sort_column = None
            self.sort_reverse = False
            for col in COLUMNS:
                self.tree.heading(col, text=col)

    # ========================================================================
    # Sorting
    # ========================================================================

    def sort_by_column(self, col):
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        idx = COLUMNS.index(col)
        items = [(self.tree.item(i)['values'], i) for i in self.tree.get_children()]
        if col == 'Size':
            key = lambda row: parse_size(row[0][idx])
        else:
            key = lambda row: str(row[0][idx]).lower()
        items.sort(key=key, reverse=self.sort_reverse)

        for new_index, (_, item) in enumerate(items):
            self.tree.move(item, '', new_index)
            self.tree.item(item, tags=(self._row_tag(new_index),))

        arrow = ' ▼' if self.sort_reverse else ' ▲'
        for c in COLUMNS:
            text = c + arrow if c == col else c
            self.tree.heading(c, text=text, command=lambda c=c: self.sort_by_column(c))

    # ========================================================================
    # Selection & item actions
    # ========================================================================

    def select_all_results(self):
        children = self.tree.get_children()
        if not children:
            return
        self.tree.selection_set(children)
        self.tree.focus(children[0])
        self.update_status(f"Selected all {len(children)} item(s)")

    def _handle_ctrl_a(self, event):
        """Global Ctrl+A — selects all rows unless an Entry/Listbox has focus."""
        focused = self.root.focus_get()
        if isinstance(focused, (tk.Entry, ttk.Entry, tk.Listbox)):
            return
        self.select_all_results()
        return 'break'

    def _selected_path(self):
        """Path of the first selected tree item, or None."""
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])['values'][PATH_COL]

    def open_item(self, event):
        self.open_selected_item()

    def open_selected_item(self):
        path = self._selected_path()
        if not path:
            return
        if self.stop_on_open.get() and self.is_searching:
            self.stop_search()
        if not os.path.exists(path):
            messagebox.showwarning("Not Found", f"Item no longer exists:\n{path}")
            return
        try:
            os.startfile(path)
            self.update_status(f"Opened: {path}")
        except OSError as e:
            messagebox.showerror("Error", f"Cannot open: {e}")

    def open_containing_folder(self):
        path = self._selected_path()
        if not path:
            return
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            messagebox.showwarning("Not Found", "Folder no longer exists")
            return
        os.startfile(folder)
        self.update_status(f"Opened folder: {folder}")

    def copy_path(self):
        path = self._selected_path()
        if not path:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(path)
        self.update_status(f"Copied to clipboard: {path}")
        messagebox.showinfo("Copied", f"Path copied to clipboard:\n{path}")

    def rename_selected_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        if len(sel) > 1:
            messagebox.showinfo("Rename", "Please select a single item to rename.")
            return
        item_id = sel[0]
        values = list(self.tree.item(item_id)['values'])
        item_type, old_name, old_path = values[0], values[1], values[2]

        if not os.path.exists(old_path):
            messagebox.showwarning("Not Found", f"Item no longer exists:\n{old_path}")
            return

        new_name = simpledialog.askstring("Rename",
                                          f"Rename {item_type.lower()}:",
                                          initialvalue=old_name, parent=self.root)
        if not new_name or new_name.strip() == '' or new_name == old_name:
            return

        new_path = os.path.join(os.path.dirname(old_path), new_name)
        if os.path.exists(new_path):
            messagebox.showerror("Rename Failed",
                                 f"An item with that name already exists:\n{new_path}")
            return
        try:
            os.rename(old_path, new_path)
        except OSError as e:
            messagebox.showerror("Rename Failed", f"Could not rename:\n{e}")
            return

        values[1], values[2] = new_name, new_path
        self.tree.item(item_id, values=values)
        self._update_stored_result(old_path, tuple(values))
        self.update_status(f"Renamed: {old_path} → {new_path}")

    def delete_selected_items(self):
        sel = self.tree.selection()
        if not sel:
            return

        # Each row: (item_id, type, name, path)
        rows = []
        for item_id in sel:
            v = self.tree.item(item_id)['values']
            rows.append((item_id, v[0], v[1], v[2]))

        if not self._confirm_delete(rows):
            return

        deleted, errors = self._delete_rows(rows)
        self.update_result_count(len(self.search_results))
        self.update_status(f"Deleted {deleted} item(s)" +
                           (f"; {len(errors)} error(s)" if errors else ""))
        if errors:
            messagebox.showerror("Delete Errors",
                                 "Some items could not be deleted:\n\n" +
                                 "\n".join(errors[:20]))

    def _confirm_delete(self, rows):
        if len(rows) == 1:
            _, item_type, name, path = rows[0]
            return messagebox.askyesno(
                "Confirm Delete",
                f"Delete this {item_type.lower()}?\n\n{name}\n{path}")
        preview = "\n".join(f"  • {r[3]}" for r in rows[:10])
        if len(rows) > 10:
            preview += f"\n  ... and {len(rows) - 10} more"
        return messagebox.askyesno(
            "Confirm Multiple Deletion",
            f"Delete {len(rows)} items?\n\n{preview}",
            icon='warning')

    def _delete_rows(self, rows):
        deleted = 0
        errors = []
        for item_id, _item_type, _name, path in rows:
            try:
                if not os.path.exists(path):
                    errors.append(f"{path} (not found)")
                    continue
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.tree.delete(item_id)
                self._remove_stored_result(path)
                deleted += 1
            except OSError as e:
                errors.append(f"{path}: {e}")
        return deleted, errors

    def _update_stored_result(self, old_path, new_values):
        for i, r in enumerate(self.search_results):
            if r[PATH_COL] == old_path:
                self.search_results[i] = new_values
                return

    def _remove_stored_result(self, path):
        self.search_results = [r for r in self.search_results
                               if r[PATH_COL] != path]

    def show_context_menu(self, event):
        # If user right-clicks an unselected row, select it first
        row_id = self.tree.identify_row(event.y)
        if row_id and row_id not in self.tree.selection():
            self.tree.selection_set(row_id)
        if self.tree.selection():
            self.context_menu.post(event.x_root, event.y_root)

    # ========================================================================
    # Export
    # ========================================================================

    def export_results(self):
        if not self.search_results and not self.tree.get_children():
            messagebox.showwarning("No Results", "No search results to export")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"),
                       ("CSV files", "*.csv"),
                       ("All files", "*.*")],
            initialfile=f"search_results_{self._timestamp()}.txt",
        )
        if not filepath:
            return
        rows = self.search_results or self._results_from_tree()
        try:
            if filepath.lower().endswith('.csv'):
                self._export_csv(filepath, rows)
            else:
                self._export_txt(filepath, rows)
            messagebox.showinfo("Export Complete", f"Results saved to:\n{filepath}")
            self.update_status(f"Exported {len(rows)} results to {filepath}")
        except OSError as e:
            messagebox.showerror("Export Error", f"Failed to save file: {e}")

    def _export_csv(self, filepath, rows):
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS)
            writer.writerows(rows)

    def _export_txt(self, filepath, rows):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("SEARCH RESULTS\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Search Directory: {self.dir_path.get()}\n")
            f.write(f"Search Pattern: {self.pattern.get()}\n")
            f.write(f"Case Sensitive: {self.case_sensitive.get()}\n")
            f.write(f"Include Subfolders: {self.subfolders.get()}\n")
            f.write(f"Search Type: {self.search_type.get()}\n")
            f.write(f"Excluded Dirs: {sorted(self._excluded_dirs_in_use())}\n")
            f.write("=" * 80 + "\n\n")
            for result in rows:
                for label, value in zip(COLUMNS, result):
                    f.write(f"{label}: {value}\n")
                f.write("-" * 80 + "\n")
            f.write(f"\nTotal Results: {len(rows)}\n")

    def _results_from_tree(self):
        return [self.tree.item(i)['values'] for i in self.tree.get_children()]

    @staticmethod
    def _timestamp():
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # ========================================================================
    # Status / errors
    # ========================================================================

    def update_status(self, message):
        self.root.after(0, lambda: self.status_var.set(message))

    def show_error(self, message):
        self.progress.stop()
        self.progress.grid_remove()
        self.search_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.is_searching = False
        messagebox.showerror("Error", message)


def main():
    root = tk.Tk()
    FileSearchGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
