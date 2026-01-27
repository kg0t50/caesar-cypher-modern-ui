"""
caesar_custom_app.py

A modern, animated Caesar Cipher app using CustomTkinter.

Features:
- Encrypt / Decrypt / Brute Force
- Save / Load files
- Copy output to clipboard
- Light / Dark theme toggle
- Rounded buttons, custom fonts (with fallbacks)
- Small animations (transition for status bar & theme change)
- Single-file, ready to copy/paste

Dependencies:
    pip install customtkinter

Author: Asami-style assistant for Kgotso
"""

import tkinter as tk
from tkinter import filedialog, font as tkfont, messagebox
import customtkinter as ctk
import os
import time
from functools import partial

# -------------------------
# App config & utilities
# -------------------------
APP_TITLE = "Caesar Cipher — Modern UI"
WINDOW_SIZE = "820x620"
DEFAULT_SHIFT = 3
ALPHABET_SIZE = 26

# Theme colours (ctk uses built-in themes, but we'll customise some colors)
LIGHT_BG = "#F4F6F8"
DARK_BG = "#111217"
ACCENT = "#2dd4bf"  # aquamarine accent


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


# -------------------------
# Caesar logic
# -------------------------
def shift_char(ch: str, shift: int) -> str:
    if 'A' <= ch <= 'Z':
        idx = ord(ch) - ord('A')
        return chr(((idx + shift) % ALPHABET_SIZE) + ord('A'))
    if 'a' <= ch <= 'z':
        idx = ord(ch) - ord('a')
        return chr(((idx + shift) % ALPHABET_SIZE) + ord('a'))
    return ch

def encrypt_text(text: str, shift: int) -> str:
    return ''.join(shift_char(ch, shift) for ch in text)

def decrypt_text(text: str, shift: int) -> str:
    return encrypt_text(text, -shift)

def brute_force(text: str) -> str:
    lines = []
    for s in range(ALPHABET_SIZE):
        lines.append(f"Shift {s:2d}: {decrypt_text(text, s)}")
    return '\n'.join(lines)


