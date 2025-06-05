import os
import random
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import json
import time

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
FINAL_PHOTO_SIZE = (500, 500)     # Size for the final image

# Progress bar settings
PROGRESS_BAR_LENGTH = 300         # Length of progress bar

# Auto-save settings
AUTO_SAVE_INTERVAL = 30000        # Auto-save interval in milliseconds (30 seconds)
# Зберігаємо файл автозбереження у домашню директорію, де є права на запис.
AUTO_SAVE_FILE = os.path.join(os.path.expanduser("~"), "autosave_state.json")

# Tournament settings defaults
DEFAULT_TOURNAMENT_TYPE = "Single Elimination"  # (stub: "Round Robin" може бути додано)
DEFAULT_NUM_CHOICES = 2                         # Кількість варіантів вибору (2 або 4)

# Settings file for export/import
SETTINGS_FILE = "tournament_settings.json"

# Session history file
SESSION_HISTORY_FILE = "session_history.json"

# ------------------------------
# ===== Main Application Class =====
# ------------------------------

class PhotoTournament:
    def __init__(self, root, photo_paths):
        """
        Ініціалізація турніру.
        """
        self.root = root
        self.root.title("Photo Tournament")
        
        # Завантаження лише валідних зображень
        self.all_photos = self.load_valid_images(photo_paths)
        if len(self.all_photos) < 2:
            messagebox.showerror("Error", "Not enough valid photos for the tournament.")
            self.root.destroy()
            return
        self.photo_paths = self.all_photos.copy()
        
        # Налаштування програми (можна змінювати через панель налаштувань)
        self.photo_size = PHOTO_SIZE
        self.final_photo_size = FINAL_PHOTO_SIZE
        self.progress_length = PROGRESS_BAR_LENGTH
        self.auto_save_interval = AUTO_SAVE_INTERVAL
        self.tournament_type = DEFAULT_TOURNAMENT_TYPE
        self.num_choices = DEFAULT_NUM_CHOICES  # 2 або 4 варіанти вибору
        
        # Статистика для аналізу матчів
        self.stats = {
            "total_decision_time": 0.0,
            "num_decisions": 0,
            "num_undos": 0,
            "selection_counts": {KEY_LEFT: 0, KEY_RIGHT: 0, KEY_OPTION3: 0, KEY_OPTION4: 0}
        }
        self.match_start_time = time.time()

        # Стан турніру
        self.round = 1
        self.match_number = 0
        self.winners = []
        self.current_choices = []  # Список зображень для поточного матчу (довжина = num_choices)
        self.history = []          # Список для збереження стану (для багаторівневого undo)
        self.match_log = []        # Журнал всіх матчів
        
        # Побудова інтерфейсу
        self.build_ui()
        
        # Прив'язка подій: автоматичне збереження при закритті та зміна розміру вікна
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<Configure>", self.on_resize)
        self.last_width = self.root.winfo_width()
        
        # Перевірка наявності збереженого стану і пропозиція відновлення
        self.check_for_saved_state()
        
        # Прив'язка клавіш для швидкого управління
        self.root.bind("<Key>", self.on_key_press)
        
        # Запуск таймера автозбереження
        self.schedule_autosave()
        
        # Запуск першого раунду турніру
        self.start_round()

    def load_valid_images(self, photo_paths):
        """
        Повертає список валідних шляхів до зображень, перевіряючи можливість їх відкриття.
        """
        valid = []
        for path in photo_paths:
            try:
                with Image.open(path) as img:
                    img.verify()
                valid.append(path)
            except Exception:
                continue
        return valid

    def build_ui(self):
        """
        Створення основних фреймів та віджетів.
        """
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=5)
        self.middle_frame = tk.Frame(self.root)
        self.middle_frame.pack()
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(pady=5)

        # Інформаційна метка та progress bar
        self.info_label = tk.Label(self.top_frame, text="", font=("Arial", 14))
        self.info_label.pack()
        self.progress = ttk.Progressbar(self.top_frame, orient="horizontal", length=self.progress_length, mode="determinate")
        self.progress.pack(pady=5)

        # Віджети для відображення зображень (залежно від num_choices)
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

        # Кнопки для вибору
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

        # Додаткові кнопки управління
        self.undo_button = tk.Button(self.bottom_frame, text=f"Undo ({KEY_UNDO.upper()})", command=self.undo)
        self.undo_button.pack(side=tk.LEFT, padx=5)
        self.tree_button = tk.Button(self.bottom_frame, text="Show Tournament Tree (T)", command=self.show_tree)
        self.tree_button.pack(side=tk.LEFT, padx=5)
        self.settings_button = tk.Button(self.bottom_frame, text="Settings (S)", command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT, padx=5)
        self.restart_button = tk.Button(self.bottom_frame, text="Restart", command=self.restart)
        self.restart_button.pack(side=tk.LEFT, padx=5)

    def on_resize(self, event):
        """
        Викликається при зміні розміру вікна.
        Динамічно масштабує зображення, зберігаючи пропорції.
        """
        if event.widget == self.root:
            if abs(event.width - self.last_width) > 50:
                self.last_width = event.width
                scale = event.width / 800  # базовий розмір 800
                new_width = int(PHOTO_SIZE[0] * scale)
                new_height = int(PHOTO_SIZE[1] * scale)
                self.photo_size = (new_width, new_height)
                self.display_current_choices()

    def on_close(self):
        """
        Викликається при закритті вікна.
        Автоматично зберігає стан і завершує роботу.
        """
        self.auto_save()
        self.root.destroy()

    def schedule_autosave(self):
        """
        Запускає виклик функції автозбереження через заданий інтервал.
        """
        self.root.after(self.auto_save_interval, self.auto_save)

    def auto_save(self):
        """
        Автоматично зберігає поточний стан турніру у JSON файл.
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
            # print("Auto-saved state.")
        except Exception as e:
            messagebox.showerror("Error", f"Auto-save failed:\n{e}")
        self.schedule_autosave()

    def check_for_saved_state(self):
        """
        Якщо існує файл автозбереження, пропонує відновити сесію.
        """
        if os.path.exists(AUTO_SAVE_FILE):
            if messagebox.askyesno("Restore Session", "A saved session was found. Do you want to restore it?"):
                try:
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
                    messagebox.showinfo("Info", "Session restored successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to restore session:\n{e}")

    def start_round(self):
        """
        Готує та запускає новий раунд.
        """
        if self.tournament_type == "Single Elimination":
            random.shuffle(self.photo_paths)
        self.match_number = 0
        self.winners = []
        self.history.clear()
        self.update_info()
        self.update_progress()
        self.next_match()

    def update_info(self):
        """
        Оновлює інформаційну метку з поточним раундом та номером матчу.
        """
        total_matches = len(self.photo_paths) // self.num_choices
        text = f"Round {self.round} | Match {self.match_number+1} of {total_matches}"
        self.info_label.config(text=text)

    def update_progress(self):
        """
        Оновлює progress bar.
        """
        total_matches = len(self.photo_paths) // self.num_choices
        value = (self.match_number / total_matches) * 100 if total_matches else 100
        self.progress['value'] = value
        self.root.update_idletasks()

    def next_match(self):
        """
        Завантажує наступний набір зображень для поточного матчу.
        """
        total = len(self.photo_paths)
        if self.match_number * self.num_choices >= total:
            remainder = total - self.match_number * self.num_choices
            if remainder > 0:
                self.winners.extend(self.photo_paths[-remainder:])
                messagebox.showinfo("Info", "Remaining images automatically advance to the next round.")
            if len(self.winners) == 1:
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

    def display_current_choices(self):
        """
        Відображає поточний набір зображень.
        Зберігає оригінальні пропорції за допомогою методу thumbnail.
        Також при подвійному кліку відкриває оригінальне зображення у новому вікні.
        """
        for i, path in enumerate(self.current_choices):
            try:
                img = Image.open(path)
                # Використовуємо метод thumbnail для збереження аспектного співвідношення.
                img.thumbnail(self.photo_size, Image.Resampling.LANCZOS)
                photo_img = ImageTk.PhotoImage(img)
                self.image_labels[i].config(image=photo_img)
                self.image_labels[i].image = photo_img
                self.image_labels[i].bind("<Double-Button-1>", lambda e, p=path: self.view_original(p))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image {path}:\n{e}")

    def save_state(self):
        """
        Зберігає поточний стан для undo.
        """
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

    def undo(self):
        """
        Виконує багаторівневу відміну.
        """
        if not self.history:
            messagebox.showinfo("Info", "No actions to undo.")
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

    def on_key_press(self, event):
        """
        Обробляє натискання клавіш.
        """
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

    def make_choice(self, key):
        """
        Обробляє вибір за натисканням клавіші, оновлює статистику та зберігає результат.
        """
        self.save_state()
        decision_time = time.time() - self.match_start_time
        self.stats["total_decision_time"] += decision_time
        self.stats["num_decisions"] += 1
        if key in self.stats["selection_counts"]:
            self.stats["selection_counts"][key] += 1

        # Визначаємо індекс вибору
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

    def make_choice_by_index(self, index):
        """
        Обробляє вибір при натисканні кнопки.
        """
        if self.num_choices == 2:
            key = KEY_LEFT if index == 0 else KEY_RIGHT
        elif self.num_choices == 4:
            mapping = {0: KEY_LEFT, 1: KEY_RIGHT, 2: KEY_OPTION3, 3: KEY_OPTION4}
            key = mapping.get(index, KEY_LEFT)
        self.make_choice(key)

    def view_original(self, image_path):
        """
        Відкриває нове вікно для перегляду оригінального зображення з можливістю масштабування.
        """
        if not os.path.exists(image_path):
            messagebox.showerror("Error", f"File {image_path} not found.")
            return
        top = tk.Toplevel(self.root)
        top.title("View Original")
        try:
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
            w, h = img.size
            new_size = (int(w * zoom_factor), int(h * zoom_factor))
            resized = img.resize(new_size, Image.Resampling.LANCZOS)
            photo_img = ImageTk.PhotoImage(resized)
            canvas.delete("all")
            canvas.create_image(0, 0, anchor="nw", image=photo_img)
            canvas.image = photo_img
            canvas.config(scrollregion=(0, 0, new_size[0], new_size[1]))

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
        Зберігає журнал турніру у TXT та JSON файли.
        """
        try:
            with open("tournament_log.txt", "w", encoding="utf-8") as f:
                f.write("Photo Tournament Log\n")
                f.write("===========================\n")
                for entry in self.match_log:
                    f.write(f"Round {entry['round']}, Match {entry['match']}: {entry['choices']} -> Winner: {entry['winner']}, Decision Time: {entry['decision_time']:.2f}s\n")
                if self.photo_paths:
                    f.write("\nFinal Winner: " + self.photo_paths[0] + "\n")
            with open("tournament_log.json", "w", encoding="utf-8") as f_json:
                json.dump(self.match_log, f_json, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tournament log:\n{e}")

    def append_session_history(self):
        """
        Додає поточну сесію (журнал матчів та статистику) до файлу історії сесій.
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
            except Exception:
                history = []
        history.append(session)
        try:
            with open(SESSION_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save session history:\n{e}")

    def show_tree(self):
        """
        Відкриває нове вікно, що відображає просте текстове представлення дерева турніру.
        """
        tree_win = tk.Toplevel(self.root)
        tree_win.title("Tournament Tree")
        text_area = tk.Text(tree_win, width=80, height=20)
        text_area.pack(fill=tk.BOTH, expand=True)
        tree_text = f"Tournament Tree (Round {self.round})\n"
        tree_text += "----------------------------\n"
        for entry in self.match_log:
            tree_text += f"R{entry['round']} M{entry['match']}: {entry['choices']} -> Winner: {entry['winner']}\n"
        text_area.insert(tk.END, tree_text)

    def open_settings(self):
        """
        Відкриває вікно налаштувань для зміни конфігурації.
        """
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

        tk.Label(settings_win, text="Tournament Type:").grid(row=7, column=0, sticky="w")
        type_var = tk.StringVar(value=self.tournament_type)
        type_menu = ttk.Combobox(settings_win, textvariable=type_var, values=["Single Elimination", "Round Robin"])
        type_menu.grid(row=7, column=1)

        tk.Label(settings_win, text="Number of Choices per Match (2 or 4):").grid(row=8, column=0, sticky="w")
        num_choices_entry = tk.Entry(settings_win)
        num_choices_entry.insert(0, str(self.num_choices))
        num_choices_entry.grid(row=8, column=1)

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
            try:
                new_num = int(num_choices_entry.get())
                if new_num in (2, 4):
                    self.num_choices = new_num
                else:
                    messagebox.showerror("Error", "Number of choices must be 2 or 4.")
            except Exception as e:
                messagebox.showerror("Error", f"Invalid number of choices: {e}")
            settings = {
                "KEY_LEFT": KEY_LEFT,
                "KEY_RIGHT": KEY_RIGHT,
                "KEY_OPTION3": KEY_OPTION3,
                "KEY_OPTION4": KEY_OPTION4,
                "photo_size": self.photo_size,
                "final_photo_size": self.final_photo_size,
                "auto_save_interval": self.auto_save_interval,
                "tournament_type": self.tournament_type,
                "num_choices": self.num_choices
            }
            try:
                with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                    json.dump(settings, f, ensure_ascii=False, indent=4)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export settings: {e}")
            messagebox.showinfo("Settings", "Settings saved successfully. Restart tournament for changes to take effect.")
            settings_win.destroy()
        tk.Button(settings_win, text="Save Settings", command=save_settings).grid(row=9, column=0, pady=5)
        tk.Button(settings_win, text="Import Settings", command=self.import_settings).grid(row=9, column=1, pady=5)

    def import_settings(self):
        """
        Імпортує налаштування з файлу.
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
                messagebox.showinfo("Settings", "Settings imported successfully. Restart tournament for changes to take effect.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import settings: {e}")
        else:
            messagebox.showinfo("Settings", "No settings file found.")

    def show_winner(self):
        """
        Відображає фінальне зображення-переможця, зберігає журнал турніру та додає сесійну історію.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
        winner = self.photo_paths[0]
        try:
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
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load final image:\n{e}")

    def restart(self):
        """
        Перезапускає турнір.
        """
        self.photo_paths = self.all_photos.copy()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.build_ui()
        self.round = 1
        self.match_number = 0
        self.winners = []
        self.history.clear()
        self.match_log.clear()
        self.stats = {"total_decision_time": 0.0, "num_decisions": 0, "num_undos": 0, 
                      "selection_counts": {KEY_LEFT: 0, KEY_RIGHT: 0, KEY_OPTION3: 0, KEY_OPTION4: 0}}
        self.start_round()

# ------------------------------
# ===== Program Startup =====
# ------------------------------

if __name__ == "__main__":
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
