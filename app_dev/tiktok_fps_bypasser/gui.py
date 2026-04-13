"""Graphical interface for the TikTok FPS Compression Bypasser."""

from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
import webbrowser
from datetime import datetime

import customtkinter as ctk
from customtkinter.windows.widgets.core_rendering.ctk_canvas import CTkCanvas
from tkinter import filedialog, messagebox

from .localization import TRANSLATIONS, detect_language
from .secure_api import BACKEND_NAME, get_scale_factor_from_fps, get_video_fps, patch_mp4

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD

    DND_BASE = TkinterDnD.Tk
    DND_AVAILABLE = True
except Exception:
    DND_FILES = None
    DND_BASE = ctk.CTk
    DND_AVAILABLE = False


def _normalize_tk_dimension(value):
    if isinstance(value, (int, float)):
        return int(round(value))

    if isinstance(value, str):
        try:
            return str(int(round(float(value))))
        except ValueError:
            return value

    return value


def _patch_customtkinter_canvas_dimensions():
    if getattr(CTkCanvas, "_lenoz7_dimension_patch", False):
        return

    original_init = CTkCanvas.__init__
    original_configure = CTkCanvas.configure

    def _normalize_kwargs(kwargs):
        normalized = dict(kwargs)
        for key in ("width", "height", "bd", "borderwidth", "highlightthickness"):
            if key in normalized:
                normalized[key] = _normalize_tk_dimension(normalized[key])
        return normalized

    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **_normalize_kwargs(kwargs))

    def patched_configure(self, *args, **kwargs):
        return original_configure(self, *args, **_normalize_kwargs(kwargs))

    CTkCanvas.__init__ = patched_init
    CTkCanvas.configure = patched_configure
    CTkCanvas.config = patched_configure
    CTkCanvas._lenoz7_dimension_patch = True


_patch_customtkinter_canvas_dimensions()


def human_size(num):
    for unit in ["B", "KB", "MB", "GB"]:
        if num < 1024.0:
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} TB"


class GlassPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        defaults = dict(
            fg_color=("#FFFFFF", "#111114"),
            border_width=1,
            border_color=("#D8D8D8", "#27272A"),
            corner_radius=22,
        )
        defaults.update(kwargs)
        super().__init__(master, **defaults)


