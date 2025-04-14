import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
import os
from typing import Dict, Set, Optional
import configparser

class MarkdownNoteApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.config_file = "notes_config.ini"
        self.default_extension = ".md"
        self.pinned_notes: Set[str] = set()
        self.dark_mode = False
        self.current_note = None
        self.notes: Dict[str, str] = {}
        
        # Load configuration
        self.config = configparser.ConfigParser()
        self.load_config()
        
        self.setup_ui()
        self.load_notes()
        self.update_list()
    
    def load_config(self) -> None:
        """Load or create configuration file."""
        self.config.read(self.config_file)
        
        if not self.config.has_section('Settings'):
            self.config.add_section('Settings')
            self.config.set('Settings', 'notes_path', os.getcwd())
            self.save_config()
        
        self.notes_path = self.config.get('Settings', 'notes_path', fallback=os.getcwd())

    def save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def set_notes_path(self) -> None:
        """Set a new path for saving notes."""
        new_path = filedialog.askdirectory(initialdir=self.notes_path)
        if new_path:
            self.notes_path = new_path
            self.config.set('Settings', 'notes_path', new_path)
            self.save_config()
            self.load_notes()
            self.update_list()

    def get_note_path(self, title: str) -> str:
        """Get full path for a note file."""
        return os.path.join(self.notes_path, f"{title}{self.default_extension}")

    def load_notes(self) -> None:
        """Load notes from markdown files in the notes directory."""
        self.notes = {}
        self.pinned_notes = set()
        
        try:
            if not os.path.exists(self.notes_path):
                os.makedirs(self.notes_path)
                
            for filename in os.listdir(self.notes_path):
                if filename.endswith(self.default_extension):
                    title = filename[:-len(self.default_extension)]
                    try:
                        with open(os.path.join(self.notes_path, filename), 'r', encoding='utf-8') as file:
                            content = file.read()
                            self.notes[title] = content
                            
                            # Check if this is a pinned note (first line contains #pinned)
                            if content.startswith("#pinned\n"):
                                self.pinned_notes.add(title)
                    except (IOError, UnicodeDecodeError) as e:
                        print(f"Error loading note {filename}: {e}")
        except OSError as e:
            messagebox.showerror("Error", f"Failed to access notes directory: {e}")

    def save_note_to_file(self, title: str, content: str) -> bool:
        """Save a single note to file."""
        try:
            with open(self.get_note_path(title), 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save note: {e}")
            return False

    def add_note(self) -> None:
        """Add a new note."""
        title = simpledialog.askstring("New Note", "Enter note title:")
        if not title:
            return
            
        # Remove invalid characters from filename
        safe_title = "".join(c for c in title if c not in '\\/:*?"<>|')
        if safe_title != title:
            messagebox.showwarning("Warning", "Removed invalid characters from note title")
            
        if safe_title in self.notes:
            messagebox.showerror("Error", "Note with this title already exists!")
            return
            
        self.notes[safe_title] = ""
        if self.save_note_to_file(safe_title, ""):
            self.update_list()
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(tk.END)
            self.load_selected_note()

    def delete_note(self) -> None:
        """Delete the selected note."""
        selected = self.listbox.curselection()
        if not selected:
            return
            
        title = self.listbox.get(selected[0])
        if not messagebox.askyesno("Delete", f"Delete '{title}'?"):
            return
            
        try:
            os.remove(self.get_note_path(title))
            if title in self.pinned_notes:
                self.pinned_notes.remove(title)
            del self.notes[title]
            self.update_list()
            self.text_area.delete("1.0", tk.END)
            self.current_note = None
            self.save_button.config(state=tk.DISABLED)
        except OSError as e:
            messagebox.showerror("Error", f"Failed to delete note: {e}")

    def update_list(self, filter_text: str = "") -> None:
        """Update the notes list with optional filtering."""
        self.listbox.delete(0, tk.END)
        
        # Sort notes with pinned notes first, then alphabetically
        sorted_notes = sorted(
            self.notes.keys(),
            key=lambda x: (x not in self.pinned_notes, x.lower())
        
        for title in sorted_notes:
            if filter_text.lower() in title.lower():
                self.listbox.insert(tk.END, title)
                if title in self.pinned_notes:
                    self.listbox.itemconfig(tk.END, {'fg': 'blue'})

    def load_selected_note(self) -> None:
        """Load the selected note into the text area."""
        selected = self.listbox.curselection()
        if not selected:
            return
            
        title = self.listbox.get(selected[0])
        self.current_note = title
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, self.notes[title])
        self.save_button.config(state=tk.NORMAL)

    def save_note(self) -> None:
        """Save the current note."""
        if not self.current_note:
            return
            
        content = self.text_area.get("1.0", tk.END).strip()
        self.notes[self.current_note] = content
        
        if self.save_note_to_file(self.current_note, content):
            # Update pinned status based on content
            if content.startswith("#pinned\n"):
                self.pinned_notes.add(self.current_note)
            elif self.current_note in self.pinned_notes:
                self.pinned_notes.remove(self.current_note)
            
            self.update_list()

    def toggle_dark_mode(self) -> None:
        """Toggle between dark and light mode."""
        self.dark_mode = not self.dark_mode
        bg_color = "#2E2E2E" if self.dark_mode else "#F5F5F5"
        fg_color = "#FFFFFF" if self.dark_mode else "#000000"
        highlight_color = "#3B3B3B" if self.dark_mode else "#E0E0E0"
        
        widgets = [
            self.text_area, self.listbox, self.search_entry, 
            self.root, self.button_frame, self.status_bar
        ]
        
        for widget in widgets:
            if widget in [self.text_area, self.listbox, self.search_entry]:
                widget.config(bg=highlight_color, fg=fg_color)
                if hasattr(widget, 'insertbackground'):
                    widget.config(insertbackground=fg_color)
            else:
                widget.config(bg=bg_color)
        
        # Update listbox selection colors
        self.listbox.config(
            selectbackground="#007BFF" if not self.dark_mode else "#005BBA",
            selectforeground="#FFF"
        )
        
        # Update status bar colors
        self.status_bar.config(
            bg=bg_color,
            fg=fg_color
        )

    def search_notes(self) -> None:
        """Filter notes based on search query."""
        query = self.search_entry.get()
        self.update_list(query)

    def toggle_pin(self) -> None:
        """Toggle pin status of selected note."""
        selected = self.listbox.curselection()
        if not selected:
            return
            
        title = self.listbox.get(selected[0])
        if title in self.pinned_notes:
            self.pinned_notes.remove(title)
            # Remove #pinned tag if it exists
            if self.notes[title].startswith("#pinned\n"):
                self.notes[title] = self.notes[title][8:]
        else:
            self.pinned_notes.add(title)
            # Add #pinned tag if not present
            if not self.notes[title].startswith("#pinned\n"):
                self.notes[title] = f"#pinned\n{self.notes[title]}"
        
        self.save_note_to_file(title, self.notes[title])
        self.update_list()

    def setup_ui(self) -> None:
        """Initialize the user interface."""
        self.root.title("Markdown Note-Taking App")
        self.root.geometry("900x650")
        self.root.configure(bg="#F5F5F5")
        
        # Configure grid weights for resizing
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.create_menu()
        self.create_widgets()
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self.save_note())
        self.root.bind('<Control-n>', lambda e: self.add_note())
        self.root.bind('<Control-o>', lambda e: self.set_notes_path())

    def create_menu(self) -> None:
        """Create the menu bar."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Note", command=self.add_note, accelerator="Ctrl+N")
        file_menu.add_command(label="Save Note", command=self.save_note, accelerator="Ctrl+S")
        file_menu.add_command(label="Set Notes Location", command=self.set_notes_path, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Delete Note", command=self.delete_note)
        edit_menu.add_command(label="Pin/Unpin Note", command=self.toggle_pin)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        # View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

    def create_widgets(self) -> None:
        """Create and arrange all widgets."""
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text=f"Notes location: {self.notes_path}",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=3, column=0, sticky="ew")
        
        # Search frame
        search_frame = ttk.Frame(self.root, padding=10)
        search_frame.grid(row=0, column=0, sticky="ew")
        
        self.search_entry = ttk.Entry(search_frame, width=60)
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_notes())
        
        search_button = ttk.Button(search_frame, text="Search", command=self.search_notes)
        search_button.pack(side=tk.RIGHT, padx=5)
        
        # Main content frame
        content_frame = ttk.Frame(self.root)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Notes list with scrollbar
        list_frame = ttk.Frame(content_frame)
        list_frame.grid(row=0, column=0, sticky="ns", padx=(0, 5))
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(
            list_frame,
            width=30,
            height=25,
            bg="#F5F5F5",
            fg="#000",
            selectbackground="#007BFF",
            selectforeground="#FFF",
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", lambda e: self.load_selected_note())
        
        # Text area with scrollbar
        text_frame = ttk.Frame(content_frame)
        text_frame.grid(row=0, column=1, sticky="nsew")
        
        text_scrollbar = ttk.Scrollbar(text_frame)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_area = tk.Text(
            text_frame,
            wrap=tk.WORD,
            bg="#F5F5F5",
            fg="#000",
            insertbackground="#000",
            font=("Consolas", 12),  # Monospaced font better for markdown
            yscrollcommand=text_scrollbar.set
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        text_scrollbar.config(command=self.text_area.yview)
        
        # Button frame
        self.button_frame = ttk.Frame(self.root, padding=10)
        self.button_frame.grid(row=2, column=0, sticky="ew")
        
        buttons = [
            ("Add Note", self.add_note),
            ("Delete Note", self.delete_note),
            ("Save Note", self.save_note),
            ("Dark Mode", self.toggle_dark_mode),
            ("Pin Note", self.toggle_pin),
            ("Set Location", self.set_notes_path)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(self.button_frame, text=text, command=command)
            btn.grid(row=0, column=i, padx=5, sticky="ew")
            if text == "Save Note":
                self.save_button = btn
                self.save_button.config(state=tk.DISABLED)
        
        # Configure column weights for button frame
        for i in range(len(buttons)):
            self.button_frame.grid_columnconfigure(i, weight=1)

    def show_about(self) -> None:
        """Show about dialog."""
        about_text = (
            "Markdown Note-Taking App\n"
            "Version 2.0\n\n"
            "Features:\n"
            "- Notes saved as Markdown (.md) files\n"
            "- Customizable storage location\n"
            "- Pinned notes support\n"
            "- Dark/light mode\n"
            "- Search functionality\n\n"
            "Keyboard Shortcuts:\n"
            "Ctrl+N: New note\n"
            "Ctrl+S: Save note\n"
            "Ctrl+O: Set notes location"
        )
        messagebox.showinfo("About", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownNoteApp(root)
    root.mainloop()
