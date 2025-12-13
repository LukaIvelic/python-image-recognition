# Hand Gesture Reference Guide

Quick reference for all available hand gestures and their mouse control actions.

## Gesture Overview

### 1. CURSOR CONTROL ☝️
**Finger Pattern**: Index finger extended only  
**Action**: Move cursor  
**Usage**: Point with your index finger to control cursor position  
**Tips**: Keep movements smooth for better control

---

### 2. LEFT CLICK 👍
**Finger Pattern**: Thumb + Index finger extended  
**Action**: Left mouse click  
**Usage**: Make a pinch/gun gesture to click  
**Cooldown**: 0.5 seconds between clicks  
**Tips**: Hold the gesture briefly to ensure detection

---

### 3. RIGHT CLICK 🤙
**Finger Pattern**: Thumb + Pinky extended  
**Action**: Right mouse click  
**Usage**: Make a "shaka" or "hang loose" gesture  
**Cooldown**: 0.5 seconds between clicks  
**Tips**: Great for opening context menus

---

### 4. DOUBLE CLICK 👌
**Finger Pattern**: Thumb + Index + Middle finger extended  
**Action**: Double left click  
**Usage**: Three fingers together (like "OK" sign but all extended)  
**Cooldown**: 0.5 seconds between clicks  
**Tips**: Useful for opening files/folders

---

### 5. SCROLL UP ✌️
**Finger Pattern**: Index + Middle finger extended (Peace sign)  
**Action**: Scroll up  
**Usage**: Make a peace/victory sign  
**Cooldown**: 0.2 seconds between scrolls  
**Scroll Amount**: Configurable (default: 3 units)  
**Tips**: Hold the gesture to continuously scroll

---

### 6. SCROLL DOWN 🤟
**Finger Pattern**: Index + Middle + Ring finger extended  
**Action**: Scroll down  
**Usage**: Three fingers up  
**Cooldown**: 0.2 seconds between scrolls  
**Scroll Amount**: Configurable (default: 3 units)  
**Tips**: Hold the gesture to continuously scroll

---

### 7. NEUTRAL ✊
**Finger Pattern**: All fingers closed (Fist)  
**Action**: No action  
**Usage**: Rest position, use between gestures  
**Tips**: Return to this gesture when transitioning

---

### 8. STOP 🖐️
**Finger Pattern**: All fingers extended (Open hand)  
**Action**: Stop all actions / Reset  
**Usage**: Open palm facing camera  
**Tips**: Use this to reset cursor smoothing or stop any ongoing action

---

## Configuration

All gestures can be customized in `config/gestures.py`

### Modifying Gesture Actions

```python
GESTURES = {
    'GESTURE_NAME': {
        'fingers': [thumb, index, middle, ring, pinky],  # True = extended
        'description': 'Human readable description',
        'action': 'action_name',  # Linked to mouse_controller
        'exact_match': True,
        'priority': 1  # Lower = checked first
    }
}
```

### Available Actions

- `move_cursor` - Control cursor position
- `left_click` - Perform left click
- `right_click` - Perform right click
- `double_click` - Perform double click
- `scroll_up` - Scroll up
- `scroll_down` - Scroll down
- `stop` - Stop/reset
- `none` - No action

## Tips for Best Results

1. **Lighting**: Ensure your hand is well-lit
2. **Background**: Plain backgrounds work best
3. **Distance**: Keep hand 1-2 feet from camera
4. **Stability**: Hold gestures steady for 0.3-0.5 seconds
5. **Transitions**: Use NEUTRAL (fist) between gestures
6. **Practice**: Try each gesture a few times to get familiar

## Troubleshooting

### Gesture Not Detected
- Ensure all required fingers are clearly extended
- Check that camera can see your entire hand
- Improve lighting conditions
- Hold gesture longer

### Wrong Gesture Detected
- Make gestures more distinct
- Adjust detection confidence in config
- Ensure fingers are fully extended or closed

### Actions Triggering Too Fast
- Increase cooldown timers in `config/config.py`
- CLICK_COOLDOWN for clicks
- SCROLL_COOLDOWN for scrolling

### Cursor Too Jittery
- Increase MOUSE_SMOOTHING in config (0.7-0.9)
- Keep hand more stable
- Improve lighting

## Safety

- **Emergency Stop**: Move mouse to screen corner (PyAutoGUI failsafe)
- **Quit Application**: Press 'q' in the video window
- **Stop Gesture**: Use open palm (STOP) to reset

## Adding Custom Gestures

1. Define finger pattern in `config/gestures.py`
2. Create action handler in `src/mouse_controller.py`
3. Add display name to GESTURE_DISPLAY_NAMES
4. Test and adjust priority/cooldowns as needed

Example:
```python
'MY_GESTURE': {
    'fingers': [True, True, False, True, False],
    'description': 'Custom gesture',
    'action': 'my_custom_action',
    'exact_match': True,
    'priority': 3
}
```

---

**Remember**: Practice makes perfect! Spend a few minutes trying each gesture to get comfortable with the system.

