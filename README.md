# Hand Gesture Mouse Control with MediaPipe

A modular Python application that uses MediaPipe to recognize hand gestures in real-time and control your mouse through intuitive hand movements. Control your computer hands-free with gestures for cursor movement, clicking, and scrolling!

## Features

- **🖱️ Full Mouse Control**: Move cursor, click, scroll - all with hand gestures
- **🎯 Real-time hand detection and tracking**
- **👆 Multiple gesture types for different actions**
- **🤚 Support for both left and right hands**
- **📊 Visual feedback with hand landmark overlay**
- **💻 Terminal output with gesture names and actions**
- **🪞 Mirror view for intuitive interaction**
- **🔧 Modular architecture for easy customization**
- **⚡ Smoothed cursor movement with configurable sensitivity**
- **🛡️ Built-in cooldowns to prevent action spam**

## Project Structure

```
.
├── config/
│   ├── __init__.py
│   ├── config.py          # Application settings (camera, display, mouse control)
│   └── gestures.py        # Gesture definitions and mouse actions
├── src/
│   ├── __init__.py
│   ├── hand_detector.py   # Hand detection using MediaPipe
│   ├── gesture_recognizer.py  # Gesture recognition logic
│   ├── mouse_controller.py    # PyAutoGUI mouse control
│   ├── visualizer.py      # Display and terminal output
│   └── app.py            # Main application orchestrator
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Architecture

The application follows a modular design with separation of concerns:

- **`config/`**: Contains all configuration settings

  - `config.py`: Camera settings, display parameters, MediaPipe & mouse control configuration
  - `gestures.py`: Gesture definitions with associated mouse actions

- **`src/`**: Core application modules

  - `hand_detector.py`: Wraps MediaPipe hand detection functionality
  - `gesture_recognizer.py`: Analyzes finger positions to identify gestures
  - `mouse_controller.py`: Handles PyAutoGUI mouse and keyboard control
  - `visualizer.py`: Handles all display and terminal output
  - `app.py`: Orchestrates all components in the main loop

- **`main.py`**: Simple entry point that starts the application

## Hand Gestures & Mouse Controls

The application recognizes the following hand gestures to control your mouse:

| Gesture            | Fingers                   | Action       | Description                                     |
| ------------------ | ------------------------- | ------------ | ----------------------------------------------- |
| **CURSOR CONTROL** | ☝️ Index only             | Move cursor  | Point with your index finger to move the cursor |
| **LEFT CLICK**     | 👍 Thumb + Index          | Left click   | Pinch gesture to left click                     |
| **RIGHT CLICK**    | 🤙 Thumb + Pinky          | Right click  | Shaka/hang loose gesture for right click        |
| **DOUBLE CLICK**   | 👌 Thumb + Index + Middle | Double click | Three fingers together to double click          |
| **SCROLL UP**      | ✌️ Index + Middle         | Scroll up    | Peace sign to scroll up                         |
| **SCROLL DOWN**    | 🤟 Index + Middle + Ring  | Scroll down  | Three fingers up to scroll down                 |
| **NEUTRAL**        | ✊ Fist                   | No action    | Rest position, no action performed              |
| **STOP**           | 🖐️ Open hand              | Stop         | Open palm to stop all actions                   |

## Requirements

- Python 3.7 or higher
- Webcam
- Windows/Linux/macOS

## Installation

1. **Clone or download this repository**

2. **Install the required dependencies:**

```bash
pip install -r requirements.txt
```

This will install:

- `mediapipe`: Google's ML framework for hand tracking
- `opencv-python`: For video capture and display
- `numpy`: For numerical operations
- `pyautogui`: For mouse and keyboard control

## Usage

Run the hand gesture mouse control application:

```bash
python main.py
```

### Controls

- The application will open a window showing your webcam feed
- Hold your hand in front of the camera
- Use different gestures to control your mouse:
  - **Point with index finger** to move the cursor around
  - **Pinch (thumb + index)** to left click
  - **Make a peace sign** to scroll up
  - **Show three fingers** to scroll down
  - **Open palm** to stop and reset
- The detected gesture and action will be displayed both:
  - On the video window (with hand landmarks)
  - In the terminal (with gesture name, action, and confidence)
- Press **'q'** to quit the application

### Tips for Best Performance

1. **Good lighting**: Ensure your hand is well-lit
2. **Plain background**: Works best against a simple background
3. **Moderate distance**: Keep your hand 1-2 feet from the camera
4. **Clear gestures**: Make distinct, well-defined gestures
5. **Stable movements**: Move smoothly for better cursor control
6. **Failsafe**: Move mouse to screen corner to abort (PyAutoGUI failsafe)

## Customization

The modular architecture makes it easy to customize the application:

### Adding New Gestures & Actions

Edit `config/gestures.py` and add your gesture definition:

```python
GESTURES = {
    'MY_CUSTOM_GESTURE': {
        'fingers': [True, False, True, False, True],  # Custom finger pattern
        'description': 'Custom gesture description',
        'action': 'custom_action',  # Define action in mouse_controller.py
        'exact_match': True,
        'priority': 2
    },
    # ... other gestures
}

