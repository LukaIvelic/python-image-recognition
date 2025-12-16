# 🖐️ AI Hand Gesture & Mouse Control

> **Control your computer with Minority Report-style hand gestures.**  
> Powered by MediaPipe & OpenCV.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-orange) ![License](https://img.shields.io/badge/License-MIT-green)

A high-performance, modular Python application that turns your webcam into a precision mouse controller. Experience lag-free cursor movement, intuitive clicking, and a built-in virtual whiteboard for drawing on your screen.

---

## ✨ Features

- **🖱️ Precision Mouse Control**: 
  - **OneEuroFilter Smoothing**: Advanced jitter reduction for "sticky" cursor feel.
  - **Failsafe Protection**: Crash-proof implementation (prevents PyAutoGUI failsafe errors).
- **🔫 Advanced Gestures**:
  - **Gun Gesture (Thumb+Index)**: Double Click (now with geometry validation to prevent accidental triggers).
  - **Pinch (Thumb+Index)**: Left Click / Drag.
  - **Peace Sign**: Scroll mode.
- **🎨 Virtual Drawing Mode**:
  - Draw on screen with your index finger.
  - **Solid Ink**: 100% opacity drawing lines (Pink/Green/Blue) that stand out.
  - **Eraser**: Use your open hand to wipe the canvas.
- **👁️ Robust AI Vision**:
  - **Saturation Boost**: Automatically enhances colors to track hands against complex backgrounds (e.g., skin-tone walls).
  - **CLAHE Enhancement**: Smart contrast adjustment for varied lighting.
  - **Model Complexity 1**: Uses the high-accuracy MediaPipe model.
- **🪞 Smart UX**:
  - **Mirror Mode**: Natural interaction.
  - **Visual Feedback**: Real-time HUD showing detected gestures and confidence.

---

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- A Webcam

### Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/LukaIvelic/python-image-recognition.git
   cd python-image-recognition
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: On macOS, you might need to grant Terminal/VSCode permission to access the Camera and Accessibility (for mouse control) in System Settings.*

---

## 🚀 Usage

Run the main application:
```bash
python main.py
```

### 🎮 Controls & Gestures

| Gesture | Fingers |  Action |
|:---:|:---|:---|
| **POINT** | ☝️ Index Finger | **Move Cursor** |
| **PINCH** | 👌 Thumb + Index (Touch) | **Left Click (Hold to Drag)** |
| **GUN** | 🔫 Thumb + Index (Extended) | **Double Click** |
| **PEACE** | ✌️ Index + Middle | **Scroll Mode** (Move hand Up/Down) |
| **SCROLL** | 🤟 3 Fingers | **Scroll Mode** (Alternative) |
| **DRAW** | Press `d` on keyboard | **Toggle Drawing Mode** |
| **STOP** | 🖐️ Open Hand | **Stop / Eraser (in Draw Mode)** |

### ⌨️ Keyboard Shortcuts
- **`q`**: Quit application
- **`d`**: Toggle Drawing Mode / Mouse Mode
- **`c`**: Clear Drawing Canvas

---

## ⚙️ Configuration

You can fine-tune the experience in `config/config.py`.

**Key Settings:**
```python
# Sensitivity
MOUSE_SMOOTHING = 0.5   # Higher = Smoother but more lag
SCROLL_AMOUNT = 50      # Pixels per scroll step

# Detection
MIN_DETECTION_CONFIDENCE = 0.8  # Stricter detection
MODEL_COMPLEXITY = 1            # 0=Fast, 1=Accurate

# Visuals
DRAWING_OPACITY = 1.0   # 1.0 = Non-transparent lines
```

---

## 🏗️ Project Structure
```
.
├── config/             # Settings & Gesture Definitions
├── src/                # Core Logic
│   ├── app.py          # Main Loop
│   ├── hand_detector.py# MediaPipe + Image Enhancement (CLAHE/HSV)
│   ├── gesture_recognizer.py # Geometry-based gesture logic
│   ├── mouse_controller.py   # Mouse inputs & Smoothing
│   ├── visualizer.py   # Visualization Manager
│   ├── ui/             # UI Components
│   │   └── hud.py      # Heads-Up Display & Overlays
│   └── utils/          # Utilities
│       └── geometry.py # Coordinate Mapping Math
├── main.py             # Entry Point
└── requirements.txt    # Dependencies
```

---

## ⚠️ Safety & Privacy
- **Processing is local**: No video is sent to the cloud.
- **Failsafe**: If the mouse gets stuck or goes out of control, slam your real mouse to the corner of the screen to trigger the OS safety abort (or press `q`).

---

## 📜 License
MIT License. Free to use and modify.
