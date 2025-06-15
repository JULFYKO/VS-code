import os
import json
from PIL import Image

def load_valid_images(photo_paths):
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

def save_to_json(data, file_path):
    """
    Saves data to a JSON file.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_from_json(file_path):
    """
    Loads data from a JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def create_emergency_save_folder(folder_path):
    """
    Creates an emergency save folder if it does not exist.
    """
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
        except Exception as e:
            print(f"Error creating emergency save folder: {e}")