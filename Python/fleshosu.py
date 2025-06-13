import sys
import time
import threading
import librosa
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import numpy as np
import tempfile
import os
import soundfile as sf

# === Configuration ===
HIT_ZONE_X = 100
NODE_COLOR = "#FF6464"
NODE_RADIUS = 16
LINE_Y = 220
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 400
FPS = 60

# === Tkinter Setup ===
root = tk.Tk()
root.title("FleshOsu! Rhythm Game")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="#22242a")
canvas.pack()

# === File Dialog ===
def select_audio():
    path = filedialog.askopenfilename(
        title="Select audio file",
        filetypes=[("Audio Files", "*.wav *.mp3 *.ogg *.flac *.m4a *.aac *.aiff *.wma")]
    )
    return path

audio_path = select_audio()
if not audio_path:
    messagebox.showinfo("No file", "No file selected. Exiting.")
    sys.exit()

# === Async Beat Detection with Progress ===
beat_times = []
tempo = 0
y = None
sr = None
audio_wav_path = None

def analyze_beats():
    global beat_times, tempo, y, sr, audio_wav_path
    try:
        canvas.create_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, text="Loading audio...", fill="white", font=("Consolas", 18), tags="loading")
        root.update()
        y, sr = librosa.load(audio_path, sr=None, mono=True, dtype=np.float32)
        canvas.delete("loading")
        canvas.create_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, text="Analyzing beats...", fill="white", font=("Consolas", 18), tags="loading")
        root.update()
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, units='frames')
        beat_times.clear()
        beat_times.extend(librosa.frames_to_time(beat_frames, sr=sr))
        # Convert audio to wav for simpleaudio if needed
        if not audio_path.lower().endswith(".wav"):
            tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            y16 = np.int16(np.clip(y, -1, 1) * 32767)
            sf.write(tmp_wav.name, y16, sr, subtype='PCM_16')
            audio_wav_path = tmp_wav.name
        else:
            audio_wav_path = audio_path
        time.sleep(0.3)
        canvas.delete("loading")
        canvas.create_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, text=f"Detected {len(beat_times)} beats.\nTempo: {int(tempo)} BPM", fill="white", font=("Consolas", 16))
        root.update()
        time.sleep(1)
        canvas.delete("all")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to analyze audio:\n{e}")
        sys.exit()

# Run beat detection in a thread and wait for finish
analyze_thread = threading.Thread(target=analyze_beats)
analyze_thread.start()
while analyze_thread.is_alive():
    root.update()
    time.sleep(0.01)

# === Node Class ===
class Node:
    def __init__(self, spawn_time):
        self.spawn_time = spawn_time
        self.x = WINDOW_WIDTH
        self.y = LINE_Y
        self.hit = False
        self.miss = False

    def update(self, dt, speed):
        self.x -= speed * dt

    def draw(self):
        color = NODE_COLOR if not self.hit else "#64FF64"
        if self.miss:
            color = "#C04040"
        canvas.create_oval(
            self.x - NODE_RADIUS, self.y - NODE_RADIUS,
            self.x + NODE_RADIUS, self.y + NODE_RADIUS,
            fill=color, outline="#FFF", width=2
        )

# === Game State ===
nodes = []
next_beat_idx = 0
speed = 220.0
score = 0
combo = 0
max_combo = 0
misses = 0
feedback = ""
feedback_timer = 0
game_started = False
start_time = 0
audio_playing = False

# === Audio Playback (tkinter-only, no pygame) ===
try:
    import simpleaudio as sa
    AUDIO_OK = True
except ImportError:
    AUDIO_OK = False

def play_audio():
    global audio_playing
    if AUDIO_OK:
        try:
            # Wait until audio_wav_path is ready and file exists
            while not audio_wav_path or not os.path.exists(audio_wav_path):
                time.sleep(0.01)
            wave_obj = sa.WaveObject.from_wave_file(audio_wav_path)
            audio_playing = True
            wave_obj.play()
        except Exception as e:
            messagebox.showinfo("Audio", f"Audio playback failed: {e}")
    else:
        messagebox.showinfo("Audio", "simpleaudio not installed, no sound will play.")

