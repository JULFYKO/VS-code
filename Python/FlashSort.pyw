#  _____ _           _     ____             _   
# |  ___| | __ _ ___| |__ / ___|  ___  _ __| |_ 
# | |_  | |/ _` / __| '_ \\___ \ / _ \| '__| __|
# |  _| | | (_| \__ \ | | |___) | (_) | |  | |_ 
# |_|   |_|\__,_|___/_| |_|____/ \___/|_|   \__|
# -----------------------------------------------------------------------------
# FlashSort Media Organizer
#
# This program is a desktop application for quickly sorting, viewing, and organizing
# media files (images, videos, audio) within a selected folder. It features a modern
# VS Code–style interface with both keyboard shortcuts and mouse controls.
#
# Main features:
# - Move files to category folders using hotkeys (A, S, D, F, J, K, L, ;)
# - Preview images and videos directly in the app
# - Open files and folders in the system file manager
# - Undo the last file move
# - Analyze and report duplicate files
# - Group similar images using perceptual hashing
# - Apply filters and generate reports about folder contents
# - All main functions are available via toolbar buttons and keyboard shortcuts
#
# Author: JulfyKo
# -----------------------------------------------------------------------------
# Program Structure Overview (for quick navigation)
#
# - FlashSortMediaOrganizer class:
#     - __init__                  : Main initialization
#     - load_config               : Load configuration from file
#     - save_config               : Save configuration to file
#     - setup_styles              : Apply VS Code–style colors and fonts
#     - create_header             : Create header with title and instructions
#     - create_toolbar            : Create toolbar with function buttons
#     - create_main_layout        : Set up file list and media preview panels
#     - create_status_bar         : Create status bar at the bottom
#     - show_feedback             : Show temporary status messages
#     - bind_keyboard_shortcuts   : Bind all keyboard shortcuts
#     - choose_source_folder      : Select and load media folder
#     - open_optimized_folder     : Select and load optimized folder
#     - populate_file_listbox     : Fill file list panel
#     - on_file_select            : Handle file selection from list
#     - open_current_file         : Open current file in system viewer
#     - show_current_file         : Display current file in preview
#     - video_thread_func         : Thread for video playback
#     - update_video_frame        : Update video frame in preview
#     - move_file_by_key          : Move file to category by key
#     - on_key_press              : Handle key press events
#     - manual_move               : Move file by manual key input
#     - skip_current_file         : Skip current file
#     - undo_last_move            : Undo last file move
#     - rewind_video              : Rewind video 5 seconds
#     - fast_forward_video        : Fast forward video 5 seconds
#     - open_sorted_folder        : Open sorted folder in system
#     - configure_keys            : Configure category key mappings
#     - change_language           : Switch application language
#     - show_help                 : Show help dialog
#     - show_text_report          : Show text report in popup
#     - analyze_duplicates        : Find and report duplicate files
#     - group_similar_files       : Group similar images by perceptual hash
#     - generate_report           : Generate folder content report
#     - apply_filters             : Filter files by size/extension
#
# - Main block:
#     - if __name__ == "__main__": Start the application
# -----------------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import cv2
import os
import shutil
import threading
import time
import json
import hashlib
import sys
import subprocess
import winreg
import imagehash  # For perceptual image hashing
import datetime


class FlashSortMediaOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("FlashSort Media Organizer")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1e1e1e")
        
        # Colors and fonts (VS Code–style)
        self.BG_COLOR = "#1e1e1e"
        self.FG_COLOR = "#d4d4d4"
        self.ACCENT_COLOR = "#007acc"
        self.BUTTON_BG = "#3c3c3c"
        self.FONT_MAIN = ("Consolas", 14)
        self.FONT_TITLE = ("Consolas", 24, "bold")
        self.FONT_INSTR = ("Consolas", 12)
        
        # Configuration file
        self.config_file = "flashsort_config.json"

        # Category key mappings (used exclusively for moving files)
        self.key_mappings = {
            'A': "Category A",
            'S': "Category S",
            'D': "Category D",
            'F': "Category F",
            'J': "Category J",
            'K': "Category K",
            'L': "Category L",
            ';': "Category ;"
        }
        self.load_config()
        
        # Set primary language to English
        self.language = "en"
        
        # Variables for file/media handling
        self.source_folder = ""
        self.root_folder = ""  # Додаємо для зберігання вибраної користувачем папки
        self.file_list = []
        self.current_index = None  # index of current file in list
        self.video_capture = None
        self.video_playing = False
        self.video_thread = None
        self.frame_lock = threading.Lock()
        self.current_photo = None
        
        # For undoing the last file move
        self.last_move = None
        
        self.setup_styles()
        self.create_header()       # Header with title and instructions
        self.create_toolbar()      # Fixed toolbar with all function buttons (all visible)
        self.create_main_layout()  # Main area: left file list and media preview
        self.create_status_bar()   # Bottom status bar
        self.bind_keyboard_shortcuts()
        
    # --- Configuration and styles ---
    def load_config(self):
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            self.key_mappings = config.get("key_mappings", self.key_mappings)
        except Exception:
            pass
        
    def save_config(self):
        config = {"key_mappings": self.key_mappings}
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print("Error saving configuration:", e)
        
    def setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background=self.BG_COLOR)
        style.configure("TLabel", background=self.BG_COLOR, foreground=self.FG_COLOR, font=self.FONT_MAIN)
        style.configure("Title.TLabel", background=self.BG_COLOR, foreground=self.FG_COLOR, font=self.FONT_TITLE)
        style.configure("Instr.TLabel", background=self.BG_COLOR, foreground=self.FG_COLOR, font=self.FONT_INSTR)
        style.configure("Status.TLabel", background=self.BUTTON_BG, foreground=self.FG_COLOR, font=self.FONT_MAIN)
        
    # --- Header with title and instruction text ---
    def create_header(self):
        self.header_frame = ttk.Frame(self.root)
        self.header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title = ttk.Label(self.header_frame, text="NeonSort Media Organizer", style="Title.TLabel", anchor="center")
        title.pack(fill=tk.X)
        
        instr_text = ("Keyboard Shortcuts: 8: Help | 1: Open Folder | O: Open Optimized Folder | "
                      "P: Open File | X: Skip File | U: Undo | T: Rewind (5 sec) | I: Fast Forward (5 sec) | "
                      "E: Open Sorted Folder | Space: Configure Keys")
        instr = ttk.Label(self.header_frame, text=instr_text, style="Instr.TLabel", anchor="center")
        instr.pack(fill=tk.X, pady=(5,0))
        
    # --- Fixed toolbar with function buttons (visible for mouse control) ---
    def create_toolbar(self):
        self.toolbar_frame = ttk.Frame(self.root)
        self.toolbar_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create buttons for each function
        btn_open_folder = ttk.Button(self.toolbar_frame, text="Open Folder", command=self.choose_source_folder)
        btn_open_folder.pack(side=tk.LEFT, padx=5)
        
        btn_open_optimized = ttk.Button(self.toolbar_frame, text="Open Optimized Folder", command=self.open_optimized_folder)
        btn_open_optimized.pack(side=tk.LEFT, padx=5)
        
        btn_open_file = ttk.Button(self.toolbar_frame, text="Open File", command=self.open_current_file)
        btn_open_file.pack(side=tk.LEFT, padx=5)
        
        btn_skip = ttk.Button(self.toolbar_frame, text="Skip File", command=self.skip_current_file)
        btn_skip.pack(side=tk.LEFT, padx=5)
        
        btn_undo = ttk.Button(self.toolbar_frame, text="Undo", command=self.undo_last_move)
        btn_undo.pack(side=tk.LEFT, padx=5)
        
        btn_rewind = ttk.Button(self.toolbar_frame, text="Rewind", command=self.rewind_video)
        btn_rewind.pack(side=tk.LEFT, padx=5)
        
        btn_forward = ttk.Button(self.toolbar_frame, text="Fast Forward", command=self.fast_forward_video)
        btn_forward.pack(side=tk.LEFT, padx=5)
        
        btn_open_sorted = ttk.Button(self.toolbar_frame, text="Open Sorted", command=self.open_sorted_folder)
        btn_open_sorted.pack(side=tk.LEFT, padx=5)
        
        btn_configure = ttk.Button(self.toolbar_frame, text="Configure Keys", command=self.configure_keys)
        btn_configure.pack(side=tk.LEFT, padx=5)
        
        btn_help = ttk.Button(self.toolbar_frame, text="Help", command=self.show_help)
        btn_help.pack(side=tk.LEFT, padx=5)
        
    # --- Main layout (left: file list; right: media preview) ---
    def create_main_layout(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel – File Explorer
        self.sidebar_frame = ttk.Frame(self.main_frame, width=300)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        sidebar_title = ttk.Label(self.sidebar_frame, text="Files", style="Title.TLabel")
        sidebar_title.pack(pady=5)
        self.file_listbox = tk.Listbox(self.sidebar_frame, font=self.FONT_MAIN, bg=self.BUTTON_BG,
                                       fg=self.FG_COLOR, selectbackground=self.ACCENT_COLOR)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)
        
        # Right panel – Media preview
        self.preview_frame = ttk.Frame(self.main_frame, relief="sunken")
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.media_label = ttk.Label(self.preview_frame, anchor="center")
        self.media_label.pack(fill=tk.BOTH, expand=True)
        
    # --- Status bar ---
    def create_status_bar(self):
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        self.status_label = ttk.Label(self.status_frame, text="File: ", style="Status.TLabel", anchor="w")
        self.status_label.pack(fill=tk.X)
        
    # --- Function to show feedback messages ---
    def show_feedback(self, msg):
        self.status_label.config(text=msg)
        self.root.after(2000, lambda: self.status_label.config(text=f"File: {self.file_list[self.current_index] if self.current_index is not None and self.current_index < len(self.file_list) else ''}"))
        
    # --- Bind keyboard shortcuts (unique keys for system functions) ---
    def bind_keyboard_shortcuts(self):
        self.root.bind("<Key>", self.on_key_press)
        self.root.bind("8", lambda event: self.show_help())
        self.root.bind("1", lambda event: self.choose_source_folder())
        self.root.bind("o", lambda event: self.open_optimized_folder())
        self.root.bind("p", lambda event: self.open_current_file())
        self.root.bind("x", lambda event: self.skip_current_file())
        self.root.bind("u", lambda event: self.undo_last_move())
        self.root.bind("t", lambda event: self.rewind_video())
        self.root.bind("i", lambda event: self.fast_forward_video())
        self.root.bind("e", lambda event: self.open_sorted_folder())
        self.root.bind("<space>", lambda event: self.configure_keys())
        
    # --- File/media handling functions ---
    def choose_source_folder(self):
        folder = filedialog.askdirectory(title="Select Media Folder")
        if folder:
            # Створюємо головну папку FlashSort_dateYYYY-MM-DD
            today = datetime.date.today()
            main_folder_name = f"FlashSort_date{today.strftime('%Y-%m-%d')}"
            main_folder_path = os.path.join(folder, main_folder_name)
            if not os.path.exists(main_folder_path):
                os.makedirs(main_folder_path)
            self.root_folder = folder
            self.source_folder = main_folder_path
            # Копіюємо/переміщаємо файли з вибраної папки у головну папку (тільки медіа)
            self.file_list = []
            for file in os.listdir(folder):
                src_path = os.path.join(folder, file)
                dst_path = os.path.join(main_folder_path, file)
                if os.path.isfile(src_path) and file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif',
                                          '.mp4', '.avi', '.mov', '.mp3', '.wav', '.flac')):
                    if not os.path.exists(dst_path):
                        shutil.move(src_path, dst_path)
                    self.file_list.append(file)
            self.file_list.sort()
            self.populate_file_listbox()
            if self.file_list:
                self.current_index = 0
                self.file_listbox.select_set(0)
                self.show_current_file()
                self.file_listbox.focus_set()
                self.show_feedback("Folder loaded")
                
    def open_optimized_folder(self):
        folder = filedialog.askdirectory(title="Select Optimized Media Folder")
        if folder:
            self.source_folder = folder
            self.file_list = []
            try:
                with os.scandir(self.source_folder) as it:
                    for entry in it:
                        if entry.is_file() and entry.name.lower().endswith(
                            ('.png', '.jpg', '.jpeg', '.bmp', '.gif',
                             '.mp4', '.avi', '.mov', '.mp3', '.wav', '.flac')
                        ):
                            self.file_list.append(entry.name)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load files: {e}")
            self.file_list.sort()
            self.populate_file_listbox()
            if self.file_list:
                self.current_index = 0
                self.file_listbox.select_set(0)
                self.show_current_file()
                self.file_listbox.focus_set()
                self.show_feedback("Optimized folder loaded")
                
    def populate_file_listbox(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.file_list:
            self.file_listbox.insert(tk.END, file)
            
    def on_file_select(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            self.current_index = selection[0]
            self.show_current_file()
            
    def open_current_file(self):
        if self.current_index is not None and self.current_index < len(self.file_list):
            current_file = self.file_list[self.current_index]
            file_path = os.path.join(self.source_folder, current_file)
            if os.path.exists(file_path):
                try:
                    if os.name == "nt":
                        os.startfile(file_path)
                    elif os.name == "posix":
                        os.system(f'xdg-open "{file_path}"')
                    else:
                        messagebox.showinfo("Info", "File opening not supported on your OS.")
                    self.show_feedback("File opened")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open file: {e}")
            else:
                messagebox.showerror("Error", "File does not exist.")
                
    def show_current_file(self):
        # Stop previous video playback if any
        if self.video_playing:
            self.video_playing = False
            if self.video_thread is not None:
                self.video_thread.join()
            self.current_photo = None

        # Stop any playing audio
        self.stop_audio_playback()

        if self.current_index is None or self.current_index >= len(self.file_list):
            self.media_label.config(text="No files to display", image="")
            self.status_label.config(text="File: ")
            return

        current_file = self.file_list[self.current_index]
        self.status_label.config(text=f"File: {current_file}")
        file_path = os.path.join(self.source_folder, current_file)

        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            try:
                img = Image.open(file_path)
                img.thumbnail((800, 600))
                photo = ImageTk.PhotoImage(img)
                self.media_label.config(image=photo, text="")
                self.media_label.image = photo
            except Exception:
                self.media_label.config(text="Image load error", image="")
            self.remove_video_controls()
        elif file_path.lower().endswith('.gif'):
            self.show_gif(file_path)
            self.remove_video_controls()
        elif file_path.lower().endswith(('.mp4', '.avi', '.mov')):
            self.show_video(file_path)
        elif file_path.lower().endswith(('.mp3', '.wav', '.flac')):
            self.show_audio(file_path)
        else:
            self.media_label.config(text="Unsupported format", image="")
            self.remove_video_controls()

    def remove_video_controls(self):
        # Remove video controls if present
        if hasattr(self, 'video_slider') and self.video_slider.winfo_exists():
            self.video_slider.destroy()
        if hasattr(self, 'video_time_label') and self.video_time_label.winfo_exists():
            self.video_time_label.destroy()
        if hasattr(self, 'video_pause_btn') and self.video_pause_btn.winfo_exists():
            self.video_pause_btn.destroy()

    def show_gif(self, file_path):
        # Display animated GIF in the media_label
        try:
            self.gif_frames = []
            self.gif_delays = []
            img = Image.open(file_path)
            for frame in range(0, img.n_frames):
                img.seek(frame)
                frame_img = img.copy().convert("RGBA")
                self.gif_frames.append(ImageTk.PhotoImage(frame_img))
                delay = img.info.get('duration', 100)
                self.gif_delays.append(delay)
            self.gif_frame_index = 0
            self.media_label.config(image=self.gif_frames[0], text="")
            self.media_label.image = self.gif_frames[0]
            self.after_id = self.root.after(self.gif_delays[0], self.update_gif_frame)
        except Exception:
            self.media_label.config(text="GIF load error", image="")

    def update_gif_frame(self):
        if not hasattr(self, 'gif_frames') or not self.gif_frames:
            return
        self.gif_frame_index = (self.gif_frame_index + 1) % len(self.gif_frames)
        self.media_label.config(image=self.gif_frames[self.gif_frame_index])
        self.media_label.image = self.gif_frames[self.gif_frame_index]
        delay = self.gif_delays[self.gif_frame_index]
        self.after_id = self.root.after(delay, self.update_gif_frame)

    def show_video(self, file_path):
        # Stop previous video playback if any
        self.video_playing = False
        if hasattr(self, 'video_slider') and self.video_slider.winfo_exists():
            self.video_slider.destroy()
        if hasattr(self, 'video_time_label') and self.video_time_label.winfo_exists():
            self.video_time_label.destroy()
        if hasattr(self, 'video_pause_btn') and self.video_pause_btn.winfo_exists():
            self.video_pause_btn.destroy()

        # Stop any playing audio
        self.stop_audio_playback()

        # Open video with OpenCV
        if self.video_capture is not None:
            self.video_capture.release()
        self.video_capture = cv2.VideoCapture(file_path)
        if not self.video_capture.isOpened():
            self.media_label.config(text="Video load error", image="")
            return

        # Try to open audio with ffplay (if available)
        self.start_audio_playback(file_path)

        self.video_total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_fps = self.video_capture.get(cv2.CAP_PROP_FPS) or 25
        self.video_duration = self.video_total_frames / self.video_fps if self.video_fps else 0

        # Add slider for video position
        self.video_slider_dragging = False
        self.video_slider = ttk.Scale(self.preview_frame, from_=0, to=self.video_total_frames-1, orient=tk.HORIZONTAL, length=600, command=self.on_video_slider)
        self.video_slider.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.video_slider.set(0)
        self.video_slider.bind("<Button-1>", self.on_slider_press)
        self.video_slider.bind("<ButtonRelease-1>", self.on_slider_release)

        # Add label for time
        self.video_time_label = ttk.Label(self.preview_frame, text="00:00 / 00:00", style="Instr.TLabel")
        self.video_time_label.pack(side=tk.BOTTOM, anchor="e", padx=10)

        # Add pause/play button
        self.video_paused = False
        self.video_pause_btn = ttk.Button(self.preview_frame, text="Pause", command=self.toggle_video_pause)
        self.video_pause_btn.pack(side=tk.BOTTOM, anchor="w", padx=10)

        # Bind arrow keys for seeking (10 seconds)
        self.root.bind("<Left>", self.seek_video_left)
        self.root.bind("<Right>", self.seek_video_right)

        # Start video playback via after loop
        self.video_playing = True
        self.after_video_id = self.root.after(0, self.video_after_loop)

    def on_slider_press(self, event):
        self.video_slider_dragging = True

    def on_slider_release(self, event):
        self.video_slider_dragging = False
        value = self.video_slider.get()
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, int(value))
        self.update_video_frame()
        self.seek_audio_to_frame(int(value))

    def on_video_slider(self, value):
        if self.video_slider_dragging:
            # Only update frame when dragging is released
            return
        frame = int(float(value))
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame)
        self.update_video_frame()
        self.seek_audio_to_frame(frame)

    def toggle_video_pause(self):
        self.video_paused = not self.video_paused
        self.video_pause_btn.config(text="Play" if self.video_paused else "Pause")
        if not self.video_paused and self.video_playing:
            self.after_video_id = self.root.after(int(1000 / self.video_fps), self.video_after_loop)

    def video_after_loop(self):
        if not self.video_playing or self.video_paused:
            return
        if not self.video_slider_dragging:
            self.update_video_frame()
            cur_frame = int(self.video_capture.get(cv2.CAP_PROP_POS_FRAMES))
            if hasattr(self, 'video_slider') and self.video_slider.winfo_exists():
                self.video_slider.set(cur_frame)
            if hasattr(self, 'video_time_label') and self.video_time_label.winfo_exists():
                cur_time = cur_frame / self.video_fps if self.video_fps else 0
                total_time = self.video_duration
                self.video_time_label.config(
                    text=f"{self.format_time(cur_time)} / {self.format_time(total_time)}"
                )
            # Stop if at end
            if cur_frame >= self.video_total_frames - 1:
                self.video_playing = False
                self.stop_audio_playback()
                return
        self.after_video_id = self.root.after(int(1000 / self.video_fps), self.video_after_loop)

    def update_video_frame(self):
        if self.video_capture is not None:
            ret, frame = self.video_capture.read()
            if not ret:
                return
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img.thumbnail((800, 600))
            photo = ImageTk.PhotoImage(img)
            self.media_label.config(image=photo, text="")
            self.media_label.image = photo

    def format_time(self, seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"

    # --- Audio playback for video/audio files using ffplay (if available) ---
    def start_audio_playback(self, file_path):
        self.stop_audio_playback()
        # Only for video/audio files
        if not file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mp3', '.wav', '.flac')):
            return
        # Try to use ffplay for audio playback (must be installed and in PATH)
        try:
            # Start ffplay in a subprocess, no video, no console window
            self.audio_proc = subprocess.Popen(
                ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', '-threads', '1', file_path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception:
            self.audio_proc = None

    def stop_audio_playback(self):
        if hasattr(self, 'audio_proc') and self.audio_proc is not None:
            try:
                self.audio_proc.terminate()
            except Exception:
                pass
            self.audio_proc = None

    def seek_audio_to_frame(self, frame):
        # Restart ffplay at the new position (approximate)
        if not hasattr(self, 'audio_proc') or self.audio_proc is None:
            return
        if self.video_fps:
            seconds = frame / self.video_fps
            self.stop_audio_playback()
            current_file = self.file_list[self.current_index]
            file_path = os.path.join(self.source_folder, current_file)
            try:
                self.audio_proc = subprocess.Popen(
                    ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', '-threads', '1', '-ss', str(seconds), file_path],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception:
                self.audio_proc = None

    # --- Audio file preview (for .mp3, .wav, .flac) ---
    def show_audio(self, file_path):
        self.media_label.config(text="Playing audio...", image="")
        self.start_audio_playback(file_path)
    def move_file_by_key(self, key):
        if self.current_index is None or self.current_index >= len(self.file_list):
            return
        if key not in self.key_mappings:
            return
        folder_name = self.key_mappings[key]
        # Категорійна папка створюється всередині self.source_folder (головної папки)
        dest_folder = os.path.join(self.source_folder, folder_name)
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        current_file = self.file_list[self.current_index]
        src = os.path.join(self.source_folder, current_file)
        dst = os.path.join(dest_folder, current_file)
        try:
            shutil.move(src, dst)
            self.last_move = (src, dst)
        except Exception:
            print("Error moving file")
        self.file_list.pop(self.current_index)
        self.populate_file_listbox()
        if self.file_list:
            new_index = min(self.current_index, len(self.file_list) - 1)
            self.current_index = new_index
            self.file_listbox.select_set(new_index)
        else:
            self.current_index = None
        self.show_current_file()
        self.show_feedback("File moved")
            
    def on_key_press(self, event):
        key = event.char.upper()
        # If key is in the category mappings, move file accordingly.
        if key in self.key_mappings:
            self.move_file_by_key(key)
            
    def manual_move(self):
        key = simpledialog.askstring("Move File", "Enter key for sorting:")
        if key:
            key = key.upper()
            if key in self.key_mappings:
                self.move_file_by_key(key)
            else:
                messagebox.showerror("Error", f"Key '{key}' is not configured.")
                
    def skip_current_file(self):
        if self.current_index is not None and self.current_index < len(self.file_list):
            self.file_list.pop(self.current_index)
            self.populate_file_listbox()
            if self.file_list:
                new_index = min(self.current_index, len(self.file_list) - 1)
                self.current_index = new_index
                self.file_listbox.select_set(new_index)
            else:
                self.current_index = None
        if self.video_playing:
            self.video_playing = False
            if self.video_thread is not None:
                self.video_thread.join()
            self.current_photo = None
        self.show_current_file()
        self.show_feedback("File skipped")
                
    def undo_last_move(self):
        if self.last_move:
            src, dst = self.last_move
            if os.path.exists(dst):
                try:
                    shutil.move(dst, src)
                    messagebox.showinfo("Undo", "Last action undone.")
                    self.last_move = None
                    self.choose_source_folder()  # Reload file list
                    self.show_feedback("Undo performed")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to undo last action: {e}")
            else:
                messagebox.showerror("Error", "No file to undo.")
        else:
            messagebox.showinfo("Undo", "No action to undo.")
            
    def rewind_video(self):
        if self.video_capture is not None and self.video_playing:
            current_time = self.video_capture.get(cv2.CAP_PROP_POS_MSEC)
            new_time = max(0, current_time - 5000)
            self.video_capture.set(cv2.CAP_PROP_POS_MSEC, new_time)
            self.show_feedback("Video rewound")
            
    def fast_forward_video(self):
        if self.video_capture is not None and self.video_playing:
            current_time = self.video_capture.get(cv2.CAP_PROP_POS_MSEC)
            new_time = current_time + 5000
            self.video_capture.set(cv2.CAP_PROP_POS_MSEC, new_time)
            self.show_feedback("Video forwarded")
            
    def open_sorted_folder(self):
        if self.source_folder:
            try:
                if os.name == "nt":
                    os.startfile(self.source_folder)
                elif os.name == "posix":
                    os.system(f'xdg-open "{self.source_folder}"')
                else:
                    messagebox.showinfo("Info", "Folder opening not supported on your OS.")
                self.show_feedback("Sorted folder opened")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open folder: {e}")
        else:
            messagebox.showerror("Error", "No folder selected.")
            
    def configure_keys(self):
        config_win = tk.Toplevel(self.root)
        config_win.title("Configure Keys")
        config_win.configure(bg=self.BG_COLOR)
        ttk.Label(config_win, text="Key", background=self.BG_COLOR, foreground=self.FG_COLOR, font=self.FONT_MAIN).grid(row=0, column=0, padx=10, pady=10)
        ttk.Label(config_win, text="Folder Name", background=self.BG_COLOR, foreground=self.FG_COLOR, font=self.FONT_MAIN).grid(row=0, column=1, padx=10, pady=10)
        entries = {}
        row = 1
        for key, folder in self.key_mappings.items():
            ttk.Label(config_win, text=key, background=self.BG_COLOR, foreground=self.FG_COLOR, font=self.FONT_MAIN).grid(row=row, column=0, padx=10, pady=5)
            entry = tk.Entry(config_win, font=self.FONT_MAIN)
            entry.insert(0, folder)
            entry.grid(row=row, column=1, padx=10, pady=5)
            entries[key] = entry
            row += 1
        def save_config():
            for key, entry in entries.items():
                self.key_mappings[key] = entry.get().strip() or self.key_mappings[key]
            self.save_config()
            config_win.destroy()
        btn_save = ttk.Button(config_win, text="Save", command=save_config)
        btn_save.grid(row=row, column=0, columnspan=2, pady=10)
        
    def change_language(self):
        self.language = "ua" if self.language == "en" else "en"
        messagebox.showinfo("Language Change", f"Language set to {self.language.upper()}. Please restart the application for changes to take effect.")
        
    def show_help(self):
        help_text = (
            "NeonSort Media Organizer – Help\n\n"
            "Keyboard Shortcuts:\n"
            "  8      - Help (display this message)\n"
            "  1      - Open Folder\n"
            "  O      - Open Optimized Folder\n"
            "  P      - Open File\n"
            "  X      - Skip File\n"
            "  U      - Undo Last Action\n"
            "  T      - Rewind Video (5 sec)\n"
            "  I      - Fast Forward Video (5 sec)\n"
            "  E      - Open Sorted Folder\n"
            "  Space  - Configure Keys\n\n"
            "Category keys (A, S, D, F, J, K, L, ;) move the current file to the corresponding category folder.\n\n"
            "Mouse Controls: Use the toolbar buttons above to perform actions with the mouse."
        )
        messagebox.showinfo("Help", help_text)
        
    def show_text_report(self, title, text):
        report_win = tk.Toplevel(self.root)
        report_win.title(title)
        report_win.configure(bg=self.BG_COLOR)
        txt = tk.Text(report_win, wrap="word", font=self.FONT_MAIN, bg=self.BG_COLOR, fg=self.FG_COLOR)
        txt.insert("1.0", text)
        txt.config(state="disabled")
        txt.pack(expand=True, fill="both")
        
    def analyze_duplicates(self):
        if not self.source_folder:
            messagebox.showerror("Error", "No folder selected.")
            return
        duplicates = {}
        hash_dict = {}
        media_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.mp4', '.avi', '.mov', '.mp3', '.wav', '.flac')
        for root_dir, dirs, files in os.walk(self.source_folder):
            for file in files:
                if file.lower().endswith(media_extensions):
                    file_path = os.path.join(root_dir, file)
                    try:
                        with open(file_path, 'rb') as f:
                            data = f.read()
                        md5_hash = hashlib.md5(data).hexdigest()
                        if md5_hash in hash_dict:
                            hash_dict[md5_hash].append(file_path)
                        else:
                            hash_dict[md5_hash] = [file_path]
                    except Exception as e:
                        print("Error processing file:", file_path, e)
        for h, files in hash_dict.items():
            if len(files) > 1:
                duplicates[h] = files
        if duplicates:
            result = "Duplicate files found:\n\n"
            for h, files in duplicates.items():
                result += f"Hash: {h}\n"
                for file in files:
                    result += f"  {file}\n"
                result += "\n"
            self.show_text_report("Duplicate Analysis", result)
        else:
            messagebox.showinfo("Duplicate Analysis", "No duplicates found.")
            
    def group_similar_files(self):
        if not self.source_folder:
            messagebox.showerror("Error", "No folder selected.")
            return
        image_files = []
        for root_dir, dirs, files in os.walk(self.source_folder):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    image_files.append(os.path.join(root_dir, file))
        if not image_files:
            messagebox.showinfo("Grouping Similar", "No images found.")
            return
        threshold = 5  # threshold for perceptual hash difference
        phashes = {}
        for file_path in image_files:
            try:
                ph = imagehash.phash(Image.open(file_path))
                phashes[file_path] = ph
            except Exception as e:
                print("Error calculating phash for", file_path, e)
        groups = []
        visited = set()
        for file1 in image_files:
            if file1 in visited:
                continue
            group = [file1]
            visited.add(file1)
            for file2 in image_files:
                if file2 in visited:
                    continue
                if abs(phashes[file1] - phashes[file2]) <= threshold:
                    group.append(file2)
                    visited.add(file2)
            if len(group) > 1:
                groups.append(group)
        if groups:
            result = "Similar image groups:\n\n"
            for i, group in enumerate(groups, start=1):
                result += f"Group {i}:\n"
                for file in group:
                    result += f"  {file}\n"
                result += "\n"
            self.show_text_report("Grouping Similar Images", result)
        else:
            messagebox.showinfo("Grouping Similar", "No similar groups found.")
            
    def generate_report(self):
        if not self.source_folder:
            messagebox.showerror("Error", "No folder selected.")
            return
        total_size = 0
        file_count = 0
        format_count = {}
        for root_dir, dirs, files in os.walk(self.source_folder):
            for file in files:
                file_path = os.path.join(root_dir, file)
                try:
                    size = os.path.getsize(file_path)
                    total_size += size
                    file_count += 1
                    ext = os.path.splitext(file)[1].lower()
                    format_count[ext] = format_count.get(ext, 0) + 1
                except Exception as e:
                    print("Error getting size for", file_path, e)
        report = f"Report for folder: {self.source_folder}\n\n"
        report += f"Total files: {file_count}\n"
        report += f"Total size: {total_size / (1024*1024):.2f} MB\n\n"
        report += "Files by format:\n"
        for ext, count in format_count.items():
            report += f"  {ext if ext else 'no extension'}: {count}\n"
        report += "\nFor detailed duplicate analysis, use the 'Analyze Duplicates' option in the menu."
        self.show_text_report("Report", report)
        
    def apply_filters(self):
        if not self.source_folder:
            messagebox.showerror("Error", "No folder selected.")
            return
        filter_win = tk.Toplevel(self.root)
        filter_win.title("Filters and Sorting")
        filter_win.configure(bg=self.BG_COLOR)
        ttk.Label(filter_win, text="Min Size (KB)", background=self.BG_COLOR, foreground=self.FG_COLOR, font=self.FONT_MAIN).grid(row=0, column=0, padx=10, pady=5)
        min_size_entry = tk.Entry(filter_win, font=self.FONT_MAIN)
        min_size_entry.grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(filter_win, text="Max Size (KB)", background=self.BG_COLOR, foreground=self.FG_COLOR, font=self.FONT_MAIN).grid(row=1, column=0, padx=10, pady=5)
        max_size_entry = tk.Entry(filter_win, font=self.FONT_MAIN)
        max_size_entry.grid(row=1, column=1, padx=10, pady=5)
        ttk.Label(filter_win, text="Extension (e.g., .jpg)", background=self.BG_COLOR, foreground=self.FG_COLOR, font=self.FONT_MAIN).grid(row=2, column=0, padx=10, pady=5)
        ext_entry = tk.Entry(filter_win, font=self.FONT_MAIN)
        ext_entry.grid(row=2, column=1, padx=10, pady=5)
        def apply():
            try:
                min_size = float(min_size_entry.get()) * 1024 if min_size_entry.get() else 0
            except:
                min_size = 0
            try:
                max_size = float(max_size_entry.get()) * 1024 if max_size_entry.get() else float('inf')
            except:
                max_size = float('inf')
            ext_filter = ext_entry.get().strip().lower()
            filtered = []
            for file in self.file_list:
                file_path = os.path.join(self.source_folder, file)
                try:
                    size = os.path.getsize(file_path)
                except Exception:
                    continue
                if size < min_size or size > max_size:
                    continue
                if ext_filter and not file.lower().endswith(ext_filter):
                    continue
                filtered.append(file)
            if filtered:
                self.file_list = filtered
                self.current_index = 0
                self.populate_file_listbox()
                self.file_listbox.select_set(0)
                self.show_current_file()
                messagebox.showinfo("Filters Applied", f"{len(filtered)} files match the criteria.")
            else:
                messagebox.showinfo("Filters Applied", "No files match the criteria.")
            filter_win.destroy()
        btn_apply = ttk.Button(filter_win, text="Apply", command=apply)
        btn_apply.grid(row=3, column=0, columnspan=2, pady=10)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = FlashSortMediaOrganizer(root)
    root.mainloop()
