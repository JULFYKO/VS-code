#  _____ _           _     _____                         
# |  ___| | __ _ ___| |__ |  ___| __ __ _ _ __ ___   ___ 
# | |_  | |/ _` / __| '_ \| |_ | '__/ _` | '_ ` _ \ / _ \
# |  _| | | (_| \__ \ | | |  _|| | | (_| | | | | | |  __/
# |_|   |_|\__,_|___/_| |_|_|  |_|  \__,_|_| |_| |_|\___|
# -----------------------------------------------------------------------------
# Photo Tournament Organizer
#
# This program is a desktop application for quickly sorting, viewing, and organizing
# photo files within a selected folder using a tournament-style interface.
# It features a modern VS Code–style interface with both keyboard shortcuts and mouse controls.
#
# Main features:
# - Tournament-style photo comparison (2 or 4 choices per match)
# - Keyboard shortcuts for fast selection and undo
# - Progress bar and round/match info
# - View original image with zoom
# - Auto-save and manual save of tournament state
# - Export/import settings and session history
# - Show tournament tree/log
#
# Author: JulfyKo
# -----------------------------------------------------------------------------
# Program Structure Overview (for quick navigation)
#
# - PhotoTournament class:
#     - __init__                  : Main initialization
#     - load_valid_images         : Load only valid images
#     - build_ui                  : Build main UI
#     - on_resize                 : Handle window resize
#     - on_close                  : Save state and close
#     - schedule_autosave         : Schedule auto-save
#     - auto_save                 : Auto-save state
#     - manual_save               : Manual save to emergency folder
#     - check_for_saved_state     : Offer to restore session
#     - start_round               : Start a new round
#     - update_info               : Update round/match info
#     - update_progress           : Update progress bar
#     - next_match                : Load next match
#     - display_current_choices   : Show current images
#     - save_state                : Save state for undo
#     - undo                      : Undo last action
#     - on_key_press              : Handle key presses
#     - make_choice               : Process a choice
#     - make_choice_by_index      : Process button choice
#     - view_original             : Show original image with zoom
#     - save_log_to_files         : Save tournament log
#     - append_session_history    : Save session history
#     - show_tree                 : Show tournament tree/log
#     - open_settings             : Open settings window
#     - import_settings           : Import settings from file
#     - show_winner               : Show final winner
#     - restart                   : Restart tournament
#
# - Main block:
#     - if __name__ == "__main__": Start the application
# -----------------------------------------------------------------------------

import os
import random
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import json
import time
import datetime

# ------------------------------
# ===== Quick Settings =====
# ------------------------------

# Key bindings for choices
KEY_LEFT = 'd'      # Key for selecting the left image (or first option)
KEY_RIGHT = 'f'     # Key for selecting the right image (or second option)
KEY_OPTION3 = 'j'   # Key for selecting third option (if num_choices==4)
KEY_OPTION4 = 'k'   # Key for selecting fourth option (if num_choices==4)
KEY_UNDO = 'z'      # Key for undo
KEY_SHOW_TREE = 't' # Key to show tournament tree
KEY_SETTINGS = 's'  # Key to open settings

# Image sizes and layout
PHOTO_SIZE = (300, 300)         # Default size for images during the tournament
FINAL_PHOTO_SIZE = (500, 500)   # Size for the final image

# Progress bar settings
PROGRESS_BAR_LENGTH = 300       # Length of progress bar

# Auto-save settings
AUTO_SAVE_INTERVAL = 5000      # Auto-save interval in milliseconds (5 seconds)
# Save auto-save file in the home directory
AUTO_SAVE_FILE = os.path.join(os.path.expanduser("~"), "autosave_state.json")

# Emergency folder for manual/critical saves
EMERGENCY_SAVE_FOLDER = os.path.join(os.path.expanduser("~"), "EmergencySaves")
if not os.path.exists(EMERGENCY_SAVE_FOLDER):
    try:
        os.makedirs(EMERGENCY_SAVE_FOLDER)
    except Exception as e:
        print(f"Error creating emergency save folder: {e}")

# Tournament settings defaults
DEFAULT_TOURNAMENT_TYPE = "Single Elimination"  # (stub: "Round Robin" can be added later)
DEFAULT_NUM_CHOICES = 2                         # Number of choices per match (2 or 4)

# Settings file for export/import
SETTINGS_FILE = "tournament_settings.json"

# Session history file
SESSION_HISTORY_FILE = "session_history.json"

# Add new tournament types and settings
TOURNAMENT_TYPES = [
    "Single Elimination",
    "Double Elimination",
    "Round Robin",
    "One Round",  # Новий тип
    "Custom"
]

# ------------------------------
# ===== Main Application Class =====
# ------------------------------

