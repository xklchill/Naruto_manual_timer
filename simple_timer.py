import tkinter as tk
from pynput import keyboard
import json
import os

COUNTDOWN_SECONDS = 13.5
TRANSPARENT_COLOR = "#ff00ff"
POSITION_FILE = "countdown_position.json"


class FloatingCountdown:
    def __init__(self):
        self.root = tk.Tk()

        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)

        self.root.configure(bg=TRANSPARENT_COLOR)
        self.root.attributes("-transparentcolor", TRANSPARENT_COLOR)

        # 读取上一次保存的位置
        x, y = self.load_position()
        self.root.geometry(f"180x90+{x}+{y}")

        self.label = tk.Label(
            self.root,
            text="0",
            font=("Arial", 48, "bold"),
            fg="black",
            bg=TRANSPARENT_COLOR
        )
        self.label.pack(expand=True, fill="both")

        self.offset_x = 0
        self.offset_y = 0

        self.label.bind("<Button-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.do_move)
        self.label.bind("<ButtonRelease-1>", self.save_current_position)

        # 右键退出
        self.label.bind("<Button-3>", lambda e: self.quit())

        self.remaining = 0
        self.timer_id = None

        self.listen_keyboard()

    def load_position(self):
        if os.path.exists(POSITION_FILE):
            try:
                with open(POSITION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("x", 300), data.get("y", 200)
            except Exception:
                pass

        return 300, 200

    def save_position(self, x, y):
        data = {
            "x": x,
            "y": y
        }

        with open(POSITION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def save_current_position(self, event=None):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.save_position(x, y)

    def start_move(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def do_move(self, event):
        x = self.root.winfo_pointerx() - self.offset_x
        y = self.root.winfo_pointery() - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def start_countdown(self):
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)

        self.remaining = COUNTDOWN_SECONDS
        self.update_countdown()

    def update_countdown(self):
        self.label.config(text=str(self.remaining))

        if self.remaining > 0:
            self.remaining = round(self.remaining - 0.1, 1)
            self.timer_id = self.root.after(100, self.update_countdown)
        else:
            self.timer_id = None
            self.label.config(text="0")

    def on_press(self, key):
        try:
            if key.char and key.char.lower() == "q":
                self.root.after(0, self.start_countdown)
        except AttributeError:
            pass

    def listen_keyboard(self):
        listener = keyboard.Listener(on_press=self.on_press)
        listener.daemon = True
        listener.start()

    def quit(self):
        self.save_current_position()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = FloatingCountdown()
    app.run()