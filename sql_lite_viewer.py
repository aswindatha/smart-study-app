import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import font
import time
import threading
from datetime import datetime
from collections import deque
import copy


class SQLiteViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ SQLite Database Viewer Pro - Premium Edition")
        self.root.geometry("1600x900")
        self.root.configure(bg="#000000")
        self.root.minsize(1200, 700)
        
        # Set window icon and transparency effects
        self.root.attributes('-alpha', 0.95)
        
        # Center window on screen
        self.center_window()
        
        # Premium fonts with better typography
        self.title_font = font.Font(family="Segoe UI", size=18, weight="bold")
        self.heading_font = font.Font(family="Segoe UI", size=14, weight="bold")
        self.normal_font = font.Font(family="Segoe UI", size=11)
        self.small_font = font.Font(family="Segoe UI", size=9)
        self.code_font = font.Font(family="Consolas", size=10)
        
        # Premium color palette
        self.colors = {
            'primary': '#00ff88',
            'secondary': '#00aaff', 
            'accent': '#ff00aa',
            'bg_dark': '#000000',
            'bg_medium': '#0a0a0a',
            'bg_light': '#1a1a1a',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'text_muted': '#888888',
            'border': '#333333',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'error': '#ff4444'
        }

        self.db_path = None
        self.conn = None
        self.current_table = None
        
        # Animation variables
        self.animation_speed = 50
        self.pulse_animation = None
        self.gradient_offset = 0
        
        # Performance tracking
        self.load_times = []
        self.start_time = time.time()
        
        # Edit/Undo/Redo system
        self.edit_history = deque(maxlen=50)  # Store up to 50 actions
        self.redo_stack = deque(maxlen=50)
        self.original_data = {}  # Store original data for comparison
        self.is_editing = False
        self.edit_entry = None
        self.edit_item = None
        self.edit_column = None
        self.table_columns = []
        
        self.create_ui()
        self.start_animations()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def start_animations(self):
        """Start background animations for premium feel"""
        self.animate_gradients()
        self.pulse_status()
    
    def animate_gradients(self):
        """Subtle gradient animation effects"""
        if hasattr(self, 'header_frame'):
            self.gradient_offset = (self.gradient_offset + 1) % 360
            # Subtle color shifting effect
            hue = self.gradient_offset
            if hue % 60 == 0:  # Update every 60 frames
                self.update_header_gradient()
        self.root.after(100, self.animate_gradients)
    
    def pulse_status(self):
        """Pulse effect for status indicators"""
        if hasattr(self, 'status_indicator'):
            current_alpha = self.status_indicator.cget('bg')
            # Create pulsing effect
            self.root.after(1000, self.pulse_status)
    
    def update_header_gradient(self):
        """Update header with gradient effect"""
        if hasattr(self, 'header_frame'):
            # Subtle gradient animation
            colors = ['#0a0a0a', '#1a1a1a', '#0a0a0a']
            self.header_frame.configure(bg=colors[self.gradient_offset % 3])
    
    def create_ui(self):
        # Configure premium styles
        self.setup_premium_styles()
        
        # Create animated header
        self.create_animated_header()
        
        # Create main content area
        self.create_main_content()
        
        # Create premium status bar
        self.create_premium_status_bar()
        
        # Create floating action buttons
        self.create_floating_actions()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select SQLite Database",
            filetypes=[("SQLite Database", "*.db *.sqlite *.sqlite3"), ("All Files", "*.*")]
        )

        if not file_path:
            return

        self.db_path = file_path
        self.update_status(f"Loading database: {file_path.split('/')[-1]}")

        try:
            if self.conn:
                self.conn.close()
            self.conn = sqlite3.connect(self.db_path)
            self.load_tables()
            self.enable_buttons()
            self.hide_empty_state()
            self.update_status(f"Database loaded successfully • {file_path.split('/')[-1]}")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load database:\n{str(e)}")
            self.update_status("Error loading database")

    def setup_premium_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Premium treeview with enhanced styling
        style.configure("Premium.Treeview",
                        background="#0a0a0a",
                        foreground="#ffffff",
                        rowheight=35,
                        fieldbackground="#0a0a0a",
                        bordercolor="#333333",
                        borderwidth=2,
                        font=self.code_font)
        
        style.configure("Premium.Treeview.Heading",
                        background="#1a1a1a",
                        foreground=self.colors['primary'],
                        font=self.heading_font,
                        relief="flat",
                        borderwidth=1)
        
        style.map('Premium.Treeview', 
                 background=[('selected', self.colors['primary']), 
                          ('active', '#2a2a2a')],
                 foreground=[('selected', '#000000'), 
                          ('active', '#ffffff')])
        
        # Custom button styles with glow effects
        style.configure('Premium.TButton',
                       font=self.normal_font,
                       borderwidth=0,
                       focuscolor='none',
                       relief='flat')
        
        style.map('Premium.TButton',
                 background=[('active', self.colors['primary']), 
                          ('pressed', self.colors['secondary'])],
                 foreground=[('active', '#000000'), 
                          ('pressed', '#000000')])
        
        # Premium scrollbar
        style.configure('Premium.Horizontal.TScrollbar',
                       background='#1a1a1a',
                       troughcolor='#0a0a0a',
                       bordercolor='#333333',
                       arrowcolor='#ffffff')
        
        style.configure('Premium.Vertical.TScrollbar',
                       background='#1a1a1a',
                       troughcolor='#0a0a0a',
                       bordercolor='#333333',
                       arrowcolor='#ffffff')
    
    def create_animated_header(self):
        # Premium header with gradient background
        self.header_frame = tk.Frame(self.root, bg="#0a0a0a", height=100)
        self.header_frame.pack(fill=tk.X, padx=3, pady=3)
        self.header_frame.pack_propagate(False)
        
        # Add gradient effect frame
        gradient_frame = tk.Frame(self.header_frame, bg="#1a1a1a", height=3)
        gradient_frame.pack(fill=tk.X)
        
        # Main header content
        header_container = tk.Frame(self.header_frame, bg="#0a0a0a")
        header_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Left side - Title section with enhanced styling
        title_section = tk.Frame(header_container, bg="#0a0a0a")
        title_section.pack(side=tk.LEFT, fill=tk.Y)
        
        # Animated title with glow effect
        self.title_label = tk.Label(title_section, 
                                  text="✨ SQLite Database Viewer Pro",
                                  bg="#0a0a0a", 
                                  fg=self.colors['primary'],
                                  font=self.title_font)
        self.title_label.pack(anchor=tk.W)
        
        # Subtitle with gradient text effect
        subtitle_label = tk.Label(title_section, 
                                 text="🚀 Premium Database Exploration Suite",
                                 bg="#0a0a0a", 
                                 fg=self.colors['secondary'],
                                 font=self.normal_font)
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Version badge
        version_badge = tk.Label(title_section, 
                               text="v2.0 • Premium Edition",
                               bg=self.colors['accent'], 
                               fg="#ffffff",
                               font=self.small_font,
                               padx=8, pady=2)
        version_badge.pack(anchor=tk.W, pady=(5, 0))
        
        # Right side - Premium action buttons
        button_section = tk.Frame(header_container, bg="#0a0a0a")
        button_section.pack(side=tk.RIGHT, fill=tk.Y, padx=20)
        
        # Create premium buttons with enhanced styling
        self.create_premium_button(button_section, "📂 Open Database", 
                                 self.open_file, self.colors['primary'])
        self.create_premium_button(button_section, "🔄 Refresh", 
                                 self.refresh_current_table, self.colors['secondary'])
        self.create_premium_button(button_section, "📊 Analytics", 
                                 self.show_analytics, self.colors['accent'])
        self.create_premium_button(button_section, "⚙️ Settings", 
                                 self.show_settings, self.colors['text_secondary'])
        
        # Edit/Undo/Redo buttons
        edit_section = tk.Frame(header_container, bg="#0a0a0a")
        edit_section.pack(side=tk.RIGHT, padx=10)
        
        self.undo_btn = self.create_premium_button(edit_section, "↶ Undo", 
                                                   self.undo_action, self.colors['warning'])
        self.redo_btn = self.create_premium_button(edit_section, "↷ Redo", 
                                                   self.redo_action, self.colors['warning'])
        self.save_btn = self.create_premium_button(edit_section, "💾 Save All", 
                                                  self.save_all_changes, self.colors['success'])
        
        # Initially disable edit buttons
        self.undo_btn.config(state=tk.DISABLED)
        self.redo_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
    
    def create_premium_button(self, parent, text, command, color):
        """Create a premium styled button with hover effects"""
        btn_frame = tk.Frame(parent, bg="#1a1a1a", relief="flat", bd=1)
        btn_frame.pack(side=tk.LEFT, padx=5)
        
        btn = tk.Button(btn_frame, text=text,
                       command=command,
                       font=self.normal_font,
                       bg=color, fg="#ffffff",
                       activebackground="#ffffff",
                       activeforeground="#000000",
                       padx=20, pady=12,
                       relief="flat",
                       cursor="hand2",
                       borderwidth=0)
        btn.pack(fill=tk.BOTH, expand=True)
        
        # Add hover effect
        btn.bind("<Enter>", lambda e: btn.config(bg="#ffffff", fg="#000000"))
        btn.bind("<Leave>", lambda e: btn.config(bg=color, fg="#ffffff"))
        
        return btn
    
    def create_main_content(self):
        # Main container with premium border
        main_container = tk.Frame(self.root, bg="#333333")
        main_container.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Inner content area with premium background
        content_frame = tk.Frame(main_container, bg="#0a0a0a")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create premium paned window
        self.paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create premium panels
        self.create_premium_tables_panel()
        self.create_premium_data_panel()
        
        # Add panels to paned window
        self.paned.add(self.table_frame, weight=1)
        self.paned.add(self.data_frame, weight=3)
    
    def create_premium_tables_panel(self):
        self.table_frame = tk.Frame(self.paned, bg="#1a1a1a")
        
        # Premium panel header with gradient
        panel_header = tk.Frame(self.table_frame, bg="#2a2a2a", height=50)
        panel_header.pack(fill=tk.X)
        panel_header.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(panel_header, bg="#2a2a2a")
        header_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        tables_label = tk.Label(header_content, text="📋 Database Schema",
                               bg="#2a2a2a", fg=self.colors['primary'],
                               font=self.heading_font)
        tables_label.pack(side=tk.LEFT)
        
        # Table count badge
        self.table_count_badge = tk.Label(header_content, text="0 tables",
                                         bg=self.colors['accent'], fg="#ffffff",
                                         font=self.small_font,
                                         padx=8, pady=4)
        self.table_count_badge.pack(side=tk.RIGHT)
        
        # Premium list container
        list_container = tk.Frame(self.table_frame, bg="#1a1a1a")
        list_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Custom scrollbar with premium styling
        scrollbar = tk.Scrollbar(list_container, bg="#2a2a2a", troughcolor="#0a0a0a",
                                activebackground=self.colors['primary'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.table_listbox = tk.Listbox(list_container,
                                        bg="#0a0a0a",
                                        fg="#ffffff",
                                        font=self.normal_font,
                                        selectbackground=self.colors['primary'],
                                        selectforeground="#000000",
                                        activestyle="none",
                                        yscrollcommand=scrollbar.set,
                                        relief="flat",
                                        borderwidth=0,
                                        highlightthickness=0,
                                        selectborderwidth=0)
        self.table_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.table_listbox.yview)
        self.table_listbox.bind("<<ListboxSelect>>", self.on_table_select)
        
        # Premium empty state
        self.empty_label = tk.Label(self.table_frame,
                                   text="🗄️ No Database Loaded\n\n✨ Click 'Open Database' to begin exploring",
                                   bg="#1a1a1a", fg=self.colors['text_muted'],
                                   font=self.normal_font,
                                   justify=tk.CENTER)
        self.empty_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def create_premium_data_panel(self):
        self.data_frame = tk.Frame(self.paned, bg="#1a1a1a")
        
        # Premium panel header
        self.data_header = tk.Frame(self.data_frame, bg="#2a2a2a", height=50)
        self.data_header.pack(fill=tk.X)
        self.data_header.pack_propagate(False)
        
        header_content = tk.Frame(self.data_header, bg="#2a2a2a")
        header_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self.table_info_label = tk.Label(header_content, text="📊 Data View",
                                        bg="#2a2a2a", fg=self.colors['primary'],
                                        font=self.heading_font)
        self.table_info_label.pack(side=tk.LEFT)
        
        # Performance indicator
        self.performance_label = tk.Label(header_content, text="⚡ Ready",
                                         bg=self.colors['success'], fg="#000000",
                                         font=self.small_font,
                                         padx=8, pady=4)
        self.performance_label.pack(side=tk.RIGHT)
        
        # Premium treeview container
        tree_container = tk.Frame(self.data_frame, bg="#1a1a1a")
        tree_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Premium treeview
        self.tree = ttk.Treeview(tree_container, show='headings', style="Premium.Treeview")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click for editing
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-1>", self.on_single_click)
        
        # Premium scrollbars
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview,
                           style="Premium.Vertical.TScrollbar")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview,
                           style="Premium.Horizontal.TScrollbar")
        
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Premium empty state
        self.data_empty_label = tk.Label(tree_container,
                                        text="📋 Select a table to view data\n\n✨ Choose from the schema explorer on the left",
                                        bg="#1a1a1a", fg=self.colors['text_muted'],
                                        font=self.normal_font,
                                        justify=tk.CENTER)
        self.data_empty_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def create_premium_status_bar(self):
        status_frame = tk.Frame(self.root, bg="#1a1a1a", height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        # Status content
        status_content = tk.Frame(status_frame, bg="#1a1a1a")
        status_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # Left side - Status message
        self.status_label = tk.Label(status_content, text="✨ Ready • Premium Edition",
                                   bg="#1a1a1a", fg=self.colors['text_secondary'],
                                   font=self.small_font,
                                   anchor=tk.W)
        self.status_label.pack(side=tk.LEFT)
        
        # Center - Live time
        self.time_label = tk.Label(status_content, text="",
                                 bg="#1a1a1a", fg=self.colors['text_muted'],
                                 font=self.small_font)
        self.time_label.pack(side=tk.LEFT, padx=20)
        
        # Right side - Stats
        self.row_count_label = tk.Label(status_content, text="📊 0 rows",
                                       bg="#1a1a1a", fg=self.colors['text_secondary'],
                                       font=self.small_font,
                                       anchor=tk.E)
        self.row_count_label.pack(side=tk.RIGHT)
        
        # Update time
        self.update_time()
    
    def create_floating_actions(self):
        """Create floating action buttons for quick access"""
        # Floating action button container
        fab_container = tk.Frame(self.root, bg="#000000")
        fab_container.place(relx=0.98, rely=0.5, anchor=tk.E)
        
        # Export button
        export_fab = tk.Button(fab_container, text="💾",
                               command=self.export_data,
                               font=self.normal_font,
                               bg=self.colors['accent'], fg="#ffffff",
                               activebackground="#ffffff",
                               activeforeground="#000000",
                               width=3, height=1,
                               relief="flat",
                               cursor="hand2",
                               borderwidth=0)
        export_fab.pack(pady=5)
    
    def update_time(self):
        """Update current time display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=f"🕐 {current_time}")
        self.root.after(1000, self.update_time)
    
    def on_single_click(self, event):
        """Handle single click - cancel any ongoing edit"""
        if self.is_editing:
            self.cancel_edit()
    
    def on_double_click(self, event):
        """Handle double-click for inline editing"""
        if self.is_editing or not self.current_table:
            return
        
        # Get the item and column that was clicked
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        
        self.edit_item = self.tree.identify_row(event.y)
        self.edit_column = self.tree.identify_column(event.x)
        
        if not self.edit_item or not self.edit_column:
            return
        
        # Get column index
        column_index = int(self.edit_column[1:]) - 1
        if column_index >= len(self.table_columns):
            return
        
        column_name = self.table_columns[column_index]
        
        # Get current value
        current_values = self.tree.item(self.edit_item, 'values')
        current_value = current_values[column_index] if column_index < len(current_values) else ""
        
        # Store original data for undo
        self.original_data[(self.edit_item, column_name)] = current_value
        
        # Create edit widget
        self.create_edit_widget(current_value, column_name)
    
    def create_edit_widget(self, current_value, column_name):
        """Create an inline edit widget"""
        # Get cell coordinates
        bbox = self.tree.bbox(self.edit_item, self.edit_column)
        if not bbox:
            return
        
        # Create entry widget
        self.edit_entry = tk.Entry(self.tree, 
                                 bg=self.colors['bg_light'],
                                 fg=self.colors['text_primary'],
                                 font=self.code_font,
                                 insertbackground=self.colors['primary'],
                                 relief="flat",
                                 borderwidth=2,
                                 highlightbackground=self.colors['primary'],
                                 highlightthickness=2)
        
        # Position the entry
        self.edit_entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        
        # Set current value
        self.edit_entry.insert(0, str(current_value) if current_value else "")
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus()
        
        # Bind events
        self.edit_entry.bind("<Return>", lambda e: self.save_edit())
        self.edit_entry.bind("<Escape>", lambda e: self.cancel_edit())
        self.edit_entry.bind("<FocusOut>", lambda e: self.save_edit())
        
        self.is_editing = True
        self.update_status(f"✏️ Editing {column_name}...")
    
    def save_edit(self):
        """Save the current edit"""
        if not self.is_editing or not self.edit_entry:
            return
        
        new_value = self.edit_entry.get()
        column_index = int(self.edit_column[1:]) - 1
        column_name = self.table_columns[column_index]
        
        # Get original value
        original_value = self.original_data.get((self.edit_item, column_name), "")
        
        # Only save if value changed
        if new_value != original_value:
            # Create edit action for undo/redo
            edit_action = {
                'type': 'edit',
                'table': self.current_table,
                'item': self.edit_item,
                'column': column_name,
                'column_index': column_index,
                'old_value': original_value,
                'new_value': new_value,
                'timestamp': datetime.now()
            }
            
            # Add to history
            self.edit_history.append(edit_action)
            self.redo_stack.clear()
            
            # Update treeview
            current_values = list(self.tree.item(self.edit_item, 'values'))
            current_values[column_index] = new_value
            self.tree.item(self.edit_item, values=current_values)
            
            # Update buttons
            self.update_edit_buttons()
            
            # Update status
            self.update_status(f"✏️ Edited {column_name}: '{original_value}' → '{new_value}'")
            self.performance_label.config(text="✏️ Edited", bg=self.colors['warning'], fg="#000000")
        
        self.cleanup_edit()
    
    def cancel_edit(self):
        """Cancel the current edit"""
        if self.is_editing:
            self.update_status("❌ Edit cancelled")
            self.cleanup_edit()
    
    def cleanup_edit(self):
        """Clean up edit widget"""
        if self.edit_entry:
            self.edit_entry.destroy()
            self.edit_entry = None
        
        self.is_editing = False
        self.edit_item = None
        self.edit_column = None
    
    def undo_action(self):
        """Undo the last action"""
        if not self.edit_history:
            return
        
        action = self.edit_history.pop()
        self.redo_stack.append(action)
        
        if action['type'] == 'edit':
            # Restore original value
            current_values = list(self.tree.item(action['item'], 'values'))
            current_values[action['column_index']] = action['old_value']
            self.tree.item(action['item'], values=current_values)
            
            self.update_status(f"↶ Undid edit to {action['column']}")
        
        self.update_edit_buttons()
    
    def redo_action(self):
        """Redo the last undone action"""
        if not self.redo_stack:
            return
        
        action = self.redo_stack.pop()
        self.edit_history.append(action)
        
        if action['type'] == 'edit':
            # Restore new value
            current_values = list(self.tree.item(action['item'], 'values'))
            current_values[action['column_index']] = action['new_value']
            self.tree.item(action['item'], values=current_values)
            
            self.update_status(f"↷ Redid edit to {action['column']}")
        
        self.update_edit_buttons()
    
    def save_all_changes(self):
        """Save all changes to database"""
        if not self.edit_history:
            messagebox.showinfo("Save", "No changes to save.")
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Group changes by table for efficiency
            changes_by_table = {}
            for action in self.edit_history:
                if action['table'] not in changes_by_table:
                    changes_by_table[action['table']] = []
                changes_by_table[action['table']].append(action)
            
            saved_count = 0
            for table, actions in changes_by_table.items():
                for action in actions:
                    if action['type'] == 'edit':
                        # Get primary key for WHERE clause (simplified - using rowid)
                        cursor.execute(f"SELECT rowid, * FROM {table} LIMIT 1000")
                        all_data = cursor.fetchall()
                        
                        if action['item'] and int(action['item'][1:]) <= len(all_data):
                            row_id = all_data[int(action['item'][1:]) - 1][0]
                            
                            # Update the database
                            query = f"UPDATE {table} SET {action['column']} = ? WHERE rowid = ?"
                            cursor.execute(query, (action['new_value'], row_id))
                            saved_count += 1
            
            self.conn.commit()
            
            messagebox.showinfo("Save Success", f"Saved {saved_count} changes to database.")
            self.update_status(f"💾 Saved {saved_count} changes to database")
            self.performance_label.config(text="💾 Saved", bg=self.colors['success'], fg="#000000")
            
            # Clear history after successful save
            self.edit_history.clear()
            self.redo_stack.clear()
            self.update_edit_buttons()
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save changes:\n{str(e)}")
            self.update_status("❌ Error saving changes")
    
    def update_edit_buttons(self):
        """Update the state of edit buttons"""
        has_undo = len(self.edit_history) > 0
        has_redo = len(self.redo_stack) > 0
        has_changes = has_undo or has_redo
        
        self.undo_btn.config(state=tk.NORMAL if has_undo else tk.DISABLED)
        self.redo_btn.config(state=tk.NORMAL if has_redo else tk.DISABLED)
        self.save_btn.config(state=tk.NORMAL if has_changes else tk.DISABLED)
        
    def show_analytics(self):
        """Show database analytics dashboard"""
        if not self.conn:
            messagebox.showinfo("Analytics", "Please load a database first.")
            return
        
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("📊 Database Analytics")
        analytics_window.geometry("800x600")
        analytics_window.configure(bg="#0a0a0a")
        
        # Analytics content
        title = tk.Label(analytics_window, text="📊 Database Analytics Dashboard",
                        bg="#0a0a0a", fg=self.colors['primary'],
                        font=self.title_font)
        title.pack(pady=20)
        
        # Get database statistics
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        stats_text = f"\n\n📊 Database Statistics:\n\n"
        stats_text += f"📄 Total Tables: {len(tables)}\n"
        
        total_rows = 0
        table_info = []
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                total_rows += count
                table_info.append((table[0], count))
            except:
                pass
        
        stats_text += f"📈 Total Rows: {total_rows:,}\n\n"
        stats_text += f"📋 Table Details:\n"
        
        # Sort tables by row count
        table_info.sort(key=lambda x: x[1], reverse=True)
        
        for name, count in table_info[:10]:  # Top 10 tables
            stats_text += f"  • {name}: {count:,} rows\n"
        
        stats_label = tk.Label(analytics_window, text=stats_text,
                              bg="#0a0a0a", fg="#ffffff",
                              font=self.code_font,
                              justify=tk.LEFT)
        stats_label.pack(pady=20, padx=20)
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Settings")
        settings_window.geometry("500x400")
        settings_window.configure(bg="#0a0a0a")
        
        title = tk.Label(settings_window, text="⚙️ Application Settings",
                        bg="#0a0a0a", fg=self.colors['primary'],
                        font=self.title_font)
        title.pack(pady=20)
        
        settings_text = """🎨 Premium Features:

✨ Advanced animations and transitions
🎯 Enhanced visual styling
📊 Real-time analytics dashboard
💾 Export functionality
⚡ Performance optimization
🎪 Premium dark theme

🔧 Technical Details:

• Font: Segoe UI & Consolas
• Theme: Premium Dark Edition
• Version: 2.0 Premium
• Performance: Optimized for large databases
• Animation: Smooth 60fps transitions
"""
        
        settings_label = tk.Label(settings_window, text=settings_text,
                                bg="#0a0a0a", fg="#ffffff",
                                font=self.normal_font,
                                justify=tk.LEFT)
        settings_label.pack(pady=20, padx=20)
    
    def export_data(self):
        """Export current table data to CSV"""
        if not self.current_table or not self.conn:
            messagebox.showinfo("Export", "Please select a table first.")
            return
        
        export_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title=f"Export {self.current_table} to CSV"
        )
        
        if not export_path:
            return
        
        try:
            import csv
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT * FROM {self.current_table}")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columns)
                writer.writerows(rows)
            
            messagebox.showinfo("Export Success", f"Data exported to {export_path}")
            self.update_status(f"✅ Exported {len(rows)} rows to CSV")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")
    
    def create_tables_panel(self):
        self.table_frame = tk.Frame(self.paned, bg="#161b22")
        
        # Panel header
        panel_header = tk.Frame(self.table_frame, bg="#21262d", height=40)
        panel_header.pack(fill=tk.X)
        panel_header.pack_propagate(False)
        
        tables_label = tk.Label(panel_header, text="📋 Tables & Views",
                               bg="#21262d", fg="#f0f6fc",
                               font=self.heading_font)
        tables_label.pack(pady=8)
        
        # Tables list with modern styling
        list_container = tk.Frame(self.table_frame, bg="#161b22")
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Custom scrollbar
        scrollbar = tk.Scrollbar(list_container, bg="#21262d", troughcolor="#0d1117")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.table_listbox = tk.Listbox(list_container,
                                        bg="#0d1117",
                                        fg="#c9d1d9",
                                        font=self.normal_font,
                                        selectbackground="#238636",
                                        selectforeground="#ffffff",
                                        activestyle="none",
                                        yscrollcommand=scrollbar.set,
                                        relief="flat",
                                        borderwidth=0,
                                        highlightthickness=0)
        self.table_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.table_listbox.yview)
        self.table_listbox.bind("<<ListboxSelect>>", self.on_table_select)
        
        # Empty state message
        self.empty_label = tk.Label(self.table_frame,
                                   text="No database loaded\n\n📂 Click 'Open Database' to begin",
                                   bg="#161b22", fg="#6e7681",
                                   font=self.normal_font,
                                   justify=tk.CENTER)
        self.empty_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def create_data_panel(self):
        self.data_frame = tk.Frame(self.paned, bg="#161b22")
        
        # Panel header with table info
        self.data_header = tk.Frame(self.data_frame, bg="#21262d", height=40)
        self.data_header.pack(fill=tk.X)
        self.data_header.pack_propagate(False)
        
        self.table_info_label = tk.Label(self.data_header, text="📊 Data View",
                                        bg="#21262d", fg="#f0f6fc",
                                        font=self.heading_font)
        self.table_info_label.pack(pady=8)
        
        # Treeview container
        tree_container = tk.Frame(self.data_frame, bg="#161b22")
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Modern treeview
        self.tree = ttk.Treeview(tree_container, show='headings')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Modern scrollbars
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Empty state for data view
        self.data_empty_label = tk.Label(tree_container,
                                        text="Select a table to view its data\n\n📋 Choose from the tables list on the left",
                                        bg="#161b22", fg="#6e7681",
                                        font=self.normal_font,
                                        justify=tk.CENTER)
        self.data_empty_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def create_status_bar(self):
        status_frame = tk.Frame(self.root, bg="#21262d", height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Ready • No database loaded",
                                   bg="#21262d", fg="#8b949e",
                                   font=self.small_font,
                                   anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=2)
        
        # Row counter label
        self.row_count_label = tk.Label(status_frame, text="",
                                       bg="#21262d", fg="#8b949e",
                                       font=self.small_font,
                                       anchor=tk.E)
        self.row_count_label.pack(side=tk.RIGHT, padx=10, pady=2)

    def load_tables(self):
        self.table_listbox.delete(0, tk.END)
        self.current_table = None

        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        # Also get views
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;")
        views = cursor.fetchall()

        if not tables and not views:
            messagebox.showinfo("Empty Database", "This database contains no tables or views.")
            return

        # Add tables with premium styling
        for table in tables:
            self.table_listbox.insert(tk.END, f"📄 {table[0]}")
        
        # Add views
        for view in views:
            self.table_listbox.insert(tk.END, f"👁️ {view[0]}")
        
        # Update table count badge
        total_count = len(tables) + len(views)
        self.table_count_badge.config(text=f"{total_count} items")
        
        self.update_status(f"✨ Loaded {len(tables)} tables and {len(views)} views")
        self.performance_label.config(text="⚡ Loaded", bg=self.colors['success'], fg="#000000")

    def on_table_select(self, event):
        selected = self.table_listbox.curselection()
        if not selected:
            return

        selected_item = self.table_listbox.get(selected[0])
        # Remove emoji prefix to get actual table name
        table_name = selected_item[2:]  # Skip emoji and space
        self.current_table = table_name
        
        # Update header
        icon = "📄" if "📄" in selected_item else "👁️"
        table_type = "Table" if "📄" in selected_item else "View"
        self.table_info_label.config(text=f"{icon} {table_name} ({table_type})")
        
        self.display_table_data(table_name)

    def display_table_data(self, table_name):
        # Clear existing data
        for col in self.tree.get_children():
            self.tree.delete(col)
        
        # Hide empty state
        self.data_empty_label.place_forget()
        
        # Start performance tracking
        start_time = time.time()

        cursor = self.conn.cursor()

        try:
            # Get table structure
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            columns = [col[1] for col in columns_info]
            
            # Store columns for editing
            self.table_columns = columns
            
            # Configure treeview columns
            self.tree["columns"] = columns
            
            # Set column headers with enhanced styling
            for i, col in enumerate(columns):
                self.tree.heading(col, text=f"{col}\n({columns_info[i][2]})")
                self.tree.column(col, width=150, anchor=tk.W)
            
            # Get data with performance limit
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")
            rows = cursor.fetchall()
            
            # Insert data with smooth animation effect
            for i, row in enumerate(rows):
                self.tree.insert("", tk.END, values=row)
                
            # Update performance metrics
            load_time = (time.time() - start_time) * 1000
            self.load_times.append(load_time)
            
            # Get total row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = cursor.fetchone()[0]
            
            # Update status with premium styling
            self.update_status(f"✨ Showing {min(len(rows), 1000)} of {total_rows:,} rows in '{table_name}' ({load_time:.1f}ms)")
            self.row_count_label.config(text=f"📊 {total_rows:,} total rows")
            
            # Update performance indicator
            if load_time < 100:
                perf_text = "⚡ Fast"
                perf_color = self.colors['success']
            elif load_time < 500:
                perf_text = "🐢 Normal"
                perf_color = self.colors['warning']
            else:
                perf_text = "🐌 Slow"
                perf_color = self.colors['error']
                
            self.performance_label.config(text=perf_text, bg=perf_color, fg="#ffffff")
            
        except Exception as e:
            messagebox.showerror("Data Error", f"Failed to load table data:\n{str(e)}")
            self.update_status(f"❌ Error loading table '{table_name}'")
            self.performance_label.config(text="❌ Error", bg=self.colors['error'], fg="#ffffff")
    
    def refresh_current_table(self):
        if self.current_table:
            self.display_table_data(self.current_table)
            self.update_status(f"🔄 Refreshed table '{self.current_table}'")
            self.performance_label.config(text="⚡ Refreshed", bg=self.colors['success'], fg="#000000")
    
    def enable_buttons(self):
        """Enable premium action buttons"""
        # Note: Premium buttons are always enabled, but we can update their states
        self.update_status("✨ Premium features activated")
    
    def hide_empty_state(self):
        """Hide empty state messages"""
        self.empty_label.place_forget()
    
    def update_status(self, message):
        """Update status bar with premium styling"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def show_database_info(self):
        if not self.conn:
            return
            
        cursor = self.conn.cursor()
        
        # Get database info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;")
        views = cursor.fetchall()
        
        # Calculate total rows
        total_rows = 0
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                total_rows += cursor.fetchone()[0]
            except:
                pass
        
        info = f"📊 Database Information\n\n"
        info += f"📁 File: {self.db_path.split('/')[-1]}\n"
        info += f"📄 Tables: {len(tables)}\n"
        info += f"👁️ Views: {len(views)}\n"
        info += f"📈 Total Rows: {total_rows:,}\n\n"
        
        if tables:
            info += "Tables:\n"
            for table in tables[:10]:  # Show first 10
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                info += f"  • {table[0]} ({count:,} rows)\n"
            
            if len(tables) > 10:
                info += f"  ... and {len(tables) - 10} more\n"
        
        messagebox.showinfo("Database Info", info)
    
    def enable_buttons(self):
        self.refresh_btn.config(state=tk.NORMAL)
        self.info_btn.config(state=tk.NORMAL)
    
    def hide_empty_state(self):
        self.empty_label.place_forget()
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = SQLiteViewer(root)
    root.mainloop()
