import os
import random
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import json
import time
import datetime

KEY_LEFT = 'd'
KEY_RIGHT = 'f'
KEY_OPTION3 = 'j'
KEY_OPTION4 = 'k'
KEY_UNDO = 'z'
KEY_SHOW_TREE = 't'
KEY_SETTINGS = 's'
PHOTO_SIZE = (300, 300)
FINAL_PHOTO_SIZE = (500, 500)
PROGRESS_BAR_LENGTH = 300
AUTO_SAVE_INTERVAL = 5000
AUTO_SAVE_FILE = os.path.join(os.path.expanduser("~"), "autosave_state.json")
EMERGENCY_SAVE_FOLDER = os.path.join(os.path.expanduser("~"), "EmergencySaves")
if not os.path.exists(EMERGENCY_SAVE_FOLDER):
    try:
        os.makedirs(EMERGENCY_SAVE_FOLDER)
    except Exception as e:
        print(f"Error creating emergency save folder: {e}")
DEFAULT_TOURNAMENT_TYPE = "Single Elimination"
DEFAULT_NUM_CHOICES = 2
SETTINGS_FILE = "tournament_settings.json"
SESSION_HISTORY_FILE = "session_history.json"
TOURNAMENT_TYPES = [
    "Single Elimination",
    "Double Elimination",
    "Round Robin",
    "One Round",
    "Custom"
]

