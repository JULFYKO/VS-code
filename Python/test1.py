#!/usr/bin/env python3
import sys
import argparse
import os
import logging
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageOps, ImageFilter
import pytesseract
import pyperclip

def preprocess_image(img: Image.Image, 
                     to_grayscale: bool = True,
                     auto_contrast: bool = True,
                     denoise: bool = True) -> Image.Image:
    """
    Застосовує базову обробку до зображення для покращення OCR:
      1) Переводить у відтінки сірого
      2) Автоконтраст
      3) Згладжує дрібний шум

    :param img: вхідний PIL Image
    :return: оброблене зображення
    """
    if to_grayscale:
        img = img.convert("L")
    if auto_contrast:
        img = ImageOps.autocontrast(img)
    if denoise:
        img = img.filter(ImageFilter.MedianFilter(size=3))
    return img

def ocr_image_to_text(image_path: Path, langs: str) -> str:
    """
    Розпізнає текст із зображення, застосовуючи препроцесінг та Tesseract.
    :param image_path: шлях до зображення
    :param langs: рядок з мовами для Tesseract (наприклад: 'ukr+eng')
    :return: отриманий текст
    """
    logging.debug(f"Відкриваємо зображення: {image_path}")
    img = Image.open(image_path)
    img = preprocess_image(img)
    logging.debug("Запускаємо OCR...")
    text = pytesseract.image_to_string(img, lang=langs)
    return text

def copy_to_clipboard(text: str) -> None:
    """
    Копіює текст у системний буфер обміну.
    """
    pyperclip.copy(text)
    logging.info("Текст скопійовано в буфер обміну.")

def select_image_file() -> Path:
    """
    Відкриває діалогове вікно для вибору зображення.
    :return: Path до вибраного файлу або None, якщо не вибрано.
    """
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Оберіть зображення для OCR",
        filetypes=[("Зображення", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.tif"), ("Всі файли", "*.*")]
    )
    root.destroy()
    if not file_path:
        return None
    return Path(file_path)

def parse_args():
    p = argparse.ArgumentParser(
        description="OCR: зображення → текст → буфер обміну"
    )
    p.add_argument("image", type=Path, nargs="?",
                   help="Шлях до зображення (jpg/png/...). Якщо не вказано — відкриється діалог вибору.")
    p.add_argument("-l", "--langs", default="ukr+eng",
                   help="Мови для OCR (наприклад: 'ukr+eng').")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="Більш докладний вихід у консоль.")
    return p.parse_args()

def setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s",
        level=level, datefmt="%H:%M:%S"
    )

def show_text_window(text: str):
    """
    Відкриває вікно з текстом та кнопкою для копіювання в буфер.
    """
    def copy_action():
        pyperclip.copy(text)
        btn_copy.config(text="Скопійовано!", state="disabled")
        root.after(1500, lambda: (btn_copy.config(text="Копіювати", state="normal")))

    root = tk.Tk()
    root.title("Результат OCR")
    root.geometry("600x400")

    txt = tk.Text(root, wrap="word")
    txt.insert("1.0", text)
    txt.config(state="disabled")
    txt.pack(expand=True, fill="both", padx=10, pady=10)

    btn_copy = tk.Button(root, text="Копіювати", command=copy_action)
    btn_copy.pack(pady=(0, 10))

    root.mainloop()

def main():
    args = parse_args()
    setup_logging(args.verbose)

    image_path = args.image
    if image_path is None:
        image_path = select_image_file()
        if image_path is None:
            logging.info("Файл не вибрано. Вихід.")
            sys.exit(0)

    if not image_path.exists():
        logging.error(f"Файл не знайдено: {image_path}")
        sys.exit(1)
    try:
        text = ocr_image_to_text(image_path, args.langs)
        if not text.strip():
            logging.warning("OCR повернув порожній результат.")
        else:
            show_text_window(text)
            # print(text)  # За потреби можна залишити для консольного виводу
    except Exception as e:
        logging.exception("Під час обробки сталася помилка:")
        sys.exit(2)

if __name__ == "__main__":
    main()
