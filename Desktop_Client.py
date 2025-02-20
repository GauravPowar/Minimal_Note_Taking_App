import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

# File to store notes
NOTES_FILE = "notes.json"

def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as file:
            return json.load(file)
    return {}

def save_notes():
    with open(NOTES_FILE, "w") as file:
        json.dump(notes, file, indent=4)

def add_note():
    title = simpledialog.askstring("New Note", "Enter note title:")
    if title and title not in notes:
        notes[title] = ""
        update_list()
        save_notes()
    elif title in notes:
        messagebox.showerror("Error", "Note with this title already exists!")

def delete_note():
    selected = listbox.curselection()
    if selected:
        title = listbox.get(selected[0])
        if messagebox.askyesno("Delete", f"Delete '{title}'?"):
            del notes[title]
            update_list()
            text_area.delete("1.0", tk.END)
            save_notes()

def update_list():
    listbox.delete(0, tk.END)
    for title in notes.keys():
        listbox.insert(tk.END, title)

def load_selected_note():
    selected = listbox.curselection()
    if selected:
        title = listbox.get(selected[0])
        text_area.delete("1.0", tk.END)
        text_area.insert(tk.END, notes[title])
        save_button.config(state=tk.NORMAL)

def save_note():
    selected = listbox.curselection()
    if selected:
        title = listbox.get(selected[0])
        notes[title] = text_area.get("1.0", tk.END).strip()
        save_notes()
        messagebox.showinfo("Saved", "Note saved successfully!")

def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    bg_color = "#2E2E2E" if dark_mode else "#F5F5F5"
    fg_color = "#FFFFFF" if dark_mode else "#000000"
    button_color = "#444" if dark_mode else "#DDD"
    
    root.config(bg=bg_color)
    text_area.config(bg=bg_color, fg=fg_color, insertbackground=fg_color)
    listbox.config(bg=bg_color, fg=fg_color)
    for button in button_frame.winfo_children():
        button.config(bg=button_color, fg=fg_color, relief=tk.FLAT)

dark_mode = False
notes = load_notes()

# UI Setup
root = tk.Tk()
root.title("Minimalist Note-Taking App")
root.geometry("550x450")
root.config(bg="#F5F5F5")

frame = tk.Frame(root, bg=root['bg'])
frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

listbox = tk.Listbox(frame, width=30, height=10, bg=root['bg'], fg="#000", selectbackground="#007BFF", selectforeground="#FFF")
listbox.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)
listbox.bind("<<ListboxSelect>>", lambda e: load_selected_note())

text_area = tk.Text(root, wrap=tk.WORD, height=10, bg="#F5F5F5", fg="#000", insertbackground="#000")
text_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

button_frame = tk.Frame(root, bg=root['bg'])
button_frame.pack(pady=5)

tk.Button(button_frame, text="Add Note", command=add_note, bg="#DDD", fg="#000", width=10).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Delete Note", command=delete_note, bg="#DDD", fg="#000", width=10).grid(row=0, column=1, padx=5)
save_button = tk.Button(button_frame, text="Save Note", command=save_note, bg="#DDD", fg="#000", width=10, state=tk.DISABLED)
save_button.grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="Dark Mode", command=toggle_dark_mode, bg="#444", fg="#FFF", width=10).grid(row=0, column=3, padx=5)

update_list()
root.mainloop()



