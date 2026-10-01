"""Bounded hotkey sequences. Default CLI execution is a dry run."""
import argparse
import ctypes
import threading
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Step:
    action: str
    value: object
    delay_ms: int = 0


SEQUENCES = {
    "q": (Step("scroll", -2, 31), Step("scroll", 2, 32)),
    "t": (Step("click", "left", 100), Step("click", "right")),
    "1": (Step("click", "left", 10), Step("click", "right", 10),
          Step("tap", "space", 20)),
}


class Engine:
    def __init__(self, emit, allowed=lambda: True):
        self.emit = emit
        self.allowed = allowed
        self.cancel = threading.Event()
        self.lock = threading.Lock()
        self.paused = False
        self.last = float("-inf")

    def run(self, key):
        if key not in SEQUENCES or not self.lock.acquire(blocking=False):
            return False
        try:
            now = time.monotonic()
            if self.paused or self.cancel.is_set() or now - self.last < .3:
                return False
            if not self.allowed():
                return False
            self.last = now
            for step in SEQUENCES[key]:
                if self.cancel.is_set() or self.paused or not self.allowed():
                    return False
                self.emit(step)
                if self.cancel.wait(step.delay_ms / 1000):
                    return False
            return True
        finally:
            self.lock.release()


def game_active():
    """Only the original game's foreground window is accepted."""
    if not hasattr(ctypes, "windll"):
        return False
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    text = ctypes.create_unicode_buffer(512)
    user32.GetWindowTextW(hwnd, text, len(text))
    return "left 4 dead 2" in text.value.lower()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", choices=SEQUENCES, default="q")
    parser.add_argument("--live", action="store_true",
                        help="Listen for Q/T/1 while Left 4 Dead 2 is foreground")
    args = parser.parse_args()
    if not args.live:
        Engine(lambda s: print(f"{s.action}: {s.value}; wait {s.delay_ms} ms")).run(args.demo)
        return
    from pynput import keyboard, mouse
    mouse_output, key_output = mouse.Controller(), keyboard.Controller()
    def emit(step):
        if step.action == "scroll":
            mouse_output.scroll(0, step.value)
        elif step.action == "click":
            mouse_output.click(getattr(mouse.Button, step.value))
        else:
            key_output.press(keyboard.Key.space)
            try:
                pass
            finally:
                key_output.release(keyboard.Key.space)
    engine = Engine(emit, game_active)
    held = set()
    workers = []
    def press(key):
        token = getattr(key, "char", None)
        token = token.lower() if token else str(key)
        if token in held:
            return
        held.add(token)
        if key == keyboard.Key.f8:
            engine.paused = not engine.paused
            print("Paused" if engine.paused else "Ready")
        elif key == keyboard.Key.f5 and any(k in held for k in
                                            ("Key.alt", "Key.alt_l", "Key.alt_r")):
            engine.cancel.set()
            return False
        elif token in SEQUENCES:
            # No backlog of delayed actions; the engine rejects overlap.
            thread = threading.Thread(target=engine.run, args=(token,), daemon=True)
            workers[:] = [w for w in workers if w.is_alive()]
            workers.append(thread)
            thread.start()
    def release(key):
        token = getattr(key, "char", None)
        held.discard(token.lower() if token else str(key))
    print("Q / T / 1 • F8 pause • Alt+F5 exit • foreground L4D2 only")
    try:
        with keyboard.Listener(on_press=press, on_release=release) as listener:
            listener.join()
    finally:
        engine.cancel.set()
        for worker in workers:
            worker.join(timeout=1)


if __name__ == "__main__":
    main()
