import cv2
import numpy as np

class BlobTracker:
    def __init__(self):
        # Default HSV color range (Blue)
        self.lower_hsv = np.array([34, 30, 94])
        self.upper_hsv = np.array([68, 116, 229])
        
        # Blob size limits (in pixels)
        self.min_blob_area = 500
        self.max_blob_area = 50000
        
        # Tracking state
        self.last_position = None
        self.frames_lost = 0
        self.max_frames_lost = 10
        
    def create_trackbars(self):
        """Create window with trackbars for color adjustment"""
        cv2.namedWindow('Color Adjustments')
        
        # HSV trackbars
        cv2.createTrackbar('H Min', 'Color Adjustments', self.lower_hsv[0], 179, lambda x: None)
        cv2.createTrackbar('H Max', 'Color Adjustments', self.upper_hsv[0], 179, lambda x: None)
        cv2.createTrackbar('S Min', 'Color Adjustments', self.lower_hsv[1], 255, lambda x: None)
        cv2.createTrackbar('S Max', 'Color Adjustments', self.upper_hsv[1], 255, lambda x: None)
        cv2.createTrackbar('V Min', 'Color Adjustments', self.lower_hsv[2], 255, lambda x: None)
        cv2.createTrackbar('V Max', 'Color Adjustments', self.upper_hsv[2], 255, lambda x: None)
        
        # Blob size trackbars
        cv2.createTrackbar('Min Area', 'Color Adjustments', self.min_blob_area, 10000, lambda x: None)
        cv2.createTrackbar('Max Area', 'Color Adjustments', self.max_blob_area, 100000, lambda x: None)
        
    def get_trackbar_values(self):
        """Read current trackbar values"""
        h_min = cv2.getTrackbarPos('H Min', 'Color Adjustments')
        h_max = cv2.getTrackbarPos('H Max', 'Color Adjustments')
        s_min = cv2.getTrackbarPos('S Min', 'Color Adjustments')
        s_max = cv2.getTrackbarPos('S Max', 'Color Adjustments')
        v_min = cv2.getTrackbarPos('V Min', 'Color Adjustments')
        v_max = cv2.getTrackbarPos('V Max', 'Color Adjustments')
        
        self.lower_hsv = np.array([h_min, s_min, v_min])
        self.upper_hsv = np.array([h_max, s_max, v_max])
        
        self.min_blob_area = cv2.getTrackbarPos('Min Area', 'Color Adjustments')
        self.max_blob_area = cv2.getTrackbarPos('Max Area', 'Color Adjustments')
    
    def detect_blob(self, frame):
        """Detect the colored blob in the frame"""
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask
        mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
        
        # Remove noise
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        return mask
    
    def get_average_position(self, mask):
        """Calculate average position of all white pixels (1s) in the mask"""
        # Find all coordinates where mask value is 255 (white/1)
        y_coords, x_coords = np.where(mask == 255)
        
        # Check if any white pixels exist
        if len(x_coords) == 0 or len(y_coords) == 0:
            return None, 0
        
        # Calculate total area (number of white pixels)
        area = len(x_coords)
        
        # Check if area is within bounds
        if area < self.min_blob_area or area > self.max_blob_area:
            return None, 0
        
        # Calculate average position
        avg_x = int(np.mean(x_coords))
        avg_y = int(np.mean(y_coords))
        
        return (avg_x, avg_y), area
    
    def get_direction_command(self, center, frame_shape):
        """Determine rover movement command based on blob position"""
        height, width = frame_shape[:2]
        frame_center_x = width // 2
        
        # Dead zone (pixels from center where we don't need to adjust)
        dead_zone = 50
        
        if center is None:
            return "STOP - Lost tracking"
        
        cx, cy = center
        error = cx - frame_center_x
        
        if abs(error) < dead_zone:
            return "FORWARD - Centered"
        elif error > 0:
            return f"TURN RIGHT - Error: {error}px"
        else:
            return f"TURN LEFT - Error: {abs(error)}px"
    
    def draw_overlay(self, frame, center, area, command):
        """Draw tracking information on frame"""
        height, width = frame.shape[:2]
        frame_center_x = width // 2
        
        # Draw center line
        cv2.line(frame, (frame_center_x, 0), (frame_center_x, height), (255, 255, 255), 2)
        
        # Draw dead zone
        cv2.rectangle(frame, 
                     (frame_center_x - 50, 0), 
                     (frame_center_x + 50, height), 
                     (200, 200, 200), 1)
        
        if center:
            # Draw single RED circle at average position
            cv2.circle(frame, center, 10, (0, 0, 255), -1)
            cv2.circle(frame, center, 15, (0, 0, 255), 2)
            
            # Draw line from average position to center
            cv2.line(frame, center, (frame_center_x, center[1]), (0, 255, 255), 2)
            
            # Display info
            cv2.putText(frame, f"Pixels: {area}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"Avg Position: {center}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Display command
        cv2.putText(frame, command, (10, height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        return frame

def main():
    # Initialize tracker
    tracker = BlobTracker()
    tracker.create_trackbars()
    
    # Open camera (0 for default camera, or video file path)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 60)
    
    # Try to reduce motion blur (not all cameras support this)
    try:
        cap.set(cv2.CAP_PROP_EXPOSURE, -6)  # Lower exposure = faster shutter
    except:
        pass
    
    print("=" * 50)
    print("BLOB TRACKER - AVERAGE POSITION MODE")
    print("=" * 50)
    print("Controls:")
    print("  - Adjust trackbars to tune color detection")
    print("  - Press 'q' to quit")
    print("  - Press 's' to save current settings")
    print("=" * 50)
    print("Tracking: Single RED point = average of all detected pixels")
    print("=" * 50)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        # Get current trackbar values
        tracker.get_trackbar_values()
        
        # Detect blob and get mask
        mask = tracker.detect_blob(frame)
        
        # Get average position of all white pixels
        center, area = tracker.get_average_position(mask)
        
        # Get movement command
        command = tracker.get_direction_command(center, frame.shape)
        
        # Draw overlay
        frame = tracker.draw_overlay(frame, center, area, command)
        
        # Show frames
        cv2.imshow('Blob Tracker', frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            print(f"\nSaved Settings:")
            print(f"Lower HSV: {tracker.lower_hsv}")
            print(f"Upper HSV: {tracker.upper_hsv}")
            print(f"Min Area: {tracker.min_blob_area}")
            print(f"Max Area: {tracker.max_blob_area}")
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()