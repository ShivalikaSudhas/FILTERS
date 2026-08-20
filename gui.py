"""
gui.py - Tkinter Desktop Graphical Interface for EdgeCam
--------------------------------------------------------
Provides a modern dark-mode GUI with responsive video preview, parameter sliders,
Reset Sliders button, delay timers, recording/screenshot controls, fullscreen support, and keyboard shortcuts.
"""

import os
import time
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import cv2
import numpy as np
from PIL import Image, ImageTk

from camera import CameraManager
from filters import EdgeFilter, BaseFilter
from recorder import VideoRecorder


class EdgeCamGUI:
    """
    Main Application Window and GUI Manager.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("EdgeCam")
        self.root.geometry("1024x720")
        self.root.minsize(800, 600)

        # Apply dark theme styling
        self._setup_styles()

        # Initialize Camera & Recorder
        self.camera = CameraManager(0)
        self.recorder = VideoRecorder("recordings")
        
        # Pure Edge Detection Filter
        self.active_filter = EdgeFilter(blur_kernel=5, threshold1=50, threshold2=120)

        # Delay Timer State (0, 3, or 5 seconds)
        self.delay_var = tk.IntVar(value=0)
        self.countdown_active = False
        self.countdown_target_action = None  # "screenshot" or "record"
        self.countdown_remaining = 0
        self.countdown_start_time = 0.0

        # UI & Display State
        self.is_fullscreen = False
        self.last_status_msg = "Ready"
        self.status_msg_expire = 0.0
        self.fps_tracker = time.time()
        self.frame_count = 0
        self.display_fps = 0.0

        # Build Interface Layout
        self._build_ui()
        self._bind_shortcuts()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start Video Rendering Loop
        self.update_frame()

    def _setup_styles(self):
        """Sets dark color scheme and ttk styles."""
        self.bg_color = "#181825"
        self.surface_color = "#1e1e2e"
        self.panel_color = "#313244"
        self.accent_blue = "#89b4fa"
        self.accent_red = "#f38ba8"
        self.accent_green = "#a6e3a1"
        self.accent_yellow = "#f9e2af"
        self.text_color = "#cdd6f4"
        self.subtext_color = "#bac2de"

        self.root.configure(bg=self.bg_color)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=self.surface_color)
        style.configure("Panel.TFrame", background=self.panel_color)
        style.configure("TLabel", background=self.surface_color, foreground=self.text_color, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=self.surface_color, foreground=self.accent_blue, font=("Segoe UI", 14, "bold"))
        style.configure("Status.TLabel", background=self.surface_color, foreground=self.subtext_color, font=("Segoe UI", 9))
        
        style.configure("TScale", background=self.surface_color, troughcolor=self.panel_color)
        style.configure("TRadiobutton", background=self.surface_color, foreground=self.text_color, font=("Segoe UI", 10))
        style.map("TRadiobutton", background=[("active", self.surface_color)], foreground=[("active", self.accent_blue)])

    def _build_ui(self):
        """Constructs the GUI component hierarchy."""
        # Top Header Bar (stored as instance var for fullscreen hide/show)
        self.header_frame = ttk.Frame(self.root, padding=(15, 8))
        self.header_frame.pack(fill=tk.X, side=tk.TOP)

        title_label = ttk.Label(self.header_frame, text="⚡ EdgeCam - Edge Detection Studio", style="Header.TLabel")
        title_label.pack(side=tk.LEFT)

        self.fps_label = ttk.Label(self.header_frame, text="FPS: 0", style="Status.TLabel")
        self.fps_label.pack(side=tk.RIGHT)

        # Central Video Canvas Container (stored for fullscreen padding changes)
        self.canvas_frame = tk.Frame(self.root, bg="#000000")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Control Panel Container (stored as instance var for fullscreen hide/show)
        self.controls_container = ttk.Frame(self.root, padding=10)
        self.controls_container.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=4)

        # Top Control Row: Action Buttons & Delay Selector
        actions_row = ttk.Frame(self.controls_container)
        actions_row.pack(fill=tk.X, pady=(0, 6))

        self.record_btn = tk.Button(
            actions_row, text="🔴 Record", bg="#313244", fg=self.accent_red,
            activebackground="#45475a", activeforeground=self.accent_red,
            font=("Segoe UI", 11, "bold"), bd=0, padx=16, pady=6,
            command=self.trigger_record_action, cursor="hand2"
        )
        self.record_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.snap_btn = tk.Button(
            actions_row, text="📸 Screenshot", bg="#313244", fg=self.accent_green,
            activebackground="#45475a", activeforeground=self.accent_green,
            font=("Segoe UI", 11, "bold"), bd=0, padx=16, pady=6,
            command=self.trigger_screenshot_action, cursor="hand2"
        )
        self.snap_btn.pack(side=tk.LEFT, padx=(0, 15))

        # Delay Selector Radio Group
        delay_label = ttk.Label(actions_row, text="⏱️ Timer Delay:")
        delay_label.pack(side=tk.LEFT, padx=(0, 5))

        for delay_val, label_text in [(0, "Direct (0s)"), (3, "3s Delay"), (5, "5s Delay")]:
            rb = ttk.Radiobutton(
                actions_row, text=label_text, value=delay_val, variable=self.delay_var
            )
            rb.pack(side=tk.LEFT, padx=4)

        # Fullscreen Toggle Button
        self.fs_btn = tk.Button(
            actions_row, text="⛶ Fullscreen", bg="#313244", fg=self.accent_blue,
            activebackground="#45475a", activeforeground=self.accent_blue,
            font=("Segoe UI", 10, "bold"), bd=0, padx=12, pady=6,
            command=self.toggle_fullscreen, cursor="hand2"
        )
        self.fs_btn.pack(side=tk.RIGHT)

        # Middle Control Row: Parameter Sliders & Reset Button
        sliders_row = ttk.Frame(self.controls_container)
        sliders_row.pack(fill=tk.X, pady=(0, 6))

        # Canny Threshold 1 Slider
        t1_frame = ttk.Frame(sliders_row)
        t1_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(t1_frame, text="Canny Threshold 1:").pack(side=tk.LEFT)
        self.t1_val_label = ttk.Label(t1_frame, text="50", width=4)
        self.t1_val_label.pack(side=tk.RIGHT)
        self.t1_slider = ttk.Scale(t1_frame, from_=0, to=255, value=50, command=self._on_threshold1_change)
        self.t1_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        # Canny Threshold 2 Slider
        t2_frame = ttk.Frame(sliders_row)
        t2_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(t2_frame, text="Canny Threshold 2:").pack(side=tk.LEFT)
        self.t2_val_label = ttk.Label(t2_frame, text="120", width=4)
        self.t2_val_label.pack(side=tk.RIGHT)
        self.t2_slider = ttk.Scale(t2_frame, from_=0, to=255, value=120, command=self._on_threshold2_change)
        self.t2_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        # Gaussian Blur Slider
        blur_frame = ttk.Frame(sliders_row)
        blur_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(blur_frame, text="Blur Kernel:").pack(side=tk.LEFT)
        self.blur_val_label = ttk.Label(blur_frame, text="5", width=3)
        self.blur_val_label.pack(side=tk.RIGHT)
        self.blur_slider = ttk.Scale(blur_frame, from_=1, to=15, value=5, command=self._on_blur_change)
        self.blur_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        # Reset Sliders Button
        self.reset_btn = tk.Button(
            sliders_row, text="🔄 Reset Sliders", bg="#313244", fg=self.accent_yellow,
            activebackground="#45475a", activeforeground=self.accent_yellow,
            font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=4,
            command=self.reset_sliders, cursor="hand2"
        )
        self.reset_btn.pack(side=tk.RIGHT)

        # Bottom Row: Status Bar
        bottom_row = ttk.Frame(self.controls_container)
        bottom_row.pack(fill=tk.X)

        self.status_label = ttk.Label(
            bottom_row, text="Ready  |  R: Record   S: Screenshot   F: Fullscreen (Esc to exit)", style="Status.TLabel"
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _bind_shortcuts(self):
        """Binds keyboard shortcuts. Close using the window X button."""
        self.root.bind("<Key-r>", lambda e: self.trigger_record_action())
        self.root.bind("<Key-R>", lambda e: self.trigger_record_action())
        self.root.bind("<Key-s>", lambda e: self.trigger_screenshot_action())
        self.root.bind("<Key-S>", lambda e: self.trigger_screenshot_action())
        self.root.bind("<Key-f>", lambda e: self.toggle_fullscreen())
        self.root.bind("<Key-F>", lambda e: self.toggle_fullscreen())
        self.root.bind("<Escape>", lambda e: self.exit_fullscreen())

    def set_status(self, msg: str, duration: float = 4.0):
        """Sets temporary status bar message."""
        self.last_status_msg = msg
        self.status_msg_expire = time.time() + duration
        self.status_label.config(text=f"Status: {msg}")

    def reset_sliders(self):
        """Resets all parameter sliders back to standard default values."""
        self.t1_slider.set(50)
        self.t2_slider.set(120)
        self.blur_slider.set(5)
        self._on_threshold1_change(50)
        self._on_threshold2_change(120)
        self._on_blur_change(5)
        self.set_status("🔄 Sliders reset to defaults (T1: 50, T2: 120, Blur: 5)")

    # Slider Handlers
    def _on_threshold1_change(self, val):
        t1 = int(float(val))
        self.t1_val_label.config(text=str(t1))
        self.active_filter.set_thresholds(t1, self.active_filter.threshold2)

    def _on_threshold2_change(self, val):
        t2 = int(float(val))
        self.t2_val_label.config(text=str(t2))
        self.active_filter.set_thresholds(self.active_filter.threshold1, t2)

    def _on_blur_change(self, val):
        k = int(float(val))
        k = k if k % 2 != 0 else k + 1
        self.blur_val_label.config(text=str(k))
        self.active_filter.set_blur(k)

    # Action Handlers with Delay Timer Support
    def trigger_screenshot_action(self):
        delay = self.delay_var.get()
        if delay == 0:
            self.take_screenshot()
        else:
            self.start_countdown(delay, "screenshot")

    def trigger_record_action(self):
        if self.recorder.is_recording:
            self.stop_recording()
        else:
            delay = self.delay_var.get()
            if delay == 0:
                self.start_recording()
            else:
                self.start_countdown(delay, "record")

    def start_countdown(self, seconds: int, action: str):
        if self.countdown_active:
            return
        self.countdown_active = True
        self.countdown_remaining = seconds
        self.countdown_target_action = action
        self.countdown_start_time = time.time()
        self.set_status(f"Countdown started: {action.capitalize()} in {seconds}s...")

    def update_countdown(self):
        if not self.countdown_active:
            return

        elapsed = time.time() - self.countdown_start_time
        remaining = self.countdown_remaining - int(elapsed)

        if remaining <= 0:
            self.countdown_active = False
            action = self.countdown_target_action
            self.countdown_target_action = None
            if action == "screenshot":
                self.take_screenshot()
            elif action == "record":
                self.start_recording()

    def take_screenshot(self):
        frame = self.camera.get_frame()
        if frame is None:
            self.set_status("Screenshot failed: No camera frame!")
            return

        processed = self.active_filter.apply(frame)

        os.makedirs("screenshots", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join("screenshots", f"EdgeCam_Snap_{timestamp}.png")
        
        cv2.imwrite(filepath, processed)
        self.set_status(f"📸 Screenshot saved to {filepath}", duration=5.0)

    def start_recording(self):
        if not self.camera.is_opened:
            self.set_status("Cannot record: Camera offline!")
            return

        w, h = self.camera.frame_width, self.camera.frame_height
        fps = self.camera.fps if self.camera.fps > 0 else 30.0
        
        filepath = self.recorder.start(w, h, fps)
        self.record_btn.config(text="⏹️ Stop Rec", bg=self.accent_red, fg="#000000")
        self.set_status(f"🔴 Recording started -> {filepath}")

    def stop_recording(self):
        filepath = self.recorder.stop()
        self.record_btn.config(text="🔴 Record", bg="#313244", fg=self.accent_red)
        if filepath:
            self.set_status(f"✅ Video saved to {filepath}", duration=6.0)

    # Fullscreen Logic
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        if self.is_fullscreen:
            # Hide header and controls so video fills edge-to-edge
            self.header_frame.pack_forget()
            self.controls_container.pack_forget()
            self.canvas_frame.pack_configure(padx=0, pady=0)
            self.fs_btn.config(text="Exit Fullscreen")
        else:
            self._restore_normal_layout()

    def exit_fullscreen(self):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)
            self._restore_normal_layout()

    def _restore_normal_layout(self):
        """Restores header and control panels after exiting fullscreen."""
        # Re-pack header at top
        self.header_frame.pack(fill=tk.X, side=tk.TOP, before=self.canvas_frame)
        # Re-pack controls at bottom
        self.controls_container.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=4)
        # Restore canvas padding
        self.canvas_frame.pack_configure(padx=15, pady=5)
        self.fs_btn.config(text="⛶ Fullscreen")

    # Main Rendering Loop
    def update_frame(self):
        self.frame_count += 1
        now = time.time()
        if now - self.fps_tracker >= 1.0:
            self.display_fps = self.frame_count / (now - self.fps_tracker)
            self.frame_count = 0
            self.fps_tracker = now
            self.fps_label.config(text=f"FPS: {self.display_fps:.1f}")

        if self.status_msg_expire > 0 and now > self.status_msg_expire:
            self.status_msg_expire = 0.0
            rec_status = "  🔴 RECORDING" if self.recorder.is_recording else ""
            self.status_label.config(
                text=f"Ready{rec_status}  |  R: Record   S: Screenshot   F: Fullscreen (Esc to exit)"
            )

        if self.countdown_active:
            self.update_countdown()

        raw_frame = self.camera.get_frame()

        if raw_frame is not None:
            processed_frame = self.active_filter.apply(raw_frame)

            if self.recorder.is_recording:
                self.recorder.write_frame(processed_frame)

            display_frame = processed_frame.copy()

            if self.recorder.is_recording:
                duration_str = self.recorder.get_duration_formatted()
                cv2.circle(display_frame, (30, 30), 10, (0, 0, 255), -1)
                cv2.putText(
                    display_frame, f"REC {duration_str}", (50, 36),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA
                )

            if self.countdown_active:
                elapsed = time.time() - self.countdown_start_time
                num = max(1, self.countdown_remaining - int(elapsed))
                h, w = display_frame.shape[:2]
                
                overlay = display_frame.copy()
                cv2.circle(overlay, (w // 2, h // 2), 70, (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.6, display_frame, 0.4, 0, display_frame)
                
                text = str(num)
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 3.0, 5)[0]
                tx = (w - text_size[0]) // 2
                ty = (h + text_size[1]) // 2
                cv2.putText(
                    display_frame, text, (tx, ty),
                    cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 255, 255), 5, cv2.LINE_AA
                )

            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()

            if cw > 10 and ch > 10:
                fh, fw = rgb_frame.shape[:2]
                scale = min(cw / fw, ch / fh)
                nw, nh = max(1, int(fw * scale)), max(1, int(fh * scale))

                resized_img = Image.fromarray(rgb_frame).resize((nw, nh), Image.Resampling.BILINEAR)
                self.tk_image = ImageTk.PhotoImage(image=resized_img)

                self.canvas.delete("all")
                cx = (cw - nw) // 2
                cy = (ch - nh) // 2
                self.canvas.create_image(cx, cy, anchor=tk.NW, image=self.tk_image)
        else:
            cw = max(400, self.canvas.winfo_width())
            ch = max(300, self.canvas.winfo_height())
            self.canvas.delete("all")
            self.canvas.create_text(
                cw // 2, ch // 2,
                text="📷 Camera Offline or Initializing...",
                fill="#f38ba8", font=("Segoe UI", 16, "bold")
            )

        self.root.after(16, self.update_frame)

    def on_close(self):
        if self.recorder.is_recording:
            self.recorder.stop()
        self.camera.release()
        self.root.destroy()
