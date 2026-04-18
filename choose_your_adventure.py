import os
import sys
import math
import wave
import struct
import tkinter as tk

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
WINDOW_WIDTH = 960
CANVAS_HEIGHT = 460
WINDOW_HEIGHT = CANVAS_HEIGHT + 160
TEXT_FONT = ("Segoe UI", 14)

SCENES = {
    "intro": {
        "title": "Mystic Forest",
        "text": "You wake up in a misty forest with glowing mushrooms. A path stretches into the distance, while shadows rustle in the trees.",
        "background": "bg_forest.ppm",
        "character": "hero.ppm",
        "sound": "bgm.wav",
        "choices": [
            {"text": "Follow the glowing path", "target": "castle"},
            {"text": "Hide and wait", "target": "cave"},
        ],
    },
    "castle": {
        "title": "Castle Gate",
        "text": "A friendly wizard greets you at the castle gate and offers to guide you. You feel a warm energy around you.",
        "background": "bg_castle.ppm",
        "character": "wizard.ppm",
        "sound": "bgm.wav",
        "choices": [
            {"text": "Accept the wizard's help", "target": "peace"},
            {"text": "Explore the tower alone", "target": "danger"},
        ],
    },
    "cave": {
        "title": "Hidden Cave",
        "text": "You crouch behind a mossy tree and discover a cave entrance. A creature stirs inside, and the air grows cold.",
        "background": "bg_cave.ppm",
        "character": "goblin.ppm",
        "sound": "bgm.wav",
        "choices": [
            {"text": "Sneak inside", "target": "danger"},
            {"text": "Run back to the path", "target": "castle"},
        ],
    },
    "peace": {
        "title": "A New Beginning",
        "text": "With the wizard's guidance, you step into a bright future. The adventure has only just begun.",
        "background": "bg_castle.ppm",
        "character": "hero.ppm",
        "sound": "click.wav",
        "choices": [
            {"text": "Play again", "target": "intro"},
        ],
    },
    "danger": {
        "title": "Danger Awaits",
        "text": "A shadow leaps from the darkness. You have entered a challenge that will test your courage.",
        "background": "bg_cave.ppm",
        "character": "goblin.ppm",
        "sound": "click.wav",
        "choices": [
            {"text": "Try again", "target": "intro"},
        ],
    },
}


def save_ppm(path, width, height, pixel_func):
    with open(path, "wb") as fp:
        fp.write(f"P6\n{width} {height}\n255\n".encode("ascii"))
        for y in range(height):
            for x in range(width):
                r, g, b = pixel_func(x, y, width, height)
                fp.write(bytes((r, g, b)))


def forest_pixel(x, y, w, h):
    if y > h * 0.75:
        base = (62, 90, 45)
    else:
        base = (112, 171, 216)
    if 30 < x < 110 and y > h * 0.45:
        return (92, 58, 24) if y > h * 0.65 else (40, 112, 55)
    if 220 < x < 325 and y > h * 0.35 and y < h * 0.65:
        return (42, 132, 62)
    if 540 < x < 620 and y > h * 0.4:
        return (91, 61, 27) if y > h * 0.68 else (34, 101, 42)
    if y < h * 0.15 and 300 < x < 500:
        return (255, 241, 171)
    return base


def cave_pixel(x, y, w, h):
    if y > h * 0.8:
        base = (46, 40, 39)
    else:
        base = (54, 58, 73)
    if 360 < x < 600 and y > h * 0.35:
        return (22, 22, 27) if x < 420 or x > 540 else (12, 12, 14)
    if y > h * 0.7 and 220 < x < 280:
        return (90, 84, 78)
    return base


def castle_pixel(x, y, w, h):
    if y > h * 0.85:
        base = (98, 97, 78)
    else:
        base = (142, 198, 255)
    if 520 < x < 640 and y > h * 0.45:
        return (205, 205, 222) if x > 560 else (176, 175, 189)
    if 670 < x < 760 and y > h * 0.4:
        return (186, 184, 203)
    if 480 < x < 520 and y > h * 0.6:
        return (90, 30, 50)
    return base


def hero_pixel(x, y, w, h):
    center_x = w // 2
    if y < h * 0.25:
        dx = x - center_x
        if dx * dx + (y - 40) ** 2 < 950:
            return (243, 203, 156)
    if y > h * 0.3 and abs(x - center_x) < 28:
        return (55, 92, 196)
    if 100 < y < 135 and abs(x - center_x) < 12:
        return (55, 92, 196)
    if y > h * 0.5 and abs(x - center_x) < 16:
        return (31, 42, 61)
    if 65 < y < 75 and abs(x - (center_x - 25)) < 18:
        return (255, 255, 255)
    return (18, 18, 18)


def wizard_pixel(x, y, w, h):
    center_x = w // 2
    if y < h * 0.3:
        if abs(x - center_x) < 30 and y > h * 0.1:
            return (44, 24, 97)
    if y < h * 0.25 and abs(x - center_x) < 18:
        return (255, 223, 186)
    if y > h * 0.3 and abs(x - center_x) < 24:
        return (91, 163, 222)
    if 140 < y < 170 and abs(x - (center_x - 40)) < 18:
        return (80, 125, 47)
    if 120 < y < 140 and abs(x - (center_x + 40)) < 14:
        return (80, 125, 47)
    return (16, 16, 24)


