import os
import tkinter as tk
from tkinter import filedialog, messagebox
from src.tournament import PhotoTournament

def main():
    try:
        root = tk.Tk()
        root.withdraw()
        folder = filedialog.askdirectory(title="Select Folder with Photos")
        root.deiconify()
        if not folder:
            messagebox.showerror("Error", "No folder selected. Exiting program.")
            root.destroy()
        else:
            valid_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp")
            photo_paths = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(valid_extensions)]
            app = PhotoTournament(root, photo_paths)
            root.mainloop()
    except Exception as e:
        messagebox.showerror("Startup Error", f"An error occurred at startup:\n{e}")

if __name__ == "__main__":
    main()