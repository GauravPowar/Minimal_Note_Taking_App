import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import os
from typing import Dict, Set

class NoteApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.notes_file = "notes.json"
        self.notes: Dict[str, str] = self.load_notes()
        self.pinned_notes: Set[str] = set()
        self.dark_mode = False
        self.current_note = None
        
        self.setup_ui()
        self.update_list()
    
    def load_notes(self) -> Dict[str, str]:
        """Load notes from JSON file."""
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, "r") as file:
                    return json.load(file)
            except (json.JSONDecodeError, IOError):
                messagebox.showerror("Error", "Failed to load notes file")
        return {}

    def save_notes(self) -> None:
        """Save notes to JSON file."""
        try:
            with open(self.notes_file, "w") as file:
                json.dump(self.notes, file, indent=4)
        except IOError:
            messagebox.showerror("Error", "Failed to save notes")

    def add_note(self) -> None:
        """Add a new note."""
        title = simpledialog.askstring("New Note", "Enter note title:")
        if not title:
            return
            
        if title in self.notes:
            messagebox.showerror("Error", "Note with this title already exists!")
            return
            
        self.notes[title] = ""
        self.update_list()
        self.save_notes()
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
            
        if title in self.pinned_notes:
            self.pinned_notes.remove(title)
            
        del self.notes[title]
        self.update_list()
        self.text_area.delete("1.0", tk.END)
        self.save_notes()
        self.current_note = None
        self.save_button.config(state=tk.DISABLED)

    def update_list(self, filter_text: str = "") -> None:
        """Update the notes list with optional filtering."""
        self.listbox.delete(0, tk.END)
        
        # Sort notes with pinned notes first, then alphabetically
        sorted_notes = sorted(
            self.notes.keys(),
            key=lambda x: (x not in self.pinned_notes, x.lower())
        )
        
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
            
        self.notes[self.current_note] = self.text_area.get("1.0", tk.END).strip()
        self.save_notes()

    def toggle_dark_mode(self) -> None:
        """Toggle between dark and light mode."""
        self.dark_mode = not self.dark_mode
        bg_color = "#2E2E2E" if self.dark_mode else "#F5F5F5"
        fg_color = "#FFFFFF" if self.dark_mode else "#000000"
        highlight_color = "#3B3B3B" if self.dark_mode else "#E0E0E0"
        
        widgets = [
            self.text_area, self.listbox, self.search_entry, 
            self.root, self.button_frame
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
        else:
            self.pinned_notes.add(title)
        self.update_list()
        self.save_notes()

    def setup_ui(self) -> None:
        """Initialize the user interface."""
        self.root.title("Optimized Note-Taking App")
        self.root.geometry("800x600")
        self.root.configure(bg="#F5F5F5")
        
        # Configure grid weights for resizing
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.create_menu()
        self.create_widgets()
        
        # Bind Ctrl+S for saving
        self.root.bind('<Control-s>', lambda e: self.save_note())

    def create_menu(self) -> None:
        """Create the menu bar."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Note", command=self.add_note, accelerator="Ctrl+N")
        file_menu.add_command(label="Save Note", command=self.save_note, accelerator="Ctrl+S")
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
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.add_note())
        self.root.bind('<Control-N>', lambda e: self.add_note())

    def create_widgets(self) -> None:
        """Create and arrange all widgets."""
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
            height=20,
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
            font=("Arial", 12),
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
            ("Pin Note", self.toggle_pin)
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
            "Optimized Note-Taking App v2.0\n"
            "Created with Python and Tkinter\n"
            "Features:\n"
            "- Pinned notes\n"
            "- Dark mode\n"
            "- Keyboard shortcuts\n"
            "- Responsive layout"
        )
        messagebox.showinfo("About", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = NoteApp(root)
    root.mainloop()