class PhotoTournament:
    def __init__(self, root, photo_paths):
        self.root = root
        self.root.title("Photo Tournament")
        self.all_photos = self.load_valid_images(photo_paths)
        if len(self.all_photos) < 2:
            messagebox.showerror("Error", "Not enough valid photos for the tournament.")
            self.root.destroy()
            return
        self.photo_paths = self.all_photos.copy()
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
        self.round_robin_matches = []
        self.double_elim_losers = []
        self.finalists = []
        self.log_window = None
        self.top_n_enabled = False
        self.top_n_value = 1
        self.stats = {
            "total_decision_time": 0.0,
            "num_decisions": 0,
            "num_undos": 0,
            "selection_counts": {KEY_LEFT: 0, KEY_RIGHT: 0, KEY_OPTION3: 0, KEY_OPTION4: 0}
        }
        self.match_start_time = time.time()
        self.round = 1
        self.match_number = 0
        self.winners = []
        self.current_choices = []
        self.history = []
        self.match_log = []
        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<Configure>", self.on_resize)
        self.last_width = self.root.winfo_width()
        self.check_for_saved_state()
        self.root.bind("<Key>", self.on_key_press)
        self.schedule_autosave()
        self.start_round()

    def load_valid_images(self, photo_paths):
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
        self.photo_frame = ttk.Frame(self.root)
        self.photo_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.progress_frame = ttk.Frame(self.root)
        self.progress_frame.pack(side=tk.TOP, fill=tk.X)

        self.info_frame = ttk.Frame(self.root)
        self.info_frame.pack(side=tk.TOP, fill=tk.X)

        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        self.canvas = tk.Canvas(self.photo_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.photo_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.progress = ttk.Progressbar(self.progress_frame, length=self.progress_length)
        self.progress.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.info_label = ttk.Label(self.info_frame, text="", anchor=tk.W)
        self.info_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        self.round_label = ttk.Label(self.info_frame, text="Round: 1", anchor=tk.W)
        self.round_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        self.match_label = ttk.Label(self.info_frame, text="Match: 1", anchor=tk.W)
        self.match_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        self.save_button = ttk.Button(self.button_frame, text="Save", command=self.manual_save)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.undo_button = ttk.Button(self.button_frame, text="Undo", command=self.undo)
        self.undo_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.settings_button = ttk.Button(self.button_frame, text="Settings", command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.quit_button = ttk.Button(self.button_frame, text="Quit", command=self.on_close)
        self.quit_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.root.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        if self.last_width == self.root.winfo_width():
            return
        self.last_width = self.root.winfo_width()
        self.update_photo_display()

    def on_close(self):
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            self.root.destroy()

    def schedule_autosave(self):
        self.root.after(self.auto_save_interval, self.auto_save)

    def auto_save(self):
        try:
            state = {
                "round": self.round,
                "match_number": self.match_number,
                "winners": self.winners,
                "photo_paths": self.photo_paths,
                "current_choices": self.current_choices,
                "match_log": self.match_log,
                "stats": self.stats
            }
            with open(AUTO_SAVE_FILE, "w") as f:
                json.dump(state, f)
        except Exception as e:
            print(f"Error during auto-save: {e}")
        self.schedule_autosave()

    def manual_save(self):
        try:
            state = {
                "round": self.round,
                "match_number": self.match_number,
                "winners": self.winners,
                "photo_paths": self.photo_paths,
                "current_choices": self.current_choices,
                "match_log": self.match_log,
                "stats": self.stats
            }
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if file_path:
                with open(file_path, "w") as f:
                    json.dump(state, f)
                messagebox.showinfo("Save", "Tournament state saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving state: {e}")

    def check_for_saved_state(self):
        if os.path.exists(AUTO_SAVE_FILE):
            try:
                with open(AUTO_SAVE_FILE, "r") as f:
                    state = json.load(f)
                    self.round = state.get("round", 1)
                    self.match_number = state.get("match_number", 0)
                    self.winners = state.get("winners", [])
                    self.photo_paths = state.get("photo_paths", self.photo_paths)
                    self.current_choices = state.get("current_choices", [])
                    self.match_log = state.get("match_log", [])
                    self.stats = state.get("stats", self.stats)
            except Exception as e:
                print(f"Error loading saved state: {e}")

    def start_round(self):
        if self.tournament_type == "Single Elimination":
            self.start_single_elimination()
        elif self.tournament_type == "Double Elimination":
            self.start_double_elimination()
        elif self.tournament_type == "Round Robin":
            self.start_round_robin()
        elif self.tournament_type == "One Round":
            self.start_one_round()
        elif self.tournament_type == "Custom":
            self.start_custom_bracket()

    def start_single_elimination(self):
        self.round = 1
        self.match_number = 0
        self.winners = []
        self.history.clear()
        self.next_match()

    def start_double_elimination(self):
        self.round = 1
        self.match_number = 0
        self.winners = []
        self.history.clear()
        self.next_match()

    def start_round_robin(self):
        self.round = 1
        self.match_number = 0
        self.winners = []
        self.history.clear()
        self.next_match()

    def start_one_round(self):
        self.round = 1
        self.match_number = 0
        self.winners = []
        self.history.clear()
        self.next_match()

    def start_custom_bracket(self):
        self.round = 1
        self.match_number = 0
        self.winners = []
        self.history.clear()
        self.next_match()

    def update_info(self):
        self.round_label.config(text=f"Round: {self.round}")
        self.match_label.config(text=f"Match: {self.match_number}")

    def update_progress(self):
        progress = (self.match_number / len(self.photo_paths)) * 100
        self.progress['value'] = progress

    def next_match(self):
        if self.match_number * 2 >= len(self.photo_paths):
            self.show_winner()
            return
        self.current_choices = self.photo_paths[self.match_number * 2:self.match_number * 2 + 2]
        self.display_current_choices()
        self.update_info()
        self.update_progress()
        self.match_number += 1
        self.match_start_time = time.time()

    def display_current_choices(self):
        for widget in self.photo_frame.winfo_children():
            widget.destroy()

        for i, photo_path in enumerate(self.current_choices):
            try:
                img = Image.open(photo_path)
                img.thumbnail(self.photo_size, Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(img)

                panel = ttk.Label(self.photo_frame, image=photo)
                panel.image = photo
                panel.grid(row=0, column=i, padx=5, pady=5)

                info = ttk.Label(self.photo_frame, text=os.path.basename(photo_path))
                info.grid(row=1, column=i, padx=5, pady=5)
            except Exception as e:
                print(f"Error displaying image {photo_path}: {e}")

    def save_state(self):
        state = {
            "round": self.round,
            "match_number": self.match_number,
            "winners": self.winners,
            "photo_paths": self.photo_paths,
            "current_choices": self.current_choices,
            "match_log": self.match_log,
            "stats": self.stats
        }
        with open("tournament_state.json", "w") as f:
            json.dump(state, f)

    def undo(self):
        if not self.match_log:
            return
        last_match = self.match_log.pop()
        self.round = last_match["round"]
        self.match_number = last_match["match"]
        self.winners = self.winners[:-1]
        self.photo_paths = self.photo_paths[:len(self.winners) * 2]
        self.current_choices = self.photo_paths[self.match_number * 2:self.match_number * 2 + 2]
        self.display_current_choices()
        self.update_info()
        self.update_progress()

    def on_key_press(self, event):
        key = event.char
        if key == KEY_UNDO:
            self.undo()
        elif key == KEY_SETTINGS:
            self.open_settings()
        elif key == KEY_SHOW_TREE:
            self.show_tree()
        elif key in [KEY_LEFT, KEY_RIGHT, KEY_OPTION3, KEY_OPTION4]:
            self.make_choice(key)

    def make_choice(self, key):
        if key == KEY_LEFT:
            self.make_choice_by_index(0)
        elif key == KEY_RIGHT:
            self.make_choice_by_index(1)
        elif key == KEY_OPTION3:
            self.make_choice_by_index(2)
        elif key == KEY_OPTION4:
            self.make_choice_by_index(3)

    def make_choice_by_index(self, index):
        winner_photo = self.current_choices[index]
        self.winners.append(winner_photo)
        self.match_log.append({
            "round": self.round,
            "match": self.match_number,
            "winner": winner_photo
        })
        self.next_match()

    def view_original(self, image_path):
        try:
            img = Image.open(image_path)
            img.show()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open original image: {e}")

    def save_log_to_files(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(EMERGENCY_SAVE_FOLDER, f"log_{timestamp}.json")
            with open(log_file, "w") as f:
                json.dump(self.match_log, f)
            messagebox.showinfo("Log Saved", f"Match log saved to:\n{log_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving log: {e}")

    def append_session_history(self):
        try:
            if os.path.exists(SESSION_HISTORY_FILE):
                with open(SESSION_HISTORY_FILE, "r") as f:
                    history = json.load(f)
            else:
                history = []

            history.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "round": self.round,
                "match_number": self.match_number,
                "winners": self.winners,
                "photo_paths": self.photo_paths,
                "current_choices": self.current_choices,
                "match_log": self.match_log,
                "stats": self.stats
            })

            with open(SESSION_HISTORY_FILE, "w") as f:
                json.dump(history, f)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving session history: {e}")

    def show_tree(self):
        # Tree view implementation here
        pass

    def open_settings(self):
        # Settings window implementation here
        pass

    def import_settings(self):
        # Import settings implementation here
        pass

    def show_log_window(self):
        # Log window implementation here
        pass

    def show_winner(self):
        if self.winners:
            winner = self.winners[0]
            messagebox.showinfo("Tournament Winner", f"The winner is: {winner}")

    def restart(self):
        if messagebox.askokcancel("Restart", "Do you really want to restart the tournament?"):
            self.round = 1
            self.match_number = 0
            self.winners = []
            self.current_choices = []
            self.history = []
            self.match_log = []
            self.start_round()