# === Controls ===
def on_key(event):
    global speed, combo, max_combo, misses, score, feedback, feedback_timer
    if event.keysym in ("Up", "w"):
        speed += 30
    elif event.keysym in ("Down", "s"):
        speed = max(50, speed - 30)
    elif event.keysym in ("z", "x", "space"):
        hit_this = False
        for node in nodes:
            if not node.hit and not node.miss and abs(node.x - HIT_ZONE_X) < NODE_RADIUS + 10:
                node.hit = True
                score += 100
                combo += 1
                max_combo = max(max_combo, combo)
                feedback = "Great!"
                feedback_timer = 0.5
                hit_this = True
                break
        if not hit_this:
            combo = 0
            misses += 1
            feedback = "Miss!"
            feedback_timer = 0.5
    elif event.keysym == "Escape":
        root.destroy()

root.bind("<Key>", on_key)

# === Main Game Loop ===
def game_loop():
    global next_beat_idx, feedback, feedback_timer, start_time, game_started

    now = time.time()
    if not game_started:
        start_time = now
        if AUDIO_OK:
            threading.Thread(target=play_audio, daemon=True).start()
        game_started = True

    dt = 1.0 / FPS
    current_time = now - start_time

    # Spawn nodes
    while next_beat_idx < len(beat_times) and beat_times[next_beat_idx] <= current_time:
        nodes.append(Node(beat_times[next_beat_idx]))
        next_beat_idx += 1

    # Update nodes
    for node in nodes:
        node.update(dt, speed)
        if not node.hit and not node.miss and node.x < HIT_ZONE_X - NODE_RADIUS:
            node.miss = True
            global combo, misses
            combo = 0
            misses += 1
            feedback = "Miss!"
            feedback_timer = 0.5

    # Remove nodes that are far left
    nodes[:] = [n for n in nodes if n.x > -NODE_RADIUS*2 or not n.hit]

    # Drawing
    canvas.delete("all")
    # Draw line
    canvas.create_line(0, LINE_Y, WINDOW_WIDTH, LINE_Y, fill="#DDD", width=2)
    # Draw hit zone
    canvas.create_rectangle(HIT_ZONE_X-8, LINE_Y-32, HIT_ZONE_X+8, LINE_Y+32, fill="#7CE77C", outline="#50B850", width=2)
    # Draw nodes
    for node in nodes:
        node.draw()
    # Draw score, combo, etc.
    canvas.create_text(20, 20, anchor="w", text=f"Score: {score}", fill="#FFF", font=("Consolas", 18, "bold"))
    canvas.create_text(20, 50, anchor="w", text=f"Combo: {combo}", fill="#FFD850" if combo > 0 else "#FF5050", font=("Consolas", 16, "bold"))
    canvas.create_text(20, 75, anchor="w", text=f"Max Combo: {max_combo}", fill="#FFD850", font=("Consolas", 12))
    canvas.create_text(20, 100, anchor="w", text=f"Misses: {misses}", fill="#FF5050", font=("Consolas", 12))
    canvas.create_text(WINDOW_WIDTH-20, 20, anchor="e", text=f"Speed: {int(speed)} px/s", fill="#FFF", font=("Consolas", 14))
    canvas.create_text(WINDOW_WIDTH-20, 45, anchor="e", text=f"Tempo: {int(tempo)} BPM", fill="#B0B0FF", font=("Consolas", 14))

    # Feedback
    if feedback and feedback_timer > 0:
        fb_color = "#64FF64" if feedback == "Great!" else "#FF5050"
        canvas.create_text(WINDOW_WIDTH//2, LINE_Y-60, text=feedback, fill=fb_color, font=("Consolas", 32, "bold"))
        feedback_timer -= dt
        if feedback_timer <= 0:
            feedback = ""

    # Controls help
    help_lines = [
        "Controls:",
        "Z / X / SPACE - Hit",
        "UP/DOWN - Change speed",
        "ESC - Quit"
    ]
    for i, line in enumerate(help_lines):
        canvas.create_text(WINDOW_WIDTH-20, WINDOW_HEIGHT-80 + i*20, anchor="e", text=line, fill="#BBB", font=("Consolas", 11))

    root.after(int(1000/FPS), game_loop)

game_loop()
root.mainloop()

# Clean up temp wav file if created
if audio_wav_path and audio_wav_path != audio_path:
    try:
        os.remove(audio_wav_path)
    except Exception:
        pass
