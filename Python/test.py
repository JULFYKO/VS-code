import os
import urllib.parse
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import concurrent.futures

try:
    import win32com.client
    import pythoncom
except ImportError:
    win32com = None
    pythoncom = None

try:
    import docx
except ImportError:
    docx = None

def read_txt_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"[!] Помилка читання .txt файлу: {e}"

def read_rtf_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"[!] Помилка читання .rtf файлу: {e}"

def read_docx_file(path):
    if docx is None:
        return "[!] Модуль python-docx не встановлено, не можу прочитати .docx файл"
    try:
        document = docx.Document(path)
        paragraphs = [para.text for para in document.paragraphs if para.text]
        return "\n".join(paragraphs) if paragraphs else "[Порожній документ .docx]"
    except Exception as e:
        return f"[!] Помилка читання .docx файлу: {e}"

def read_doc_file(path):
    if win32com is None or pythoncom is None:
        return "[!] pywin32/pythoncom не встановлено, не можу прочитати .doc файл"
    # У кожному потоці треба ініціалізувати COM
    try:
        pythoncom.CoInitialize()
    except Exception:
        pass  # Якщо не вдається, далі спробуємо працювати, але може бути помилка
    try:
        decoded_path = urllib.parse.unquote(path)
        normalized_path = os.path.normpath(decoded_path)
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        doc = word.Documents.Open(normalized_path)
        text = doc.Content.Text
        doc.Close(False)
        word.Quit()
        return text.strip() if text else "[Порожній .doc]"
    except Exception as e:
        return f"[!] Помилка читання .doc файлу: {e}"
    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass

def read_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.txt':
        return read_txt_file(path)
    if ext == '.rtf':
        return read_rtf_file(path)
    if ext == '.docx':
        return read_docx_file(path)
    if ext == '.doc':
        return read_doc_file(path)
    return f"[!] Формат файлу {ext} не підтримується"

def get_desktop_path():
    return os.path.join(os.path.expanduser("~"), "Desktop")

def process_one(path):
    """Читає один файл і повертає (basename, content)."""
    name = os.path.basename(path)
    content = read_file(path)
    return name, content

def main():
    root = tk.Tk()
    root.withdraw()
    print("Виберіть файли для об'єднання (ASCII: Ctrl/Cmd + клік для множинного вибору)...")
    file_paths = filedialog.askopenfilenames(
        title="Оберіть файли для об'єднання",
        filetypes=[("Документи", "*.txt *.rtf *.doc *.docx"), ("Всі файли", "*.*")]
    )
    if not file_paths:
        print("Файли не обрані, вихід.")
        return

    print(f"\nОбрано {len(file_paths)} файл(ів):")
    for p in file_paths:
        print(" -", p)

    desktop = get_desktop_path()
    default_name = datetime.now().strftime("merged_%Y%m%d_%H%M%S.txt")
    default_path = os.path.join(desktop, default_name)

    user_input = input(
        f"\nВведіть шлях та ім'я вихідного файлу або натисніть Enter, щоб зберегти за замовчуванням:\n[{default_path}]: "
    ).strip()
    output_path = user_input if user_input else default_path

    # Якщо користувач вказав тільки ім'я без шляху, додаємо Desktop
    if not os.path.isabs(output_path):
        output_path = os.path.join(desktop, output_path)

    # Додаємо розширення .txt, якщо його нема
    if not os.path.splitext(output_path)[1]:
        output_path += ".txt"

    # Паралельно обробляємо всі файли
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(32, os.cpu_count() or 1)) as executor:
        futures = {executor.submit(process_one, path): path for path in file_paths}
        for future in concurrent.futures.as_completed(futures):
            name, content = future.result()
            results.append((name, content))

    # Записуємо всі результати в один файл
    try:
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for name, content in results:
                outfile.write(f"--- {name} ---\n")
                outfile.write(content + "\n\n")
        print(f"\n[✔] Об'єднані файли записані у: {output_path}")
    except Exception as e:
        print(f"[!] Помилка запису у файл: {e}")

if __name__ == "__main__":
    main()
