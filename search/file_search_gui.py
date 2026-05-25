import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from threading import Thread, Lock
import fnmatch
from queue import Queue
import time


class FileSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional File Search")
        self.root.geometry("1150x820")
        self.root.resizable(True, True)

        # Modern color scheme
        self.colors = {
            'bg': '#f0f0f0',
            'primary': '#0078d4',
            'secondary': '#106ebe',
            'success': '#107c10',
            'text': '#323130',
            'border': '#d1d1d1'
        }

        # Configure root background
        self.root.configure(bg=self.colors['bg'])

        # Search results storage
        self.search_results = []
        self.is_searching = False
        self.result_queue = Queue()
        self.display_lock = Lock()
        self.sort_column = None
        self.sort_reverse = False

        self.setup_theme()
        self.setup_ui()

        # Keyboard shortcuts
        self.root.bind('<F5>', lambda e: self.start_search())
        self.root.bind('<Escape>', lambda e: self.stop_search() if self.is_searching else None)
        self.root.bind('<Control-l>', lambda e: self.dir_entry.focus())
        self.root.bind('<Return>', lambda e: self.start_search() if not self.is_searching else None)

        # Start periodic queue processing
        self.process_result_queue()

    def setup_theme(self):
        """Configure modern theme styling"""
        style = ttk.Style()

        # Try to use a modern theme
        try:
            style.theme_use('vista')  # Windows modern theme
        except:
            try:
                style.theme_use('clam')  # Cross-platform alternative
            except:
                pass

        # Configure colors for widgets
        style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'), foreground=self.colors['primary'])
        style.configure('Subtitle.TLabel', font=('Segoe UI', 9), foreground='#666666')
        style.configure('TLabelframe.Label', font=('Segoe UI', 10, 'bold'), foreground=self.colors['text'])
        style.configure('TButton', font=('Segoe UI', 9), padding=6)
        style.configure('Search.TButton', font=('Segoe UI', 10, 'bold'), padding=8)
        style.configure('Treeview', font=('Segoe UI', 9), rowheight=25)
        style.configure('Treeview.Heading', font=('Segoe UI', 9, 'bold'))

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)

        # Title with modern styling
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, pady=(0, 15))

        title_label = ttk.Label(title_frame, text="🔍 File & Folder Search Tool",
                                style='Title.TLabel')
        title_label.pack()

        subtitle_label = ttk.Label(title_frame, text="Fast and efficient file searching",
                                   style='Subtitle.TLabel')
        subtitle_label.pack()

        # Directory selection frame
        dir_frame = ttk.LabelFrame(main_frame, text="Search Location", padding="10")
        dir_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)

        ttk.Label(dir_frame, text="Directory:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.dir_path = tk.StringVar(value="A:/")
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_path, font=('Arial', 10))
        self.dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))

        self.browse_btn = ttk.Button(dir_frame, text="Browse", command=self.browse_directory)
        self.browse_btn.grid(row=0, column=2)

        # Search criteria frame
        criteria_frame = ttk.LabelFrame(main_frame, text="Search Criteria", padding="10")
        criteria_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        criteria_frame.columnconfigure(1, weight=1)

        # Search pattern
        ttk.Label(criteria_frame, text="Search Pattern:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=5)
        self.pattern = tk.StringVar(value="*")
        self.pattern_entry = ttk.Entry(criteria_frame, textvariable=self.pattern, font=('Arial', 10))
        self.pattern_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=5)

        # Quick pattern buttons
        quick_pattern_frame = ttk.Frame(criteria_frame)
        quick_pattern_frame.grid(row=0, column=2, sticky=tk.W, padx=(5, 0))
        ttk.Button(quick_pattern_frame, text="*.txt", width=6,
                   command=lambda: self.pattern.set("*.txt")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_pattern_frame, text="*.pdf", width=6,
                   command=lambda: self.pattern.set("*.pdf")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_pattern_frame, text="*.*", width=6,
                   command=lambda: self.pattern.set("*")).pack(side=tk.LEFT, padx=2)

        # Search type - Fixed layout
        ttk.Label(criteria_frame, text="Search Type:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=5)

        # Create a frame for radio buttons to better control layout
        radio_frame = ttk.Frame(criteria_frame)
        radio_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)

        self.search_type = tk.StringVar(value="both")
        ttk.Radiobutton(radio_frame, text="Files Only", variable=self.search_type, value="files").pack(side=tk.LEFT,
                                                                                                       padx=(0, 10))
        ttk.Radiobutton(radio_frame, text="Folders Only", variable=self.search_type, value="folders").pack(side=tk.LEFT,
                                                                                                           padx=(0, 10))
        ttk.Radiobutton(radio_frame, text="Both", variable=self.search_type, value="both").pack(side=tk.LEFT)

        # Options frame
        options_frame = ttk.Frame(criteria_frame)
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.case_sensitive = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Case Sensitive", variable=self.case_sensitive).pack(side=tk.LEFT,
                                                                                                 padx=(0, 10))

        self.subfolders = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include Subfolders", variable=self.subfolders).pack(side=tk.LEFT)

        self.real_time = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Real-time Display", variable=self.real_time).pack(side=tk.LEFT,
                                                                                               padx=(10, 0))

        # Search button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(0, 10))

        self.search_btn = ttk.Button(button_frame, text="🔍 Start Search", command=self.start_search,
                                     style='Search.TButton')
        self.search_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = ttk.Button(button_frame, text="⏹ Stop", command=self.stop_search, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

        self.clear_btn = ttk.Button(button_frame, text="🗑 Clear Results", command=self.clear_results)
        self.clear_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Progress bar and status
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)

        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        self.result_count_label = ttk.Label(progress_frame, text="Found: 0 items")
        self.result_count_label.grid(row=0, column=1, sticky=tk.E)

        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="📁 Search Results (Click column headers to sort • Double-click to open)", padding="10")
        results_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Create Treeview with scrollbars
        tree_container = ttk.Frame(results_frame)
        tree_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        # Treeview for results
        columns = ('Type', 'Name', 'Path', 'Size', 'Modified')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='tree headings', height=20, selectmode='extended')

        # Define headings with sorting
        self.tree.heading('#0', text='')
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))

        # Set column widths
        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('Type', width=80)
        self.tree.column('Name', width=200)
        self.tree.column('Path', width=350)
        self.tree.column('Size', width=100)
        self.tree.column('Modified', width=140)

        # Add scrollbars
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Bind double-click event
        self.tree.bind('<Double-Button-1>', self.open_item)
        self.tree.bind('<Button-3>', self.show_context_menu)  # Right-click menu

        # Context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Open", command=self.open_selected_item)
        self.context_menu.add_command(label="Open Containing Folder", command=self.open_containing_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy Path", command=self.copy_path)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Rename...", command=self.rename_selected_item)
        self.context_menu.add_command(label="Delete", command=self.delete_selected_items)

        # Keyboard shortcuts for rename/delete
        self.tree.bind('<F2>', lambda e: self.rename_selected_item())
        self.tree.bind('<Delete>', lambda e: self.delete_selected_items())

        # Status bar
        self.status_var = tk.StringVar(value="Ready • F5: Search • Esc: Stop • Enter: Start Search")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, font=('Arial', 9))
        status_bar.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # Export button
        export_frame = ttk.Frame(main_frame)
        export_frame.grid(row=7, column=0, pady=(5, 0))

        export_btn = ttk.Button(export_frame, text="💾 Export Results to File", command=self.export_results)
        export_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_on_open = tk.BooleanVar(value=False)
        ttk.Checkbutton(export_frame, text="Stop search when opening item", variable=self.stop_on_open).pack(
            side=tk.LEFT)

    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select Directory to Search")
        if directory:
            self.dir_path.set(directory)

    def start_search(self):
        # Validate inputs
        if not self.dir_path.get():
            messagebox.showerror("Error", "Please select a directory to search")
            return

        # Try to access the directory (works for all drives including A:)
        try:
            os.listdir(self.dir_path.get())
        except (FileNotFoundError, OSError, PermissionError) as e:
            messagebox.showerror("Error", f"Cannot access directory: {str(e)}")
            return

        # Clear previous results
        self.clear_results()

        # Reset search state
        self.search_results = []
        self.is_searching = True
        self.result_count_label.config(text="Found: 0 items")

        # Disable search button, enable stop button
        self.search_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        # Start search in separate thread
        self.search_thread = Thread(target=self.perform_search, daemon=True)
        self.search_thread.start()

        # Start progress bar
        self.progress.start()

    def perform_search(self):
        try:
            search_path = self.dir_path.get()
            pattern = self.pattern.get().strip()

            # Auto-wildcard: always wrap pattern with * at prefix and suffix
            if pattern:
                if not pattern.startswith('*'):
                    pattern = '*' + pattern
                if not pattern.endswith('*'):
                    pattern = pattern + '*'
                # Update the pattern field to show the auto-wildcard
                self.root.after(0, lambda: self.pattern.set(pattern))

            search_type = self.search_type.get()
            case_sensitive = self.case_sensitive.get()
            include_subfolders = self.subfolders.get()
            real_time = self.real_time.get()

            # Update status
            self.update_status(f"Searching in {search_path}...")

            items_processed = 0
            found_count = 0
            batch_results = []  # Batch for faster updates

            # Walk through directory
            if include_subfolders:
                for root, dirs, files in os.walk(search_path):
                    if not self.is_searching:
                        break

                    # Search folders
                    if search_type in ['folders', 'both']:
                        for dir_name in dirs:
                            if not self.is_searching:
                                break
                            if self.match_pattern(dir_name, pattern, case_sensitive):
                                full_path = os.path.join(root, dir_name)
                                try:
                                    mtime = os.path.getmtime(full_path)
                                    mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
                                except:
                                    mtime_str = ''
                                result = ('Folder', dir_name, full_path, '', mtime_str)
                                self.search_results.append(result)
                                found_count += 1

                                if real_time:
                                    batch_results.append(result)

                    # Search files
                    if search_type in ['files', 'both']:
                        for file_name in files:
                            if not self.is_searching:
                                break
                            if self.match_pattern(file_name, pattern, case_sensitive):
                                full_path = os.path.join(root, file_name)
                                try:
                                    stat_info = os.stat(full_path)
                                    size = self.format_size(stat_info.st_size)
                                    mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat_info.st_mtime))
                                except:
                                    size = ''
                                    mtime_str = ''
                                result = ('File', file_name, full_path, size, mtime_str)
                                self.search_results.append(result)
                                found_count += 1

                                if real_time:
                                    batch_results.append(result)

                    # Batch update every 100 items
                    if real_time and len(batch_results) >= 100:
                        for r in batch_results:
                            self.add_result_to_queue(r)
                        batch_results.clear()

                    items_processed += len(dirs) + len(files)
                    if items_processed % 500 == 0:
                        self.update_status(
                            f"Searching... Processed {items_processed} items, found {found_count} matches")
                        self.update_result_count(found_count)

                # Add remaining batch results
                if real_time and batch_results:
                    for r in batch_results:
                        self.add_result_to_queue(r)
            else:
                # Search only top directory
                try:
                    items = os.listdir(search_path)
                    total_items = len(items)

                    for i, item in enumerate(items):
                        if not self.is_searching:
                            break

                        full_path = os.path.join(search_path, item)

                        if os.path.isdir(full_path) and search_type in ['folders', 'both']:
                            if self.match_pattern(item, pattern, case_sensitive):
                                result = ('Folder', item, full_path, '',
                                          self.get_modified_time(full_path))
                                self.search_results.append(result)
                                found_count += 1

                                if real_time:
                                    self.add_result_to_queue(result)

                        elif os.path.isfile(full_path) and search_type in ['files', 'both']:
                            if self.match_pattern(item, pattern, case_sensitive):
                                size = self.get_file_size(full_path)
                                result = ('File', item, full_path, size,
                                          self.get_modified_time(full_path))
                                self.search_results.append(result)
                                found_count += 1

                                if real_time:
                                    self.add_result_to_queue(result)

                        if (i + 1) % 20 == 0:
                            self.update_status(
                                f"Searching... Processed {i + 1}/{total_items} items, found {found_count} matches")
                            self.update_result_count(found_count)

                except PermissionError:
                    pass

            # Add any remaining results if not in real-time mode
            if not real_time and self.search_results:
                self.display_all_results()

            # Final update
            self.update_status(f"Search completed! Found {len(self.search_results)} item(s)")
            self.update_result_count(len(self.search_results))

            # Search complete
            self.root.after(0, self.search_complete)

        except Exception as e:
            self.root.after(0, self.show_error, f"Search error: {str(e)}")

    def add_result_to_queue(self, result):
        """Add result to queue for GUI thread processing"""
        self.result_queue.put(result)

    def process_result_queue(self):
        """Process results from queue in GUI thread"""
        try:
            while True:
                result = self.result_queue.get_nowait()
                self.insert_result_into_tree(result)
                self.update_result_count(len(self.search_results))
        except:
            pass
        finally:
            # Schedule this method to run again
            self.root.after(100, self.process_result_queue)

    def insert_result_into_tree(self, result):
        """Insert a single result into the treeview"""
        with self.display_lock:
            item_id = self.tree.insert('', 'end', values=result)
            # Auto-scroll to bottom if near bottom
            if self.tree.yview()[1] > 0.9:  # If near bottom
                self.tree.see(item_id)

    def display_all_results(self):
        """Display all results at once"""
        with self.display_lock:
            for result in self.search_results:
                self.tree.insert('', 'end', values=result)

    def update_result_count(self, count):
        """Update the result count label"""
        self.root.after(0, lambda: self.result_count_label.config(text=f"Found: {count} items"))

    def search_complete(self):
        """Called when search is complete"""
        self.progress.stop()
        self.search_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.is_searching = False

        if not self.search_results:
            self.update_status("No results found")

    def match_pattern(self, name, pattern, case_sensitive):
        if not case_sensitive:
            name = name.lower()
            pattern = pattern.lower()

        # Convert wildcard pattern to fnmatch
        return fnmatch.fnmatch(name, pattern)

    def get_file_size(self, filepath):
        try:
            size = os.path.getsize(filepath)
            return self.format_size(size)
        except:
            return "Unknown"

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def get_modified_time(self, path):
        try:
            import time
            mtime = os.path.getmtime(path)
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
        except:
            return "Unknown"

    def open_item(self, event):
        """Handle double-click on tree item"""
        self.open_selected_item()

    def open_selected_item(self):
        """Open the selected file or folder"""
        selection = self.tree.selection()
        if selection:
            # Optionally stop search when opening item
            if self.stop_on_open.get() and self.is_searching:
                self.stop_search()

            item = self.tree.item(selection[0])
            path = item['values'][2]  # Path is the 3rd column
            if os.path.exists(path):
                try:
                    os.startfile(path)
                    self.update_status(f"Opened: {path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot open: {str(e)}")
            else:
                messagebox.showwarning("Not Found", f"Item no longer exists:\n{path}")

    def open_containing_folder(self):
        """Open the folder containing the selected item"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            path = item['values'][2]
            folder = os.path.dirname(path)
            if os.path.exists(folder):
                os.startfile(folder)
                self.update_status(f"Opened folder: {folder}")
            else:
                messagebox.showwarning("Not Found", "Folder no longer exists")

    def copy_path(self):
        """Copy the path of selected item to clipboard"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            path = item['values'][2]
            self.root.clipboard_clear()
            self.root.clipboard_append(path)
            self.update_status(f"Copied to clipboard: {path}")
            messagebox.showinfo("Copied", f"Path copied to clipboard:\n{path}")

    def rename_selected_item(self):
        """Rename the selected file or folder on disk and update the tree."""
        selection = self.tree.selection()
        if not selection:
            return
        if len(selection) > 1:
            messagebox.showinfo("Rename", "Please select a single item to rename.")
            return

        item_id = selection[0]
        values = list(self.tree.item(item_id)['values'])
        item_type, old_name, old_path = values[0], values[1], values[2]

        if not os.path.exists(old_path):
            messagebox.showwarning("Not Found", f"Item no longer exists:\n{old_path}")
            return

        new_name = simpledialog.askstring("Rename", f"Rename {item_type.lower()}:", initialvalue=old_name, parent=self.root)
        if new_name is None or new_name.strip() == '' or new_name == old_name:
            return

        new_path = os.path.join(os.path.dirname(old_path), new_name)
        if os.path.exists(new_path):
            messagebox.showerror("Rename Failed", f"An item with that name already exists:\n{new_path}")
            return

        try:
            os.rename(old_path, new_path)
        except OSError as e:
            messagebox.showerror("Rename Failed", f"Could not rename:\n{str(e)}")
            return

        values[1] = new_name
        values[2] = new_path
        self.tree.item(item_id, values=values)
        self._update_stored_result(old_path, tuple(values))
        self.update_status(f"Renamed: {old_path} → {new_path}")

    def delete_selected_items(self):
        """Delete the selected file(s)/folder(s) from disk. Confirms when multiple are selected."""
        selection = self.tree.selection()
        if not selection:
            return

        paths = []
        for item_id in selection:
            values = self.tree.item(item_id)['values']
            paths.append((item_id, values[0], values[1], values[2]))

        if len(paths) == 1:
            _, item_type, name, path = paths[0]
            if not messagebox.askyesno("Confirm Delete",
                                       f"Delete this {item_type.lower()}?\n\n{name}\n{path}"):
                return
        else:
            preview = "\n".join(f"  • {p[2]}" for p in paths[:10])
            if len(paths) > 10:
                preview += f"\n  ... and {len(paths) - 10} more"
            if not messagebox.askyesno("Confirm Multiple Deletion",
                                       f"Delete {len(paths)} items?\n\n{preview}",
                                       icon='warning'):
                return

        import shutil
        deleted = 0
        errors = []
        for item_id, item_type, name, path in paths:
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

        self.update_result_count(len(self.search_results))
        self.update_status(f"Deleted {deleted} item(s)" + (f"; {len(errors)} error(s)" if errors else ""))
        if errors:
            messagebox.showerror("Delete Errors", "Some items could not be deleted:\n\n" + "\n".join(errors[:20]))

    def _update_stored_result(self, old_path, new_values):
        """Update the in-memory search_results entry matching old_path."""
        for i, r in enumerate(self.search_results):
            if r[2] == old_path:
                self.search_results[i] = new_values
                return

    def _remove_stored_result(self, path):
        """Remove the in-memory search_results entry matching path."""
        self.search_results = [r for r in self.search_results if r[2] != path]

    def show_context_menu(self, event):
        """Show right-click context menu"""
        # If user right-clicks an unselected row, select it (so context menu acts on that row)
        row_id = self.tree.identify_row(event.y)
        if row_id and row_id not in self.tree.selection():
            self.tree.selection_set(row_id)
        selection = self.tree.selection()
        if selection:
            self.context_menu.post(event.x_root, event.y_root)

    def sort_by_column(self, col):
        """Sort treeview by column"""
        # Toggle sort direction if same column
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        # Get column index
        columns = ('Type', 'Name', 'Path', 'Size', 'Modified')
        col_index = columns.index(col)

        # Get all items
        items = [(self.tree.item(item)['values'], item) for item in self.tree.get_children()]

        # Sort items with special handling for Size column
        if col == 'Size':
            # Convert size strings back to bytes for sorting
            def size_key(item):
                size_str = item[0][col_index]
                if not size_str or size_str == 'Unknown':
                    return -1
                try:
                    # Parse size string like "1.5 MB"
                    parts = size_str.split()
                    if len(parts) == 2:
                        num, unit = float(parts[0]), parts[1]
                        multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
                        return num * multipliers.get(unit, 1)
                except:
                    return -1
                return -1
            items.sort(key=size_key, reverse=self.sort_reverse)
        else:
            # Standard string sort
            items.sort(key=lambda x: str(x[0][col_index]).lower(), reverse=self.sort_reverse)

        # Rearrange items
        for index, (values, item) in enumerate(items):
            self.tree.move(item, '', index)

        # Update column heading to show sort direction
        for c in columns:
            heading_text = c
            if c == col:
                heading_text += ' ▼' if self.sort_reverse else ' ▲'
            self.tree.heading(c, text=heading_text, command=lambda c=c: self.sort_by_column(c))

    def clear_results(self):
        """Clear all results from the tree"""
        with self.display_lock:
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.search_results = []
            self.update_result_count(0)
            self.update_status("Results cleared")
            # Reset sort state
            self.sort_column = None
            self.sort_reverse = False
            # Reset column headings
            columns = ('Type', 'Name', 'Path', 'Size', 'Modified')
            for col in columns:
                self.tree.heading(col, text=col)

    def export_results(self):
        if not self.search_results and not self.tree.get_children():
            messagebox.showwarning("No Results", "No search results to export")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"search_results_{self.get_timestamp()}.txt"
        )

        if filepath:
            try:
                results_to_export = self.search_results if self.search_results else self.get_results_from_tree()

                if filepath.endswith('.csv'):
                    # Export as CSV
                    import csv
                    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Type', 'Name', 'Path', 'Size', 'Modified'])
                        writer.writerows(results_to_export)
                else:
                    # Export as text
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write("SEARCH RESULTS\n")
                        f.write("=" * 80 + "\n\n")
                        f.write(f"Search Directory: {self.dir_path.get()}\n")
                        f.write(f"Search Pattern: {self.pattern.get()}\n")
                        f.write(f"Case Sensitive: {self.case_sensitive.get()}\n")
                        f.write(f"Include Subfolders: {self.subfolders.get()}\n")
                        f.write(f"Search Type: {self.search_type.get()}\n")
                        f.write("=" * 80 + "\n\n")

                        for result in results_to_export:
                            f.write(f"Type: {result[0]}\n")
                            f.write(f"Name: {result[1]}\n")
                            f.write(f"Path: {result[2]}\n")
                            f.write(f"Size: {result[3]}\n")
                            f.write(f"Modified: {result[4]}\n")
                            f.write("-" * 80 + "\n")

                        f.write(f"\nTotal Results: {len(results_to_export)}\n")

                messagebox.showinfo("Export Complete", f"Results saved to:\n{filepath}")
                self.update_status(f"Exported {len(results_to_export)} results to {filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to save file: {str(e)}")

    def get_results_from_tree(self):
        """Extract results from treeview"""
        results = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            results.append(values)
        return results

    def get_timestamp(self):
        import datetime
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def stop_search(self):
        self.is_searching = False
        self.update_status("Search stopped by user")
        self.progress.stop()
        self.search_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def update_status(self, message):
        self.root.after(0, lambda: self.status_var.set(message))

    def show_error(self, message):
        self.progress.stop()
        self.search_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.is_searching = False
        messagebox.showerror("Error", message)


def main():
    root = tk.Tk()
    app = FileSearchGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()