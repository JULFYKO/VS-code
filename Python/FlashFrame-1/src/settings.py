from pathlib import Path

# Quick Settings
KEY_LEFT = 'd'
KEY_RIGHT = 'f'
KEY_OPTION3 = 'j'
KEY_OPTION4 = 'k'
KEY_UNDO = 'z'
KEY_SHOW_TREE = 't'
KEY_SETTINGS = 's'

# Image sizes and layout
PHOTO_SIZE = (300, 300)
FINAL_PHOTO_SIZE = (500, 500)

# Progress bar settings
PROGRESS_BAR_LENGTH = 300

# Auto-save settings
AUTO_SAVE_INTERVAL = 5000
AUTO_SAVE_FILE = Path.home() / "autosave_state.json"

# Emergency folder for manual/critical saves
EMERGENCY_SAVE_FOLDER = Path.home() / "EmergencySaves"
EMERGENCY_SAVE_FOLDER.mkdir(exist_ok=True)

# Tournament settings defaults
DEFAULT_TOURNAMENT_TYPE = "Single Elimination"
DEFAULT_NUM_CHOICES = 2

# Settings file for export/import
SETTINGS_FILE = "tournament_settings.json"

# Session history file
SESSION_HISTORY_FILE = "session_history.json"

# Add new tournament types and settings
TOURNAMENT_TYPES = [
    "Single Elimination",
    "Double Elimination",
    "Round Robin",
    "One Round",
    "Custom"
]