GESTURE_DISPLAY_NAMES = {
    'MY_CUSTOM_GESTURE': 'My Custom Gesture',
    # ... other names
}
```

### Adjusting Mouse Control Settings

Edit `config/config.py`:

```python
# Enable/disable mouse control
ENABLE_MOUSE_CONTROL = True

# Adjust cursor smoothing (0 = no smoothing, 1 = max smoothing)
MOUSE_SMOOTHING = 0.5

# Adjust click cooldown to prevent spam
CLICK_COOLDOWN = 0.5  # seconds

# Adjust scroll sensitivity
SCROLL_AMOUNT = 3
```

### Adjusting Detection Settings

Edit `config/config.py`:

```python
# Change camera index
CAMERA_INDEX = 1  # Try different cameras

# Adjust detection sensitivity
MIN_DETECTION_CONFIDENCE = 0.7  # Higher = more strict
MIN_TRACKING_CONFIDENCE = 0.7

# Modify display settings
FONT_SCALE = 1.5  # Larger text
FONT_COLOR = (255, 0, 0)  # Change color (BGR format)
```

### Adding Custom Mouse Actions

Edit `src/mouse_controller.py` to add new actions:

```python
def execute_action(self, gesture_data, hand_landmarks, frame_shape):
    action = gesture_data.get('action', 'none')

    # Add your custom action
    if action == 'custom_action':
        # Your custom PyAutoGUI code here
        pyautogui.hotkey('ctrl', 'c')  # Example: Copy
        return 'Custom action performed'
```

### Extending Functionality

- **`HandDetector`**: Modify hand detection behavior
- **`GestureRecognizer`**: Add custom recognition algorithms
- **`MouseController`**: Add keyboard shortcuts, drag-and-drop, etc.
- **`Visualizer`**: Change display format or add new output methods
- **`HandGestureApp`**: Add additional processing steps or data logging

## How It Works

1. **Initialization**: The application initializes hand detector, gesture recognizer, mouse controller, and visualizer
2. **Camera Capture**: Each frame is captured from the webcam
3. **Hand Detection**: MediaPipe detects up to 2 hands and tracks 21 landmarks on each
4. **Gesture Analysis**: The recognizer analyzes which fingers are extended
5. **Action Mapping**: The finger pattern is matched against defined gestures
6. **Mouse Control**: PyAutoGUI executes the corresponding mouse action
7. **Visualization**: Results are displayed on screen and printed to terminal

## Troubleshooting

### Webcam not opening

- Make sure your webcam is connected and not being used by another application
- Try changing `CAMERA_INDEX` in `config/config.py` (try 0, 1, or 2)

### Poor gesture detection

- Ensure good lighting conditions
- Keep your hand at a moderate distance from the camera
- Make clear, distinct gestures
- Adjust confidence parameters in `config/config.py`

### Cursor moving erratically

- Increase `MOUSE_SMOOTHING` in `config/config.py` (try 0.7 or 0.8)
- Ensure stable hand positioning
- Check lighting and background

### Actions triggering too frequently

- Increase cooldown values in `config/config.py`
- `CLICK_COOLDOWN` for clicks
- `SCROLL_COOLDOWN` for scrolling

### PyAutoGUI failsafe triggered

- If you quickly move mouse to corner, PyAutoGUI aborts for safety
- This is a built-in safety feature
- Just restart the application

### Import errors

- Make sure you run the application from the project root directory
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're using Python 3.7 or higher

### Dependencies installation issues

- Make sure you have Python 3.7+ installed
- Try upgrading pip: `pip install --upgrade pip`
- On some systems, you may need to use `pip3` instead of `pip`

## Safety Features

- **Failsafe Mode**: Move mouse to screen corner to abort (PyAutoGUI built-in)
- **Action Cooldowns**: Prevents accidental rapid clicking/scrolling
- **Cursor Smoothing**: Reduces jittery movements
- **Clear Visual Feedback**: Always know what gesture is being detected

## Performance Tips

- Close unnecessary applications for better camera performance
- Use good lighting for better hand detection
- Keep hand movements smooth and deliberate
- Start with the neutral (fist) gesture before transitioning to actions

## Development

The modular structure makes it easy to extend and modify:

1. **Add new detection methods** in `hand_detector.py`
2. **Implement custom gesture logic** in `gesture_recognizer.py`
3. **Add new mouse/keyboard actions** in `mouse_controller.py`
4. **Create new visualization modes** in `visualizer.py`
5. **Define new gestures** in `config/gestures.py`
6. **Adjust settings** in `config/config.py`

## Use Cases

- **Accessibility**: Hands-free computer control
- **Presentations**: Control slides without touching keyboard
- **Gaming**: Custom gesture controls
- **Smart Home Control**: Combine with home automation
- **Creative Applications**: Art and music creation
- **Education**: Interactive learning experiences

## License

This project is provided as-is for educational and personal use.

## Credits

- Built with [MediaPipe](https://mediapipe.dev/) by Google
- Uses [OpenCV](https://opencv.org/) for video processing
- Uses [PyAutoGUI](https://pyautogui.readthedocs.io/) for mouse control

## Disclaimer

Use this software responsibly. Be aware of your surroundings when using gesture control. The PyAutoGUI failsafe (moving mouse to corner) can be used to immediately abort the program if needed.