class App(DND_BASE):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.lang = detect_language()
        self.t = TRANSLATIONS[self.lang]

        self.title(self.t["title"])
        self.geometry("980x680")
        self.minsize(980, 680)
        self.bg_base = "#07111F"
        self.bg_top = "#10233F"
        self.bg_bottom = "#070B12"
        self.glow_primary = "#1D4ED8"
        self.glow_secondary = "#F97316"
        self.panel_fill = "#0E1726"
        self.panel_stroke = "#223049"
        self.panel_inner = "#111C2D"
        self.panel_console = "#0A1422"
        self.input_fill = "#0C1524"
        self.input_stroke = "#24344A"
        self.button_fill = "#172235"
        self.button_hover = "#24344C"
        self.configure(bg=self.bg_base)
        self.fg_color = self.bg_base

        self.input_path = ""
        self.output_path = ""
        self.last_fps = None

        self.accent = "#F97316"
        self.accent_hover = "#EA580C"
        self.text_main = "#F4F4F5"
        self.text_soft = "#93A4BC"
        self.bg_canvas = None

        self._build_background()
        self._build_ui()
        self.bind("<Configure>", self._on_window_resize)

    def _build_background(self):
        self.bg_canvas = tk.Canvas(self, highlightthickness=0, bd=0, relief="flat")
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_canvas.tk.call("lower", self.bg_canvas._w)
        self.after(10, self._draw_background)

    def _hex_to_rgb(self, value):
        value = value.lstrip("#")
        return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))

    def _rgb_to_hex(self, rgb):
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    def _blend(self, start, end, ratio):
        start_rgb = self._hex_to_rgb(start)
        end_rgb = self._hex_to_rgb(end)
        mixed = tuple(int(start_rgb[index] + (end_rgb[index] - start_rgb[index]) * ratio) for index in range(3))
        return self._rgb_to_hex(mixed)

    def _draw_glow(self, x0, y0, x1, y1, color, steps=8):
        for step in range(steps, 0, -1):
            ratio = step / steps
            inset_x = (x1 - x0) * (1 - ratio) * 0.5
            inset_y = (y1 - y0) * (1 - ratio) * 0.5
            fill = self._blend(self.bg_bottom, color, ratio * 0.28)
            self.bg_canvas.create_oval(
                x0 + inset_x,
                y0 + inset_y,
                x1 - inset_x,
                y1 - inset_y,
                fill=fill,
                outline="",
            )

    def _draw_background(self):
        if self.bg_canvas is None:
            return

        width = max(self.winfo_width(), 980)
        height = max(self.winfo_height(), 680)
        self.bg_canvas.delete("all")
        self.bg_canvas.configure(bg=self.bg_bottom)

        bands = 90
        for index in range(bands):
            ratio = index / max(bands - 1, 1)
            color = self._blend(self.bg_top, self.bg_bottom, ratio)
            y0 = int(height * index / bands)
            y1 = int(height * (index + 1) / bands) + 2
            self.bg_canvas.create_rectangle(0, y0, width, y1, fill=color, outline="")

        self._draw_glow(width * 0.52, -height * 0.10, width * 1.08, height * 0.58, self.glow_primary)
        self._draw_glow(-width * 0.10, height * 0.08, width * 0.44, height * 0.78, self.glow_secondary)

        self.bg_canvas.create_polygon(
            0,
            height * 0.70,
            width * 0.30,
            height * 0.52,
            width * 0.62,
            height * 0.72,
            width,
            height * 0.48,
            width,
            height,
            0,
            height,
            fill=self._blend(self.bg_bottom, "#0F1B2E", 0.55),
            outline="",
        )

    def _on_window_resize(self, event):
        if event.widget is self:
            self._draw_background()

    def _build_ui(self):
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=24, pady=24)

        header = ctk.CTkFrame(root, fg_color="transparent")
        header.pack(fill="x", pady=(0, 18))

        left_head = ctk.CTkFrame(header, fg_color="transparent")
        left_head.pack(side="left", fill="x", expand=True)

        title = ctk.CTkLabel(
            left_head,
            text=self.t["title"],
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=self.text_main,
        )
        title.pack(anchor="w")

        repo_btn = ctk.CTkButton(
            header,
            text=self.t["repo"],
            height=40,
            fg_color=self.button_fill,
            hover_color=self.button_hover,
            corner_radius=14,
            command=self.open_repo,
        )
        repo_btn.pack(side="right", padx=(16, 0), pady=8)

        content = ctk.CTkFrame(root, fg_color="transparent")
        content.pack(fill="both", expand=True)

        left = GlassPanel(content, width=390, fg_color=self.panel_fill, border_color=self.panel_stroke)
        left.pack(side="left", fill="y", padx=(0, 16))
        left.pack_propagate(False)

        right = GlassPanel(content, fg_color=self.panel_fill, border_color=self.panel_stroke)
        right.pack(side="left", fill="both", expand=True)

        self._build_left_panel(left)
        self._build_right_panel(right)

        footer = ctk.CTkLabel(
            root,
            text=self.t["tip"],
            font=ctk.CTkFont(size=12),
            text_color="#6B7280",
        )
        footer.pack(anchor="w", pady=(14, 0))

    def _build_left_panel(self, parent):
        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.pack(fill="x", padx=22, pady=(22, 10))

        info_title = ctk.CTkLabel(
            top,
            text=self.t["input_output"],
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.text_main,
        )
        info_title.pack(anchor="w")

        drop_hint = self.t["drag_hint"] if DND_AVAILABLE else self.t["drag_hint_no_dnd"]

        info_desc = ctk.CTkLabel(
            top,
            text=drop_hint,
            font=ctk.CTkFont(size=13),
            wraplength=340,
            justify="left",
            text_color=self.text_soft,
        )
        info_desc.pack(anchor="w", pady=(8, 0))

        self.drop_frame = GlassPanel(parent, height=108, fg_color=self.panel_inner, border_color=self.panel_stroke)
        self.drop_frame.pack(fill="x", padx=18, pady=(8, 14))
        self.drop_frame.pack_propagate(False)

        self.drop_label = ctk.CTkLabel(
            self.drop_frame,
            text=drop_hint,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#D7E5F6",
            justify="center",
            cursor="hand2",
        )
        self.drop_label.pack(expand=True)
        self.drop_frame.configure(cursor="hand2")

        for widget in (self.drop_frame, self.drop_label):
            widget.bind("<Button-1>", self._browse_input_from_card)

        self.input_entry = self._entry_block(parent, self.t["input_label"], self.t["input_placeholder"], self.browse_input)
        self.output_entry = self._entry_block(parent, self.t["output_label"], self.t["output_placeholder"], self.browse_output)
        self.fps_entry = self._entry_block(parent, self.t["fps_label"], self.t["fps_placeholder"], None)

        action_row = ctk.CTkFrame(parent, fg_color="transparent")
        action_row.pack(fill="x", padx=22, pady=(10, 8))

        self.auto_btn = ctk.CTkButton(
            action_row,
            text=self.t["auto"],
            height=42,
            fg_color=self.button_fill,
            hover_color=self.button_hover,
            corner_radius=14,
            command=self.auto_detect_fps,
        )
        self.auto_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.clear_btn = ctk.CTkButton(
            action_row,
            text=self.t["clear"],
            width=100,
            height=42,
            fg_color="#121A28",
            hover_color="#1C273A",
            corner_radius=14,
            command=self.clear_all,
        )
        self.clear_btn.pack(side="left")

        self.patch_btn = ctk.CTkButton(
            parent,
            text=self.t["apply"],
            height=54,
            fg_color=self.accent,
            hover_color=self.accent_hover,
            corner_radius=16,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.start_patch,
        )
        self.patch_btn.pack(fill="x", padx=22, pady=(10, 18))

        stats = GlassPanel(parent, fg_color=self.panel_inner, border_color=self.panel_stroke)
        stats.pack(fill="x", padx=18, pady=(0, 18))

        stats_title = ctk.CTkLabel(
            stats,
            text=self.t["live_stats"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.text_main,
        )
        stats_title.pack(anchor="w", padx=16, pady=(14, 6))

        self.stats_label = ctk.CTkLabel(
            stats,
            text=self.t["no_file_loaded"],
            font=ctk.CTkFont(size=13),
            justify="left",
            wraplength=320,
            text_color=self.text_soft,
        )
        self.stats_label.pack(anchor="w", padx=16, pady=(0, 14))

        if DND_AVAILABLE:
            for widget in (self.drop_frame, self.drop_label):
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind("<<Drop>>", self.handle_drop)

    def _build_right_panel(self, parent):
        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.pack(fill="x", padx=22, pady=(22, 12))

        title = ctk.CTkLabel(
            top,
            text=self.t["console"],
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.text_main,
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            top,
            text=self.t["console_sub"],
            font=ctk.CTkFont(size=13),
            text_color=self.text_soft,
        )
        subtitle.pack(anchor="w", pady=(6, 0))

        console = GlassPanel(parent, fg_color=self.panel_console, border_color=self.panel_stroke)
        console.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        console_head = ctk.CTkFrame(console, fg_color="transparent")
        console_head.pack(fill="x", padx=16, pady=(14, 8))

        ctk.CTkLabel(
            console_head,
            text=self.t["output"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.text_main,
        ).pack(side="left")

        btn_row = ctk.CTkFrame(console_head, fg_color="transparent")
        btn_row.pack(side="right")

        self.clear_log_btn = ctk.CTkButton(
            btn_row,
            text=self.t["clear"],
            width=92,
            height=30,
            fg_color=self.button_fill,
            hover_color=self.button_hover,
            corner_radius=10,
            command=self.clear_log,
        )
        self.clear_log_btn.pack(side="left", padx=(0, 8))

        self.status_dot = ctk.CTkLabel(
            btn_row,
            text=f"● {self.t['ready']}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#34D399",
        )
        self.status_dot.pack(side="left")

        self.log_text = ctk.CTkTextbox(
            console,
            fg_color="#08111D",
            border_width=1,
            border_color=self.panel_stroke,
            corner_radius=14,
            text_color="#E5E7EB",
            font=ctk.CTkFont(family="Consolas", size=13),
        )
        self.log_text.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.log_text.configure(state="disabled")

    def _entry_block(self, parent, label, placeholder, browse_command):
        block = ctk.CTkFrame(parent, fg_color="transparent")
        block.pack(fill="x", padx=22, pady=(8, 0))

        ctk.CTkLabel(
            block,
            text=label,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.text_main,
        ).pack(anchor="w", pady=(0, 6))

        row = ctk.CTkFrame(block, fg_color="transparent")
        row.pack(fill="x")

        entry = ctk.CTkEntry(
            row,
            placeholder_text=placeholder,
            height=42,
            fg_color=self.input_fill,
            border_color=self.input_stroke,
            corner_radius=14,
            text_color=self.text_main,
        )
        entry.pack(side="left", fill="x", expand=True)

        button = None
        if browse_command is not None:
            button = ctk.CTkButton(
                row,
                text=self.t["browse"],
                width=90,
                height=42,
                fg_color=self.button_fill,
                hover_color=self.button_hover,
                corner_radius=14,
                command=browse_command,
            )
            button.pack(side="left", padx=(10, 0))

        wrapper = type("EntryBlock", (), {})()
        wrapper.frame = block
        wrapper.row = row
        wrapper.entry = entry
        wrapper.button = button
        return wrapper

    def _set_ready(self, ready=True, text=None, color="#34D399"):
        label = text or self.t["ready"]
        self.status_dot.configure(text=f"● {label}", text_color=color)
        self.patch_btn.configure(state="normal" if ready else "disabled")

    def _log(self, message):
        self.log_text.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self._log(self.t["log_cleared"])

    def browse_input(self):
        path = filedialog.askopenfilename(
            title=self.t["input_label"],
            filetypes=[("Video files", "*.mp4 *.mov *.m4v"), ("All files", "*.*")],
        )
        if path:
            self.load_input(path)

    def _browse_input_from_card(self, _event=None):
        self.browse_input()

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            title=self.t["output_label"],
            defaultextension=".mp4",
            filetypes=[("MP4 video", "*.mp4"), ("All files", "*.*")],
        )
        if not path:
            return

        self.output_path = path
        self.output_entry.entry.delete(0, "end")
        self.output_entry.entry.insert(0, path)
        self._log(f"{self.t['output_path_set']}: {os.path.basename(path)}")

    def load_input(self, path):
        self.input_path = path
        self.input_entry.entry.delete(0, "end")
        self.input_entry.entry.insert(0, path)

        base, extension = os.path.splitext(path)
        suggested = f"{base}_patched{extension or '.mp4'}"
        self.output_path = suggested
        self.output_entry.entry.delete(0, "end")
        self.output_entry.entry.insert(0, suggested)

        fps = get_video_fps(path)
        self.last_fps = fps
        if fps:
            self.fps_entry.entry.delete(0, "end")
            self.fps_entry.entry.insert(0, str(fps))
            fps_text = f"{self.t['detected']}: {fps}"
        else:
            fps_text = f"{self.t['detected']}: {self.t['ffprobe_unavailable']}"

        try:
            size = human_size(os.path.getsize(path))
            file_name = os.path.basename(path)
            self.stats_label.configure(text=f"File: {file_name}\nSize: {size}\n{fps_text}")
        except Exception:
            self.stats_label.configure(text=f"File: {os.path.basename(path)}\n{fps_text}")

        self.clear_log()
        self._log(f"{self.t['file_loaded']}: {os.path.basename(path)}")
        self._log(fps_text)
        self._log(f"Secure backend: {BACKEND_NAME}")

    def handle_drop(self, event):
        try:
            paths = self.tk.splitlist(event.data)
            if not paths:
                return
            raw = paths[0]
            if raw.startswith("{") and raw.endswith("}"):
                raw = raw[1:-1]
            self.load_input(raw)
        except Exception as exc:
            self._log(f"{self.t['drop_failed']}: {exc}")

    def auto_detect_fps(self):
        if not self.input_path:
            messagebox.showwarning(self.t["no_input_title"], self.t["missing_input"])
            return

        fps = get_video_fps(self.input_path)
        if fps:
            self.last_fps = fps
            self.fps_entry.entry.delete(0, "end")
            self.fps_entry.entry.insert(0, str(fps))
            self._log(f"{self.t['detected']}: {fps}")
        else:
            self._log(self.t["detect_failed"])
            messagebox.showerror(self.t["detection_failed_title"], self.t["detect_failed"])

    def clear_all(self):
        self.input_path = ""
        self.output_path = ""
        self.last_fps = None
        for block in [self.input_entry, self.output_entry, self.fps_entry]:
            block.entry.delete(0, "end")
        self.stats_label.configure(text=self.t["no_file_loaded"])
        self.clear_log()
        self._set_ready(True)
        self._log(self.t["cleared"])

    def start_patch(self):
        input_path = self.input_entry.entry.get().strip()
        output_path = self.output_entry.entry.get().strip()
        fps_value = self.fps_entry.entry.get().strip()
        manual_mode = bool(fps_value)

        if not input_path:
            messagebox.showwarning(self.t["missing_input_title"], self.t["missing_input"])
            return
        if not output_path:
            messagebox.showwarning(self.t["missing_output_title"], self.t["missing_output"])
            return
        if not os.path.exists(input_path):
            messagebox.showerror(self.t["invalid_input_title"], self.t["invalid_input"])
            return

        scale_factor = None
        selected_fps = None
        if manual_mode:
            try:
                selected_fps = float(fps_value)
                if selected_fps <= 0:
                    raise ValueError
                scale_factor = get_scale_factor_from_fps(selected_fps)
            except ValueError:
                messagebox.showerror(self.t["invalid_fps_title"], self.t["invalid_fps"])
                return
        else:
            selected_fps = get_video_fps(input_path)
            scale_factor = get_scale_factor_from_fps(selected_fps)
            if scale_factor is None:
                messagebox.showerror(self.t["fps_detection_failed_title"], self.t["missing_detected_fps"])
                return
            self.last_fps = selected_fps
            self.fps_entry.entry.delete(0, "end")
            self.fps_entry.entry.insert(0, str(selected_fps))

        self.clear_log()
        self._set_ready(False, self.t["processing"], "#F59E0B")
        self._log(self.t["start"])
        self._log(f"Input: {os.path.basename(input_path)}")
        self._log(f"Output: {os.path.basename(output_path)}")
        self._log(self.t["mode_manual"] if manual_mode else self.t["mode_auto"])
        self._log(f"Original FPS: {selected_fps}")
        self._log(f"Scale factor: {scale_factor}")

        try:
            success = patch_mp4(input_path, output_path, scale_factor=scale_factor, log_func=self._log)
            if success:
                self._log(self.t["success"])
                self._set_ready(True, self.t["done"], "#34D399")
                self._ask_open_folder(output_path)
            else:
                self._log(self.t["nothing_patched"])
                self._set_ready(True, self.t["ready"], "#34D399")
                messagebox.showwarning(self.t["nothing_patched_title"], self.t["nothing_patched"])
        except Exception as exc:
            self._log(f"Error: {exc}")
            self._set_ready(True, self.t["ready"], "#34D399")
            messagebox.showerror(self.t["patch_failed_title"], str(exc))

    def _ask_open_folder(self, output_path):
        if messagebox.askyesno(self.t["finished_title"], self.t["open_folder"]):
            self.open_folder(output_path)

    def open_folder(self, filepath):
        folder = os.path.dirname(filepath)
        try:
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.call(["open", folder])
            else:
                subprocess.call(["xdg-open", folder])
        except Exception as exc:
            messagebox.showerror("Open folder failed", str(exc))

    def open_repo(self):
        webbrowser.open("https://github.com/LuisAlves10/TikTok-FPS-Compression-Bypasser")


def main():
    app = App()
    app.mainloop()
