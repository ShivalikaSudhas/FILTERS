# ⚡ EdgeCam - Realtime Computer Vision Studio

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-green.svg)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**EdgeCam** is an open-source, real-time Computer Vision application built with **Python, OpenCV, Tkinter, Pillow, and Gradio**. It provides a sleek, dark-themed interface for real-time **Canny Edge Detection**, featuring dynamic parameter tuning, single-click slider resets, video recording, screenshot snapping, and countdown timers.

---

## 🌐 Live Web Demo

Experience EdgeCam directly in your browser without installing Python:

👉 **[Launch EdgeCam Web App on Hugging Face Spaces](https://huggingface.co/spaces/ShivalikaSudhas/EdgeCam)**

---

## ✨ Features

- **Live Canny Edge Detection**: Real-time webcam frame processing using high-performance OpenCV matrix operations.
- **Dynamic Parameter Tuning**: Real-time sliders for:
  - **Canny Threshold 1** (Lower hysteresis bound: `0–255`)
  - **Canny Threshold 2** (Upper hysteresis bound: `0–255`)
  - **Gaussian Blur Kernel** (Noise filtering: `1–15` odd values)
- **🔄 Single-Click Slider Reset**: Instantly restore default parameters (`T1: 50`, `T2: 120`, `Blur: 5`).
- **📸 High-Res Screenshots**: Save filtered frames to PNG format with timestamped filenames.
- **🔴 Smooth Video Recording**: Record edge-filtered video streams asynchronously into `.mp4` / `.avi` format.
- **⏱️ Visual Countdown Timers**: Choose **Direct (0s)**, **3s Delay**, or **5s Delay** with a centered visual countdown overlay (`3... 2... 1...`).
- **⛶ Immersive Fullscreen**: Toggle full edge-to-edge canvas display (`F` key) and exit with `Esc`.

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
| :---: | :--- |
| **`R`** | Start / Stop Video Recording |
| **`S`** | Capture High-Res Screenshot |
| **`F`** | Toggle Fullscreen Mode |
| **`Esc`** | Exit Fullscreen Mode |

---

## 🛠️ System Architecture

EdgeCam is architected with a non-blocking multi-threaded pipeline:

```text
[ Webcam Hardware ]
        │
        ▼ (Background Thread)
┌─────────────────────────┐
│     CameraManager       │  <-- Thread-safe frame queue & lock
└─────────────────────────┘
        │
        ▼ (BGR Frame Matrix)
┌─────────────────────────┐
│       EdgeFilter        │  <-- Grayscale -> Gaussian Blur -> Canny Edges
└─────────────────────────┘
        │
        ▼ (Processed Frame Matrix)
┌─────────────────────────┐
│      EdgeCamGUI         │  <-- Tkinter Canvas (~60 FPS render loop)
└─────────────────────────┘
        │
        ▼ (Async Queue Write)
┌─────────────────────────┐
│      VideoRecorder      │  <-- Non-blocking cv2.VideoWriter
└─────────────────────────┘
```

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
- Python 3.10 or higher
- A working webcam

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ShivalikaSudhas/FILTERS.git
   cd FILTERS
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the application:
   ```bash
   python main.py
   ```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.
