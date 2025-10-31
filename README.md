# Blob Tracker

A Python-based blob detection and tracking system using OpenCV. This application detects colored blobs in video streams and provides directional commands for rover navigation.

## Features

- **Real-time Blob Detection**: HSV-based color detection with trackbar adjustments
- **Blob Tracking**: Tracks the largest valid blob in the frame
- **Movement Commands**: Generates direction commands (FORWARD, TURN LEFT, TURN RIGHT)
- **Interactive Tuning**: Live trackbars for adjusting HSV ranges and blob size limits
- **Loss Recovery**: Maintains tracking for up to 10 frames when blob is lost

## Requirements

- Python 3.7+
- OpenCV (cv2)
- NumPy

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

Or individually:
```bash
pip install opencv-python numpy
```

## Usage

Run the blob tracker:
```bash
python blob_tracker.py
```

### Controls

- **Adjust Trackbars**: Fine-tune HSV color range and blob size limits in the "Color Adjustments" window
- **Press 'q'**: Quit the application
- **Press 's'**: Save and display current settings in console

### Trackbar Parameters

- **H Min/Max**: Hue range (0-179)
- **S Min/Max**: Saturation range (0-255)
- **V Min/Max**: Value range (0-255)
- **Min Area**: Minimum blob area in pixels
- **Max Area**: Maximum blob area in pixels

## How It Works

1. **Capture**: Reads frames from the default camera (webcam)
2. **Convert**: Converts BGR frames to HSV color space
3. **Mask**: Creates binary mask based on HSV thresholds
4. **Denoise**: Applies morphological operations (opening/closing)
5. **Detect**: Finds contours and identifies valid blobs
6. **Track**: Calculates blob centroid and generates movement commands
7. **Overlay**: Displays tracking info and commands on the frame

## Output

The application displays two windows:

- **Blob Tracker**: Main frame with overlay showing:
  - Blob center (green circle)
  - Frame center line (white)
  - Dead zone (gray rectangle)
  - Blob area and position
  - Movement command

- **Mask**: Binary mask showing detected blob pixels

## Customization

### Default Color (Orange)

To track different colors, modify the HSV ranges in the `__init__` method:

```python
# Example for Red
self.lower_hsv = np.array([0, 100, 100])
self.upper_hsv = np.array([10, 255, 255])
```

### Camera Settings

Modify camera properties in the `main()` function:

```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Height
cap.set(cv2.CAP_PROP_FPS, 30)            # FPS
```

## Troubleshooting

- **No blob detected**: Adjust trackbars to match your object's color
- **Flickering detection**: Increase Min Area threshold
- **Camera won't open**: Check camera permissions and availability
- **Slow performance**: Reduce frame resolution or disable exposure adjustment

## License

MIT

## Author

Blob Tracker Project
