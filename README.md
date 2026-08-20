# ⚡ EdgeCam - Realtime Edge Detection Studio

A simple, polished Windows desktop app that turns your webcam into a live **Canny Edge Detection** studio. Built with Python, OpenCV, Tkinter, and Pillow.

---

## ✨ Features

- **Live Canny Edge Detection** via webcam in real time
- **Dynamic Sliders** — Tune Canny Threshold 1, Threshold 2, and Gaussian Blur Kernel live
- **🔄 Reset Sliders** — One click restores all sliders to clean defaults (T1: 50, T2: 120, Blur: 5)
- **📸 Screenshot** — Save current edge frame as PNG with timestamp
- **🔴 Record** — Record edge-filtered video as `.mp4`
- **⏱️ Timer Delay** — Choose Direct (0s), 3s, or 5s countdown before photo/recording starts, with a visual `3... 2... 1...` overlay
- **⛶ Fullscreen** — Press `F` to go completely edge-to-edge. Press `Esc` to exit fullscreen
- Close the app using the **window X button**

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `R` | Start / Stop Recording |
| `S` | Take Screenshot |
| `F` | Toggle Fullscreen |
| `Esc` | Exit Fullscreen |

---

## 📁 Project Structure

```
EdgeCam/
├── main.py          # App launcher with Windows DPI scaling
├── camera.py        # Threaded webcam capture manager
├── filters.py       # Canny Edge Detection filter pipeline
├── recorder.py      # Async video recording engine (OpenCV VideoWriter)
├── gui.py           # Tkinter dark UI: canvas, sliders, buttons, countdown
├── app.py           # Gradio web app for Hugging Face Spaces deployment
├── requirements.txt # Python dependencies
├── README.md        # This file
└── assets/
    └── icon.ico     # App icon
```

---

## 🚀 Run Locally

```bash
pip install -r requirements.txt
python main.py
```

---

## 📦 Build Standalone Windows `.exe`

```bash
pyinstaller --noconfirm --onedir --windowed --add-data "assets;assets" --icon="assets/icon.ico" --name="EdgeCam" main.py
```

Output: `dist/EdgeCam/EdgeCam.exe` — zip this folder and share it with friends. No Python required on their machine.

---

## 🌐 Deploy to Hugging Face Spaces (Web Version)

The web version uses `app.py` (Gradio) and runs in any browser — no download needed.

### Steps
1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Name it `EdgeCam`, select **Gradio SDK**, visibility **Public**, hardware **Free CPU**
3. Upload `app.py` and `requirements.txt`
4. Done — share the link with friends!

---

## 📤 Push to GitHub

```bash
git init
git add .
git commit -m "Initial EdgeCam release"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/EdgeCam.git
git push -u origin main
```

Then create a **Release** on GitHub and attach the zipped `dist/EdgeCam` folder as a download.

---

## 🛡️ Security Notes

- No API keys or secrets in this project
- No user data is stored or transmitted
- All camera processing happens locally in RAM
- Webcam access is local to each user's device (even on Hugging Face)