class PhotoTournament:
    def __init__(self, root, photo_paths):
        """
        Initializes the photo tournament.
        """
        self.root = root
        self.root.title("Photo Tournament")
        
        # Load only valid images
        self.all_photos = self.load_valid_images(photo_paths)
        if len(self.all_photos) < 2:
            messagebox.showerror("Error", "Not enough valid photos for the tournament.")
            self.root.destroy()
            return
        self.photo_paths = self.all_photos.copy()
        
        # Program settings (can be modified via the settings panel)
        self.photo_size = PHOTO_SIZE
        self.final_photo_size = FINAL_PHOTO_SIZE
        self.progress_length = PROGRESS_BAR_LENGTH
        self.auto_save_interval = AUTO_SAVE_INTERVAL
        self.tournament_type = DEFAULT_TOURNAMENT_TYPE
        self.num_choices = DEFAULT_NUM_CHOICES
        self.allow_skip = True
        self.auto_advance = False
        self.shuffle = True
        self.seeding = False
        self.custom_bracket = None
        # TODO: Implement custom bracket logic if needed
        self.round_robin_matches = []
        self.double_elim_losers = []
        self.finalists = []
        self.log_window = None
        # Initialize Top N selection attributes
        self.top_n_enabled = False
        self.top_n_value = 1

        # Match statistics for analysis
        self.stats = {
            "total_decision_time": 0.0,
            "num_decisions": 0,
            "num_undos": 0,
            "selection_counts": {KEY_LEFT: 0, KEY_RIGHT: 0, KEY_OPTION3: 0, KEY_OPTION4: 0}
        }
        self.match_start_time = time.time()

        # Tournament state variables
        self.round = 1
        self.match_number = 0
        self.winners = []
        self.current_choices = []  # List of images for the current match (length = num_choices)
        self.history = []          # State history for multi-level undo
        self.match_log = []        # Log of all matches
        
        # Build the UI
        self.build_ui()
        
        # Bind events: auto-save on close and window resize
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<Configure>", self.on_resize)
        self.last_width = self.root.winfo_width()
        
        # Check for a saved session and offer to restore it
        self.check_for_saved_state()
        
        # Bind keys for quick control
        self.root.bind("<Key>", self.on_key_press)
        
        # Start auto-save timer
        self.schedule_autosave()
        
        # Start the first round
        self.start_round()

    def load_valid_images(self, photo_paths):
        """
        Returns a list of valid image file paths by attempting to open them.
        """
        valid = []
        for path in photo_paths:
            try:
                with Image.open(path) as img:
                    img.verify()
                valid.append(path)
            except Exception as e:
                print(f"Skipping invalid image '{path}': {e}")
                continue
        return valid

    def build_ui(self):
        """
        Builds the main frames and widgets.
        """
        try:
            self.top_frame = tk.Frame(self.root)
            self.top_frame.pack(pady=5)
            self.middle_frame = tk.Frame(self.root)
            self.middle_frame.pack()
            self.bottom_frame = tk.Frame(self.root)
            self.bottom_frame.pack(pady=5)

            # Info label and progress bar
            self.info_label = tk.Label(self.top_frame, text="", font=("Arial", 14))
            self.info_label.pack()
            self.progress = ttk.Progressbar(self.top_frame, orient="horizontal", length=self.progress_length, mode="determinate")
            self.progress.pack(pady=5)

            # Image display widgets based on number of choices
            self.image_labels = []
            if self.num_choices == 2:
                self.left_label = tk.Label(self.middle_frame)
                self.left_label.pack(side=tk.LEFT, padx=10, pady=10)
                self.right_label = tk.Label(self.middle_frame)
                self.right_label.pack(side=tk.RIGHT, padx=10, pady=10)
                self.image_labels = [self.left_label, self.right_label]
            elif self.num_choices == 4:
                self.image_labels = []
                for r in range(2):
                    row_frame = tk.Frame(self.middle_frame)
                    row_frame.pack()
                    for c in range(2):
                        lbl = tk.Label(row_frame)
                        lbl.pack(side=tk.LEFT, padx=5, pady=5)
                        self.image_labels.append(lbl)

            # Choice buttons
            self.choice_buttons = []
            choices = []
            if self.num_choices == 2:
                choices = [f"Select Left ({KEY_LEFT.upper()})", f"Select Right ({KEY_RIGHT.upper()})"]
            elif self.num_choices == 4:
                choices = [f"Option 1 ({KEY_LEFT.upper()})", f"Option 2 ({KEY_RIGHT.upper()})",
                           f"Option 3 ({KEY_OPTION3.upper()})", f"Option 4 ({KEY_OPTION4.upper()})"]
            for i, text in enumerate(choices):
                btn = tk.Button(self.bottom_frame, text=text, command=lambda idx=i: self.make_choice_by_index(idx))
                btn.pack(side=tk.LEFT, padx=5)
                self.choice_buttons.append(btn)

            # Additional control buttons
            self.undo_button = tk.Button(self.bottom_frame, text=f"Undo ({KEY_UNDO.upper()})", command=self.undo)
            self.undo_button.pack(side=tk.LEFT, padx=5)
            self.tree_button = tk.Button(self.bottom_frame, text="Show Tournament Tree (T)", command=self.show_tree)
            self.tree_button.pack(side=tk.LEFT, padx=5)
            self.settings_button = tk.Button(self.bottom_frame, text="Settings (S)", command=self.open_settings)
            self.settings_button.pack(side=tk.LEFT, padx=5)
            self.manual_save_button = tk.Button(self.bottom_frame, text="Manual Save", command=self.manual_save)
            self.manual_save_button.pack(side=tk.LEFT, padx=5)
            self.restart_button = tk.Button(self.bottom_frame, text="Restart", command=self.restart)
            self.restart_button.pack(side=tk.LEFT, padx=5)
            # Add new button for log viewing
            self.log_button = tk.Button(self.bottom_frame, text="View Log", command=self.show_log_window)
            self.log_button.pack(side=tk.LEFT, padx=5)
        except Exception as e:
            messagebox.showerror("UI Error", f"An error occurred while building the UI:\n{e}")

    def on_resize(self, event):
        """
        Called when the window is resized.
        Dynamically scales images while maintaining their aspect ratio.
        """
        try:
            if event.widget == self.root:
                if abs(event.width - self.last_width) > 50:
                    self.last_width = event.width
                    scale = event.width / 800  # Base width is 800
                    new_width = int(PHOTO_SIZE[0] * scale)
                    new_height = int(PHOTO_SIZE[1] * scale)
                    self.photo_size = (new_width, new_height)
                    self.display_current_choices()
        except Exception as e:
            print(f"Resize error: {e}")

    def on_close(self):
        """
        Called when the window is closing.
        Saves the state manually and then closes the program.
        """
        try:
            self.auto_save()  # Auto-save before closing
        except Exception as e:
            print(f"Error during auto-save on close: {e}")
        self.root.destroy()

    def schedule_autosave(self):
        """
        Schedules the auto-save function to run after the specified interval.
        """
        try:
            self.root.after(self.auto_save_interval, self.auto_save)
        except Exception as e:
            print(f"Error scheduling auto-save: {e}")

    def auto_save(self):
        """
        Automatically saves the current tournament state to a JSON file.
        """
        state = {
            "round": self.round,
            "match_number": self.match_number,
            "winners": self.winners,
            "photo_paths": self.photo_paths,
            "current_choices": self.current_choices,
            "match_log": self.match_log,
            "stats": self.stats,
            "tournament_type": self.tournament_type,
            "num_choices": self.num_choices
        }
        try:
            with open(AUTO_SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=4)
            # Uncomment next line for debugging auto-save:
            # print("Auto-saved state.")
        except Exception as e:
            messagebox.showerror("Auto-save Error", f"Auto-save failed:\n{e}")
        self.schedule_autosave()  # Reschedule auto-save

    def manual_save(self):
        """
        Manually saves the current state to an emergency folder.
        """
        state = {
            "round": self.round,
            "match_number": self.match_number,
            "winners": self.winners,
            "photo_paths": self.photo_paths,
            "current_choices": self.current_choices,
            "match_log": self.match_log,
            "stats": self.stats,
            "tournament_type": self.tournament_type,
            "num_choices": self.num_choices
        }
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        emergency_file = os.path.join(EMERGENCY_SAVE_FOLDER, f"manual_save_{timestamp}.json")
        try:
            with open(emergency_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Manual Save", f"State manually saved to:\n{emergency_file}")
        except Exception as e:
            messagebox.showerror("Manual Save Error", f"Manual save failed:\n{e}")

    def check_for_saved_state(self):
        """
        If an auto-save file exists, offers to restore the session.
        """
        if os.path.exists(AUTO_SAVE_FILE):
            try:
                if messagebox.askyesno("Restore Session", "A saved session was found. Do you want to restore it?"):
                    with open(AUTO_SAVE_FILE, "r", encoding="utf-8") as f:
                        state = json.load(f)
                    self.round = state.get("round", 1)
                    self.match_number = state.get("match_number", 0)
                    self.winners = state.get("winners", [])
                    self.photo_paths = state.get("photo_paths", self.photo_paths)
                    self.current_choices = state.get("current_choices", [])
                    self.match_log = state.get("match_log", [])
                    self.stats = state.get("stats", self.stats)
                    self.tournament_type = state.get("tournament_type", DEFAULT_TOURNAMENT_TYPE)
                    self.num_choices = state.get("num_choices", DEFAULT_NUM_CHOICES)
                    for widget in self.root.winfo_children():
                        widget.destroy()
                    self.build_ui()
                    messagebox.showinfo("Restore Session", "Session restored successfully.")
            except Exception as e:
                messagebox.showerror("Restore Error", f"Failed to restore session:\n{e}")

    def start_round(self):
        """
        Prepares and starts a new round, supporting multiple tournament types and Top N.
        """
        try:
            if self.shuffle and self.tournament_type not in ("Round Robin", "One Round"):
                random.shuffle(self.photo_paths)
            self.match_number = 0
            self.winners = []
            self.history.clear()
            # Prepare round robin matches if needed
            if self.tournament_type == "Round Robin":
                self.round_robin_matches = []
                for i in range(len(self.photo_paths)):
                    for j in range(i+1, len(self.photo_paths)):
                        self.round_robin_matches.append([self.photo_paths[i], self.photo_paths[j]])
                random.shuffle(self.round_robin_matches)
            # One Round: всі фото по 2/4, але лише 1 раунд
            if self.tournament_type == "One Round":
                self.round = 1
            # TODO: Add support for additional tournament types if needed
            self.update_info()
            self.update_progress()
            self.next_match()
        except Exception as e:
            messagebox.showerror("Round Error", f"Error starting round:\n{e}")

    def update_info(self):
        """
        Updates the info label showing the current round and match number.
        """
        try:
            total_matches = len(self.photo_paths) // self.num_choices
            text = f"Round {self.round} | Match {self.match_number+1} of {total_matches}"
            self.info_label.config(text=text)
        except Exception as e:
            print(f"Error updating info: {e}")

    def update_progress(self):
        """
        Updates the progress bar.
        """
        try:
            total_matches = len(self.photo_paths) // self.num_choices
            value = (self.match_number / total_matches) * 100 if total_matches else 100
            self.progress['value'] = value
            self.root.update_idletasks()
        except Exception as e:
            print(f"Error updating progress: {e}")

    def next_match(self):
        """
        Loads the next set of images for the current match, supporting multiple tournament types and Top N.
        """
        try:
            if self.tournament_type == "Round Robin":
                if self.match_number >= len(self.round_robin_matches):
                    # Determine winner by most wins
                    win_counts = {}
                    for entry in self.match_log:
                        win_counts[entry['winner']] = win_counts.get(entry['winner'], 0) + 1
                    sorted_winners = sorted(win_counts.items(), key=lambda x: -x[1])
                    self.photo_paths = [w[0] for w in sorted_winners]
                    self.show_winner()
                    return
                self.current_choices = self.round_robin_matches[self.match_number]
                self.display_current_choices()
                self.match_number += 1
                self.update_info()
                self.update_progress()
                self.match_start_time = time.time()
                return

            # Double Elimination logic (simplified)
            if self.tournament_type == "Double Elimination":
                # TODO: Improve double elimination logic for losers bracket and finals
                total = len(self.photo_paths)
                if self.match_number * self.num_choices >= total:
                    remainder = total - self.match_number * self.num_choices
                    if remainder > 0:
                        self.winners.extend(self.photo_paths[-remainder:])
                    if len(self.winners) == 1:
                        self.photo_paths = self.winners.copy()
                        self.show_winner()
                        return
                    # Losers go to losers bracket
                    self.double_elim_losers.extend([p for p in self.photo_paths if p not in self.winners])
                    self.photo_paths = self.winners.copy()
                    self.round += 1
                    self.start_round()
                    return
                start = self.match_number * self.num_choices
                self.current_choices = self.photo_paths[start:start+self.num_choices]
                self.display_current_choices()
                self.match_number += 1
                self.update_info()
                self.update_progress()
                self.match_start_time = time.time()
                return

            # One Round: тільки один раунд, потім вибираємо Top N
            if self.tournament_type == "One Round":
                total = len(self.photo_paths)
                if self.match_number * self.num_choices >= total:
                    remainder = total - self.match_number * self.num_choices
                    if remainder > 0:
                        self.winners.extend(self.photo_paths[-remainder:])
                    # Top N логіка
                    if self.top_n_enabled:
                        # Підрахунок кількості перемог для кожного фото
                        win_counts = {}
                        for entry in self.match_log:
                            win_counts[entry['winner']] = win_counts.get(entry['winner'], 0) + 1
                        sorted_winners = sorted(win_counts.items(), key=lambda x: -x[1])
                        self.photo_paths = [w[0] for w in sorted_winners[:self.top_n_value]]
                    else:
                        self.photo_paths = self.winners.copy()
                    self.show_winner()
                    return
                start = self.match_number * self.num_choices
                self.current_choices = self.photo_paths[start:start+self.num_choices]
                self.display_current_choices()
                self.match_number += 1
                self.update_info()
                self.update_progress()
                self.match_start_time = time.time()
                return

            # Single Elimination and Custom
            total = len(self.photo_paths)
            if self.match_number * self.num_choices >= total:
                remainder = total - self.match_number * self.num_choices
                if remainder > 0:
                    self.winners.extend(self.photo_paths[-remainder:])
                # Top N логіка
                if self.top_n_enabled and len(self.winners) > self.top_n_value:
                    win_counts = {}
                    for entry in self.match_log:
                        win_counts[entry['winner']] = win_counts.get(entry['winner'], 0) + 1
                    sorted_winners = sorted(win_counts.items(), key=lambda x: -x[1])
                    self.photo_paths = [w[0] for w in sorted_winners[:self.top_n_value]]
                    self.show_winner()
                    return
                if len(self.winners) == 1 or (self.top_n_enabled and len(self.winners) <= self.top_n_value):
                    self.photo_paths = self.winners.copy()
                    self.show_winner()
                    return
                self.photo_paths = self.winners.copy()
                self.round += 1
                self.start_round()
                return

            start = self.match_number * self.num_choices
            self.current_choices = self.photo_paths[start:start+self.num_choices]
            self.display_current_choices()
            self.match_number += 1
            self.update_info()
            self.update_progress()
            self.match_start_time = time.time()
        except Exception as e:
            messagebox.showerror("Match Error", f"Error loading next match:\n{e}")

    def display_current_choices(self):
        """
        Displays the current set of images.
        Uses the thumbnail method to preserve aspect ratio.
        Handles exceptions if a widget is missing.
        """
        for i, path in enumerate(self.current_choices):
            try:
                if not self.image_labels[i].winfo_exists():
                    print(f"Widget for index {i} does not exist. Skipping update for this widget.")
                    continue
                img = Image.open(path)
                img.thumbnail(self.photo_size, Image.Resampling.LANCZOS)
                photo_img = ImageTk.PhotoImage(img)
                self.image_labels[i].config(image=photo_img)
                self.image_labels[i].image = photo_img  # Keep reference
                self.image_labels[i].bind("<Double-Button-1>", lambda e, p=path: self.view_original(p))
            except Exception as e:
                messagebox.showerror("Display Error", f"Failed to load image '{path}':\n{e}")

    def save_state(self):
        """
        Saves the current state for undo.
        """
        try:
            snapshot = {
                "round": self.round,
                "match_number": self.match_number,
                "winners": self.winners.copy(),
                "photo_paths": self.photo_paths.copy(),
                "current_choices": self.current_choices.copy(),
                "match_log": self.match_log.copy(),
                "stats": self.stats.copy()
            }
            self.history.append(snapshot)
        except Exception as e:
            print(f"Error saving state for undo: {e}")

    def undo(self):
        """
        Performs multi-level undo.
        """
        try:
            if not self.history:
                messagebox.showinfo("Undo", "No actions to undo.")
                return
            self.stats["num_undos"] += 1
            snapshot = self.history.pop()
            self.round = snapshot["round"]
            self.match_number = snapshot["match_number"]
            self.winners = snapshot["winners"]
            self.photo_paths = snapshot["photo_paths"]
            self.current_choices = snapshot["current_choices"]
            self.match_log = snapshot["match_log"]
            self.stats = snapshot["stats"]
            self.display_current_choices()
            self.update_info()
            self.update_progress()
        except Exception as e:
            messagebox.showerror("Undo Error", f"Error during undo:\n{e}")

    def on_key_press(self, event):
        """
        Handles key press events.
        """
        try:
            key = event.char.lower()
            if key == KEY_UNDO:
                self.undo()
            elif key == KEY_SHOW_TREE:
                self.show_tree()
            elif key == KEY_SETTINGS:
                self.open_settings()
            elif self.num_choices == 2 and key in (KEY_LEFT, KEY_RIGHT):
                self.make_choice(key)
            elif self.num_choices == 4 and key in (KEY_LEFT, KEY_RIGHT, KEY_OPTION3, KEY_OPTION4):
                self.make_choice(key)
        except Exception as e:
            print(f"Key press error: {e}")

    def make_choice(self, key):
        """
        Processes a choice based on the key pressed.
        Updates statistics and logs the result.
        """
        try:
            self.save_state()  # Save state for undo
            decision_time = time.time() - self.match_start_time
            self.stats["total_decision_time"] += decision_time
            self.stats["num_decisions"] += 1
            if key in self.stats["selection_counts"]:
                self.stats["selection_counts"][key] += 1

            # Map key to index for current_choices
            index = 0
            if self.num_choices == 2:
                index = 0 if key == KEY_LEFT else 1
            elif self.num_choices == 4:
                mapping = {KEY_LEFT: 0, KEY_RIGHT: 1, KEY_OPTION3: 2, KEY_OPTION4: 3}
                index = mapping.get(key, 0)
            winner_photo = self.current_choices[index]
            log_entry = {
                "round": self.round,
                "match": self.match_number,
                "choices": self.current_choices,
                "winner": winner_photo,
                "decision_time": decision_time
            }
            self.match_log.append(log_entry)
            self.winners.append(winner_photo)
            self.root.after(300, self.next_match)
        except Exception as e:
            messagebox.showerror("Choice Error", f"Error processing choice:\n{e}")

    def make_choice_by_index(self, index):
        """
        Processes a choice when a choice button is pressed.
        """
        try:
            if self.num_choices == 2:
                key = KEY_LEFT if index == 0 else KEY_RIGHT
            elif self.num_choices == 4:
                mapping = {0: KEY_LEFT, 1: KEY_RIGHT, 2: KEY_OPTION3, 3: KEY_OPTION4}
                key = mapping.get(index, KEY_LEFT)
            self.make_choice(key)
        except Exception as e:
            messagebox.showerror("Button Choice Error", f"Error processing button choice:\n{e}")

    def view_original(self, image_path):
        """
        Opens a new window to display the original image with zoom controls.
        """
        if not os.path.exists(image_path):
            messagebox.showerror("Error", f"File '{image_path}' not found.")
            return
        try:
            top = tk.Toplevel(self.root)
            top.title("View Original")
            img = Image.open(image_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{e}")
            return

        frame = tk.Frame(top)
        frame.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        hbar = tk.Scrollbar(top, orient=tk.HORIZONTAL, command=canvas.xview)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)

        zoom_factor = 1.0

        def update_image():
            nonlocal zoom_factor, img, canvas
            try:
                w, h = img.size
                new_size = (int(w * zoom_factor), int(h * zoom_factor))
                resized = img.resize(new_size, Image.Resampling.LANCZOS)
                photo_img = ImageTk.PhotoImage(resized)
                canvas.delete("all")
                canvas.create_image(0, 0, anchor="nw", image=photo_img)
                canvas.image = photo_img
                canvas.config(scrollregion=(0, 0, new_size[0], new_size[1]))
            except Exception as e:
                messagebox.showerror("Zoom Error", f"Failed to update zoomed image:\n{e}")

        def zoom_in():
            nonlocal zoom_factor
            zoom_factor *= 1.25
            update_image()

        def zoom_out():
            nonlocal zoom_factor
            zoom_factor /= 1.25
            update_image()

        zoom_frame = tk.Frame(top)
        zoom_frame.pack(pady=5)
        tk.Button(zoom_frame, text="Zoom In", command=zoom_in).pack(side=tk.LEFT, padx=5)
        tk.Button(zoom_frame, text="Zoom Out", command=zoom_out).pack(side=tk.LEFT, padx=5)
        update_image()

    def save_log_to_files(self):
        """
        Saves the tournament log to TXT and JSON files, with numbered winners and tree.
        """
        try:
            with open("tournament_log.txt", "w", encoding="utf-8") as f:
                f.write("Photo Tournament Log\n")
                f.write("===========================\n")
                for entry in self.match_log:
                    f.write(f"Round {entry['round']}, Match {entry['match']}: {entry['choices']} -> Winner: {entry['winner']}, Decision Time: {entry['decision_time']:.2f}s\n")
                f.write("\nWinners (Ranked):\n")
                for i, winner in enumerate(self.photo_paths):
                    f.write(f"{i+1}. {winner}\n")
                if self.photo_paths:
                    f.write("\nFinal Winner: " + self.photo_paths[0] + "\n")
            with open("tournament_log.json", "w", encoding="utf-8") as f_json:
                json.dump({
                    "matches": self.match_log,
                    "winners": self.photo_paths
                }, f_json, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Log Save Error", f"Failed to save tournament log:\n{e}")

    def append_session_history(self):
        """
        Appends the current session (match log and statistics) to the session history file.
        """
        session = {
            "timestamp": time.ctime(),
            "match_log": self.match_log,
            "stats": self.stats
        }
        history = []
        if os.path.exists(SESSION_HISTORY_FILE):
            try:
                with open(SESSION_HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception as e:
                print(f"Error reading session history: {e}")
                history = []
        history.append(session)
        try:
            with open(SESSION_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Session History Error", f"Failed to save session history:\n{e}")

    def show_tree(self):
        """
        Opens a new window displaying a simple text-based tournament tree based on the match log.
        """
        try:
            tree_win = tk.Toplevel(self.root)
            tree_win.title("Tournament Tree")
            text_area = tk.Text(tree_win, width=80, height=20)
            text_area.pack(fill=tk.BOTH, expand=True)
            tree_text = f"Tournament Tree (Round {self.round})\n"
            tree_text += "----------------------------\n"
            for entry in self.match_log:
                tree_text += f"R{entry['round']} M{entry['match']}: {entry['choices']} -> Winner: {entry['winner']}\n"
            text_area.insert(tk.END, tree_text)
        except Exception as e:
            messagebox.showerror("Tree Error", f"Error displaying tournament tree:\n{e}")

    def open_settings(self):
        """
        Opens a settings window for adjusting configuration, with advanced options.
        """
        try:
            settings_win = tk.Toplevel(self.root)
            settings_win.title("Settings")

            tk.Label(settings_win, text="Key for Left Choice:").grid(row=0, column=0, sticky="w")
            key_left_entry = tk.Entry(settings_win)
            key_left_entry.insert(0, KEY_LEFT)
            key_left_entry.grid(row=0, column=1)

            tk.Label(settings_win, text="Key for Right Choice:").grid(row=1, column=0, sticky="w")
            key_right_entry = tk.Entry(settings_win)
            key_right_entry.insert(0, KEY_RIGHT)
            key_right_entry.grid(row=1, column=1)

            if self.num_choices == 4:
                tk.Label(settings_win, text="Key for Option 3:").grid(row=2, column=0, sticky="w")
                key_opt3_entry = tk.Entry(settings_win)
                key_opt3_entry.insert(0, KEY_OPTION3)
                key_opt3_entry.grid(row=2, column=1)
                
                tk.Label(settings_win, text="Key for Option 4:").grid(row=3, column=0, sticky="w")
                key_opt4_entry = tk.Entry(settings_win)
                key_opt4_entry.insert(0, KEY_OPTION4)
                key_opt4_entry.grid(row=3, column=1)

            tk.Label(settings_win, text="Photo Size (WxH):").grid(row=4, column=0, sticky="w")
            photo_size_entry = tk.Entry(settings_win)
            photo_size_entry.insert(0, f"{self.photo_size[0]}x{self.photo_size[1]}")
            photo_size_entry.grid(row=4, column=1)

            tk.Label(settings_win, text="Final Photo Size (WxH):").grid(row=5, column=0, sticky="w")
            final_size_entry = tk.Entry(settings_win)
            final_size_entry.insert(0, f"{self.final_photo_size[0]}x{self.final_photo_size[1]}")
            final_size_entry.grid(row=5, column=1)

            tk.Label(settings_win, text="Auto-Save Interval (ms):").grid(row=6, column=0, sticky="w")
            autosave_entry = tk.Entry(settings_win)
            autosave_entry.insert(0, str(self.auto_save_interval))
            autosave_entry.grid(row=6, column=1)

            # Tournament type dropdown
            tk.Label(settings_win, text="Tournament Type:").grid(row=7, column=0, sticky="w")
            type_var = tk.StringVar(value=self.tournament_type)
            type_menu = ttk.Combobox(settings_win, textvariable=type_var, values=TOURNAMENT_TYPES)
            type_menu.grid(row=7, column=1)

            tk.Label(settings_win, text="Number of Choices per Match (2 or 4):").grid(row=8, column=0, sticky="w")
            num_choices_entry = tk.Entry(settings_win)
            num_choices_entry.insert(0, str(self.num_choices))
            num_choices_entry.grid(row=8, column=1)

            # Advanced options
            skip_var = tk.BooleanVar(value=self.allow_skip)
            tk.Checkbutton(settings_win, text="Allow Skip/Auto-Advance", variable=skip_var).grid(row=10, column=0, sticky="w")
            auto_var = tk.BooleanVar(value=self.auto_advance)
            tk.Checkbutton(settings_win, text="Auto-Advance Single Images", variable=auto_var).grid(row=11, column=0, sticky="w")
            shuffle_var = tk.BooleanVar(value=self.shuffle)
            tk.Checkbutton(settings_win, text="Shuffle Each Round", variable=shuffle_var).grid(row=12, column=0, sticky="w")
            seed_var = tk.BooleanVar(value=self.seeding)
            tk.Checkbutton(settings_win, text="Enable Seeding", variable=seed_var).grid(row=13, column=0, sticky="w")

            # Top N option
            topn_var = tk.BooleanVar(value=self.top_n_enabled)
            tk.Checkbutton(settings_win, text="Enable Top N Selection", variable=topn_var).grid(row=14, column=0, sticky="w")
            tk.Label(settings_win, text="Top N Value:").grid(row=15, column=0, sticky="w")
            topn_entry = tk.Entry(settings_win)
            topn_entry.insert(0, str(self.top_n_value))
            topn_entry.grid(row=15, column=1)

            def save_settings():
                global KEY_LEFT, KEY_RIGHT, KEY_OPTION3, KEY_OPTION4
                KEY_LEFT = key_left_entry.get().lower()
                KEY_RIGHT = key_right_entry.get().lower()
                if self.num_choices == 4:
                    KEY_OPTION3 = key_opt3_entry.get().lower()
                    KEY_OPTION4 = key_opt4_entry.get().lower()
                try:
                    w, h = map(int, photo_size_entry.get().lower().split("x"))
                    self.photo_size = (w, h)
                    fw, fh = map(int, final_size_entry.get().lower().split("x"))
                    self.final_photo_size = (fw, fh)
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid size format: {e}")
                try:
                    self.auto_save_interval = int(autosave_entry.get())
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid auto-save interval: {e}")
                self.tournament_type = type_var.get()
                # TODO: Validate and handle custom tournament type settings
                try:
                    new_num = int(num_choices_entry.get())
                    if new_num in (2, 4):
                        self.num_choices = new_num
                    else:
                        messagebox.showerror("Error", "Number of choices must be 2 or 4.")
                except Exception as e:
                    messagebox.showerror("Error", f"Invalid number of choices: {e}")
                self.allow_skip = skip_var.get()
                self.auto_advance = auto_var.get()
                self.shuffle = shuffle_var.get()
                self.seeding = seed_var.get()
                self.top_n_enabled = topn_var.get()
                try:
                    self.top_n_value = int(topn_entry.get())
                    if self.top_n_value < 1:
                        self.top_n_value = 1
                except Exception:
                    self.top_n_value = 1
                settings = {
                    "KEY_LEFT": KEY_LEFT,
                    "KEY_RIGHT": KEY_RIGHT,
                    "KEY_OPTION3": KEY_OPTION3,
                    "KEY_OPTION4": KEY_OPTION4,
                    "photo_size": self.photo_size,
                    "final_photo_size": self.final_photo_size,
                    "auto_save_interval": self.auto_save_interval,
                    "tournament_type": self.tournament_type,
                    "num_choices": self.num_choices,
                    "top_n_enabled": self.top_n_enabled,
                    "top_n_value": self.top_n_value
                }
                try:
                    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                        json.dump(settings, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export settings: {e}")
                messagebox.showinfo("Settings", "Settings saved successfully. Restart tournament for changes to take effect.")
                settings_win.destroy()
            tk.Button(settings_win, text="Save Settings", command=save_settings).grid(row=16, column=0, pady=5)
            tk.Button(settings_win, text="Import Settings", command=self.import_settings).grid(row=16, column=1, pady=5)
        except Exception as e:
            messagebox.showerror("Settings Error", f"Error opening settings:\n{e}")

    def import_settings(self):
        """
        Imports settings from the settings file.
        """
        global KEY_LEFT, KEY_RIGHT, KEY_OPTION3, KEY_OPTION4
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                KEY_LEFT = settings.get("KEY_LEFT", KEY_LEFT)
                KEY_RIGHT = settings.get("KEY_RIGHT", KEY_RIGHT)
                KEY_OPTION3 = settings.get("KEY_OPTION3", KEY_OPTION3)
                KEY_OPTION4 = settings.get("KEY_OPTION4", KEY_OPTION4)
                self.photo_size = tuple(settings.get("photo_size", self.photo_size))
                self.final_photo_size = tuple(settings.get("final_photo_size", self.final_photo_size))
                self.auto_save_interval = settings.get("auto_save_interval", self.auto_save_interval)
                self.tournament_type = settings.get("tournament_type", self.tournament_type)
                self.num_choices = settings.get("num_choices", self.num_choices)
                self.top_n_enabled = settings.get("top_n_enabled", False)
                self.top_n_value = settings.get("top_n_value", 1)
                messagebox.showinfo("Settings", "Settings imported successfully. Restart tournament for changes to take effect.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import settings: {e}")
        else:
            messagebox.showinfo("Settings", "No settings file found.")

    def show_log_window(self):
        """
        Opens a window to view the tournament log and numbered winners.
        """
        try:
            if self.log_window and tk.Toplevel.winfo_exists(self.log_window):
                self.log_window.lift()
                return
            self.log_window = tk.Toplevel(self.root)
            self.log_window.title("Tournament Log & Winners")
            text_area = tk.Text(self.log_window, width=100, height=30)
            text_area.pack(fill=tk.BOTH, expand=True)
            # Build log text
            log_text = "Tournament Log\n====================\n"
            for idx, entry in enumerate(self.match_log):
                log_text += f"Round {entry['round']}, Match {entry['match']}: {entry['choices']} -> Winner: {entry['winner']} (Time: {entry['decision_time']:.2f}s)\n"
            log_text += "\nWinners (Ranked):\n-----------------\n"
            for i, winner in enumerate(self.photo_paths):
                log_text += f"{i+1}. {winner}\n"
            text_area.insert(tk.END, log_text)
            # TODO: Add export button for log or advanced log filtering
        except Exception as e:
            messagebox.showerror("Log Error", f"Failed to show log:\n{e}")

    def show_winner(self):
        """
        Displays the final winning image, saves the log, and appends the session history.
        Also generates a detailed log with numbered winners and tree.
        """
        try:
            for widget in self.root.winfo_children():
                widget.destroy()
            winner = self.photo_paths[0]
            img = Image.open(winner)
            img = img.resize(self.final_photo_size)
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(self.root, image=photo)
            lbl.image = photo
            lbl.pack(pady=10)
            tk.Label(self.root, text="Best Photo", font=("Arial", 20)).pack(pady=10)
            tk.Button(self.root, text="Restart", font=("Arial", 14), command=self.restart).pack(pady=10)
            self.save_log_to_files()
            self.append_session_history()
            # Show log window automatically
            self.show_log_window()
            # TODO: Add option to export/share winner or results
        except Exception as e:
            messagebox.showerror("Winner Error", f"Failed to load final image:\n{e}")

    def restart(self):
        """
        Restarts the tournament.
        """
        try:
            self.photo_paths = self.all_photos.copy()
            for widget in self.root.winfo_children():
                widget.destroy()
            self.build_ui()
            self.round = 1
            self.match_number = 0
            self.winners = []
            self.history.clear()
            self.match_log.clear()
            self.stats = {
                "total_decision_time": 0.0,
                "num_decisions": 0,
                "num_undos": 0,
                "selection_counts": {KEY_LEFT: 0, KEY_RIGHT: 0, KEY_OPTION3: 0, KEY_OPTION4: 0}
            }
            # TODO: Reset additional state if new features are added
            self.start_round()
        except Exception as e:
            messagebox.showerror("Restart Error", f"Failed to restart tournament:\n{e}")

# ------------------------------
# ===== Program Startup =====
# ------------------------------

if __name__ == "__main__":
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
