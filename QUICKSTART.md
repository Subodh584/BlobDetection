# Quick Start Guide

## Setup

Your Blob Tracker project is now ready! Follow these steps to get started:

### 1. Verify Dependencies
All required packages have been installed in the virtual environment:
- ✓ OpenCV (cv2)
- ✓ NumPy

### 2. Run the Application

**Option A: Using VS Code Task (Recommended)**
1. Press `Ctrl+Shift+B` (or `Cmd+Shift+B` on Mac)
2. Select "Run Blob Tracker" from the task list
3. The blob tracker will start using your default camera

**Option B: Using Terminal**
```bash
/Users/user62/Desktop/BlobDetection/.venv/bin/python blob_tracker.py
```

### 3. Using the Application

Once running, you'll see two windows:

**Color Adjustments Window:**
- Drag trackbars to adjust HSV color detection ranges
- Adjust Min Area / Max Area to filter blob sizes
- Changes apply in real-time

**Blob Tracker Window:**
- White vertical line = frame center
- Gray rectangle = dead zone (±50 pixels)
- Green circle = detected blob center
- Yellow line = shows horizontal offset from center
- Bottom text = movement command

**Console Output:**
- Press 's' to save and print current settings
- Press 'q' to quit the application

### 4. Common First Steps

**To detect an orange object:**
- Default settings are already tuned for orange
- Hold an orange object in front of camera
- Adjust trackbars if detection isn't clear

**To detect a different color:**
Edit `blob_tracker.py` line 6-7:
```python
self.lower_hsv = np.array([h_min, s_min, v_min])
self.upper_hsv = np.array([h_max, s_max, v_max])
```

Use the interactive trackbars first to find the right range, then update these defaults.

### 5. Project Structure

```
BlobDetection/
├── blob_tracker.py          # Main application
├── requirements.txt         # Python dependencies
├── README.md               # Full documentation
├── QUICKSTART.md          # This file
└── .github/
    └── copilot-instructions.md  # Development guidelines
```

## Troubleshooting

**Camera not detected:**
- Check if camera is connected and not in use by another app
- Try updating camera drivers

**No blob detected:**
- Ensure lighting is adequate
- Use trackbars to find your object's color range
- Check Min/Max Area thresholds

**Performance issues:**
- Reduce resolution in code (lines 89-90)
- Lower frame rate (line 91)

## Next Steps

- Modify HSV ranges for your specific color target
- Adjust dead zone size in `get_direction_command()` (line 84)
- Integrate with rover control system using movement commands
- Add logging for debugging and analysis

Happy tracking! 🎯