def goblin_pixel(x, y, w, h):
    center_x = w // 2
    if y < h * 0.3 and (abs(x - center_x) < 28 and y > h * 0.1):
        return (146, 192, 69)
    if y < h * 0.2 and abs(x - (center_x - 20)) < 10:
        return (146, 192, 69)
    if y < h * 0.2 and abs(x - (center_x + 20)) < 10:
        return (146, 192, 69)
    if y > h * 0.3 and abs(x - center_x) < 26:
        return (88, 124, 45)
    if y > h * 0.5 and abs(x - center_x) < 16:
        return (26, 26, 28)
    return (12, 12, 16)


def generate_audio(path, sound_type):
    sample_rate = 44100
    if sound_type == "bgm.wav":
        frequencies = [220, 262, 330, 392]
        duration = 4.0
        volume = 0.15
    else:
        frequencies = [440, 660]
        duration = 0.18
        volume = 0.2

    n_frames = int(sample_rate * duration)
    audio_data = bytearray()
    for i in range(n_frames):
        t = i / sample_rate
        sample = 0
        for idx, freq in enumerate(frequencies):
            amplitude = volume * (0.9 if idx == 0 else 0.4)
            sample += math.sin(2 * math.pi * freq * t) * amplitude
        sample = max(-1.0, min(1.0, sample))
        value = int(sample * 32767)
        audio_data += struct.pack("<h", value)

    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)


def ensure_assets():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    images = {
        "bg_forest.ppm": (960, CANVAS_HEIGHT, forest_pixel),
        "bg_cave.ppm": (960, CANVAS_HEIGHT, cave_pixel),
        "bg_castle.ppm": (960, CANVAS_HEIGHT, castle_pixel),
        "hero.ppm": (180, 260, hero_pixel),
        "wizard.ppm": (180, 260, wizard_pixel),
        "goblin.ppm": (180, 260, goblin_pixel),
    }

    for filename, (width, height, builder) in images.items():
        path = os.path.join(ASSETS_DIR, filename)
        save_ppm(path, width, height, builder)

    audio_files = ["bgm.wav", "click.wav"]
    for filename in audio_files:
        path = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(path):
            generate_audio(path, filename)


def play_sound(filename, loop=False):
    try:
        import winsound
    except ImportError:
        return

    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(path):
        return

    mode = winsound.SND_ASYNC | winsound.SND_FILENAME
    if loop:
        mode |= winsound.SND_LOOP
    winsound.PlaySound(path, mode)


def stop_sound():
    try:
        import winsound
        winsound.PlaySound(None, winsound.SND_PURGE)
    except ImportError:
        pass


class AdventureGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Choose Your Own Adventure")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=CANVAS_HEIGHT, highlightthickness=0)
        self.canvas.pack()

        self.text_frame = tk.Frame(root, bg="#10121b", height=160)
        self.text_frame.pack(fill="x", side="bottom")

        self.title_label = tk.Label(self.text_frame, text="", font=("Segoe UI", 18, "bold"), fg="#f5f6ff", bg="#10121b")
        self.title_label.pack(anchor="w", padx=16, pady=(12, 0))

        self.story_label = tk.Label(
            self.text_frame,
            text="",
            font=TEXT_FONT,
            fg="#e8ebff",
            bg="#10121b",
            wraplength=WINDOW_WIDTH - 32,
            justify="left",
        )
        self.story_label.pack(anchor="w", padx=16, pady=(4, 8))

        self.button_frame = tk.Frame(self.text_frame, bg="#10121b")
        self.button_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.choice_buttons = []
        for _ in range(3):
            button = tk.Button(
                self.button_frame,
                text="",
                font=("Segoe UI", 12),
                width=32,
                relief="raised",
                bd=4,
                bg="#2f4d8f",
                fg="#ffffff",
                activebackground="#2f6fbf",
                activeforeground="#ffffff",
                command=lambda: None,
            )
            button.pack(side="left", padx=6)
            self.choice_buttons.append(button)

        self.image_cache = {}
        self.current_scene = None
        self.goto_scene("intro")

    def load_image(self, filename):
        if filename in self.image_cache:
            return self.image_cache[filename]
        path = os.path.join(ASSETS_DIR, filename)
        image = tk.PhotoImage(file=path)
        self.image_cache[filename] = image
        return image

    def draw_scene(self, scene):
        self.canvas.delete("all")
        bg_image = self.load_image(scene["background"])
        self.canvas.create_image(0, 0, image=bg_image, anchor="nw")

        char_image = self.load_image(scene["character"])
        char_x = WINDOW_WIDTH - 220
        char_y = CANVAS_HEIGHT - 280
        self.canvas.create_image(char_x, char_y, image=char_image, anchor="nw")

        self.title_label.config(text=scene["title"])
        self.story_label.config(text=scene["text"])

        for button in self.choice_buttons:
            button.pack_forget()

        for index, choice in enumerate(scene["choices"]):
            button = self.choice_buttons[index]
            button.config(text=choice["text"], command=lambda target=choice["target"]: self.goto_scene(target))
            button.pack(side="left", padx=6)

    def goto_scene(self, scene_key):
        if self.current_scene == scene_key:
            return
        self.current_scene = scene_key
        scene = SCENES[scene_key]
        self.draw_scene(scene)

        stop_sound()
        if scene.get("sound") == "bgm.wav":
            play_sound(scene["sound"], loop=True)
        elif scene.get("sound"):
            play_sound(scene["sound"], loop=False)


def main():
    ensure_assets()
    root = tk.Tk()
    AdventureGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