# -------------------------
# UI helpers (animations)
# -------------------------
def animate_label_fade(label: ctk.CTkLabel, text: str, duration=350):
    """Simple fade-in style update using after (not true alpha fade but timed visibility)."""
    label.configure(text="")
    steps = 8
    wait = max(10, duration // steps)
    chars = list(text)

    def step(i=0):
        # gradually reveal characters
        show = ''.join(chars[:int(len(chars) * (i / steps))])
        label.configure(text=show)
        if i < steps:
            label.after(wait, lambda: step(i+1))
    step(1)


# -------------------------
# Main Application
# -------------------------
class CaesarApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(720, 520)

        # Configure default appearance for CustomTkinter
        ctk.set_appearance_mode("dark")   # start dark
        ctk.set_default_color_theme("blue")

        # Attempt to register a custom font (user can add .ttf in same folder named "Inter-Regular.ttf")
        base_font_name = "Segoe UI"
        try:
            local_font_path = os.path.join(os.path.dirname(__file__), "Inter-Regular.ttf")
            if os.path.exists(local_font_path):
                tkfont.Font(family="Inter", size=11)  # just to register
                base_font_name = "Inter"
        except Exception:
            base_font_name = "Segoe UI"

        self.base_font = (base_font_name, 11)
        self.header_font = (base_font_name, 16, "bold")

        # State variables
        self.mode = ctk.StringVar(value="Encrypt")  # Encrypt / Decrypt / Brute Force
        self.shift = ctk.IntVar(value=DEFAULT_SHIFT)
        self.status_text = tk.StringVar(value="Ready")
        self.appearance = tk.StringVar(value="Dark")

        # Layout
        self._build_ui()
        self._bind_shortcuts()

    def _build_ui(self):
        # Top bar frame
        top_frame = ctk.CTkFrame(self, corner_radius=12, fg_color=None)
        top_frame.pack(fill="x", padx=16, pady=(16, 8))

        title = ctk.CTkLabel(top_frame, text="🔐 Caesar Cipher", font=self.header_font, anchor="w")
        title.pack(side="left", padx=(12, 8), pady=8)

        subtitle = ctk.CTkLabel(top_frame, text="Encrypt · Decrypt · Brute Force  — modern UI", font=(self.base_font[0], 10))
        subtitle.pack(side="left", padx=(0, 12), pady=8)

        # Right controls on top bar
        top_right = ctk.CTkFrame(top_frame, fg_color=None, corner_radius=8)
        top_right.pack(side="right", padx=(8, 12), pady=8)

        # Theme toggle
        self.theme_toggle = ctk.CTkSwitch(top_right, text="", command=self._toggle_theme, progress_color=ACCENT)
        self.theme_toggle.pack(side="right", padx=8)
        self.theme_label = ctk.CTkLabel(top_right, text="Dark", font=(self.base_font[0], 10))
        self.theme_label.pack(side="right", padx=6)

        # Save/Load quick buttons
        load_btn = ctk.CTkButton(top_right, text="Load", width=70, command=self._load_file, corner_radius=14)
        load_btn.pack(side="right", padx=6)
        save_btn = ctk.CTkButton(top_right, text="Save", width=70, command=self._save_file, corner_radius=14)
        save_btn.pack(side="right", padx=6)

        # Main area
        main_frame = ctk.CTkFrame(self, corner_radius=14)
        main_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # Left column: controls
        left = ctk.CTkFrame(main_frame, corner_radius=12)
        left.pack(side="left", fill="y", padx=12, pady=12)

        # Mode radio buttons
        ctk.CTkLabel(left, text="Mode", font=(self.base_font[0], 12, "bold")).pack(pady=(8, 6), anchor="w", padx=8)
        modes = ["Encrypt", "Decrypt", "Brute Force"]
        for m in modes:
            r = ctk.CTkRadioButton(left, text=m, variable=self.mode, value=m, command=self._on_mode_change)
            r.pack(anchor="w", padx=12, pady=4)

        # Shift controls
        ctk.CTkLabel(left, text="Shift", font=(self.base_font[0], 12, "bold")).pack(pady=(12, 6), anchor="w", padx=8)
        spin = ctk.CTkSlider(left, from_=0, to=25, number_of_steps=26, variable=self.shift, command=self._on_shift_slide)
        spin.pack(fill="x", padx=12, pady=(0, 4))
        self.shift_label = ctk.CTkLabel(left, text=f"Shift: {self.shift.get()}", anchor="w")
        self.shift_label.pack(padx=12, pady=(0, 12), anchor="w")

        # Action buttons (rounded)
        action_frame = ctk.CTkFrame(left, fg_color=None, corner_radius=8)
        action_frame.pack(padx=8, pady=6, fill="x")

        run_btn = ctk.CTkButton(action_frame, text="Run", command=self._run, corner_radius=18, height=44, fg_color=ACCENT)
        run_btn.pack(fill="x", padx=6, pady=(8, 6))

        clear_btn = ctk.CTkButton(action_frame, text="Clear", command=self._clear_texts, corner_radius=18, height=36)
        clear_btn.pack(fill="x", padx=6, pady=(0, 8))

        copy_btn = ctk.CTkButton(action_frame, text="Copy Output", command=self._copy_output, corner_radius=18, height=36)
        copy_btn.pack(fill="x", padx=6, pady=(0, 8))

        # Right column: text areas
        right = ctk.CTkFrame(main_frame, corner_radius=12)
        right.pack(side="right", fill="both", expand=True, padx=12, pady=12)

        top_text_frame = ctk.CTkFrame(right, corner_radius=8)
        top_text_frame.pack(fill="both", expand=True, padx=12, pady=(12, 6))

        ctk.CTkLabel(top_text_frame, text="Input Text", font=(self.base_font[0], 12, "bold")).pack(anchor="w", padx=8, pady=(8,0))
        self.input_text = ctk.CTkTextbox(top_text_frame, width=420, height=180, wrap="word", corner_radius=10)
        self.input_text.pack(fill="both", expand=True, padx=8, pady=8)

        bottom_text_frame = ctk.CTkFrame(right, corner_radius=8)
        bottom_text_frame.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        ctk.CTkLabel(bottom_text_frame, text="Output", font=(self.base_font[0], 12, "bold")).pack(anchor="w", padx=8, pady=(8,0))
        self.output_text = ctk.CTkTextbox(bottom_text_frame, width=420, height=220, wrap="word", corner_radius=10, fg_color="#071013")
        self.output_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.output_text.configure(state="disabled")

        # Status bar
        status_frame = ctk.CTkFrame(self, corner_radius=8, fg_color=None)
        status_frame.pack(fill="x", padx=16, pady=(0, 12))
        self.status_label = ctk.CTkLabel(status_frame, textvariable=self.status_text, font=(self.base_font[0], 10))
        self.status_label.pack(side="left", padx=8, pady=6)

        # Small helpful label on right
        self.hint_label = ctk.CTkLabel(status_frame, text="Tip: Use Run or drag files into Load", font=(self.base_font[0], 10))
        self.hint_label.pack(side="right", padx=8, pady=6)

    # -------------------------
    # Event handlers & actions
    # -------------------------
    def _bind_shortcuts(self):
        self.bind("<Control-s>", lambda e: self._save_file())
        self.bind("<Control-o>", lambda e: self._load_file())
        self.bind("<Control-r>", lambda e: self._run())
        self.bind("<Control-c>", lambda e: self._copy_output())

    def _on_mode_change(self):
        m = self.mode.get()
        animate_label_fade(self.status_label, f"Mode set to {m}", duration=260)
        # If brute force, disable shift slider visually by greying label
        if m == "Brute Force":
            self.shift_label.configure(text="Shift: (unused in brute mode)")
        else:
            self.shift_label.configure(text=f"Shift: {self.shift.get()}")

    def _on_shift_slide(self, val):
        self.shift_label.configure(text=f"Shift: {int(float(val))}")

    def _toggle_theme(self):
        # simple theme toggle with small delay/animation feel
        cur = ctk.get_appearance_mode()
        new = "light" if cur == "dark" else "dark"
        ctk.set_appearance_mode(new)
        self.theme_label.configure(text=new.capitalize())
        animate_label_fade(self.status_label, f"Switched to {new.capitalize()} mode", duration=300)

    def _run(self):
        txt = self.input_text.get("1.0", "end").rstrip('\n')
        if not txt.strip():
            messagebox.showwarning("No input", "Please enter or load text to process.")
            return

        mode = self.mode.get()
        shift_val = clamp(self.shift.get(), 0, 25)

        # Small animated status change
        self.status_text.set("Processing...")
        self.status_label.update_idletasks()

        # simulate micro-animation (non-blocking)
        self.after(120, lambda: self._do_process(txt, mode, shift_val))

    def _do_process(self, txt, mode, shift_val):
        if mode == "Encrypt":
            out = encrypt_text(txt, shift_val)
        elif mode == "Decrypt":
            out = decrypt_text(txt, shift_val)
        else:
            out = brute_force(txt)

        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", out)
        self.output_text.configure(state="disabled")

        animate_label_fade(self.status_label, f"Done — {mode} completed", duration=260)

    def _clear_texts(self):
        self.input_text.delete("1.0", "end")
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")
        animate_label_fade(self.status_label, "Cleared text fields", duration=180)

    def _copy_output(self):
        out = self.output_text.get("1.0", "end").rstrip('\n')
        if not out:
            animate_label_fade(self.status_label, "Nothing to copy", duration=180)
            return
        self.clipboard_clear()
        self.clipboard_append(out)
        animate_label_fade(self.status_label, "Output copied to clipboard", duration=160)

    def _load_file(self):
        path = filedialog.askopenfilename(title="Open encrypted / text file", filetypes=[("Text files","*.txt"), ("All files","*.*")])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", content)
            animate_label_fade(self.status_label, f"Loaded: {os.path.basename(path)}", duration=200)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def _save_file(self):
        out = self.output_text.get("1.0", "end").rstrip('\n')
        if not out:
            messagebox.showwarning("Empty output", "No output to save. Run an operation first.")
            return
        path = filedialog.asksaveasfilename(title="Save output to file", defaultextension=".txt",
                                            filetypes=[("Text files","*.txt"), ("All files","*.*")])
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(out)
            animate_label_fade(self.status_label, f"Saved to: {os.path.basename(path)}", duration=200)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")


# -------------------------
# Run the application
# -------------------------
if __name__ == "__main__":
    # Ensure customtkinter uses modern look
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = CaesarApp()
    app.mainloop()
