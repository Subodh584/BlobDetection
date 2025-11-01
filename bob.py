import cv2
import numpy as np
import requests
import time

class AutonomousBlobTracker:
    def __init__(self, esp32_ip="192.168.4.1"):
        # ESP32 connection
        self.esp32_ip = esp32_ip
        self.esp32_url = f"http://{esp32_ip}/control"
        
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
        
        # Control parameters
        self.dead_zone = 20  # Pixels from center where no movement needed
        self.base_speed = 150  # Base motor speed
        self.max_speed = 255  # Maximum motor speed
        
        # Movement timing
        self.last_command_time = 0
        self.command_interval = 0.3  # Send commands every 100ms
        
        # ESP32 connection test
        self.test_connection()
        
    def test_connection(self):
        """Test connection to ESP32"""
        try:
            response = requests.get(f"http://{self.esp32_ip}/", timeout=2)
            if response.status_code == 200:
                print("✓ Connected to ESP32 successfully!")
                return True
        except:
            print("✗ Warning: Could not connect to ESP32")
            print(f"  Make sure ESP32 is powered on and you're connected to WiFi: ESP32_Motor_Control")
            print(f"  ESP32 IP should be: {self.esp32_ip}")
        return False
    
    def send_motor_command(self, speed):
        """
        Send movement command to ESP32
        speed > 0: Move FORWARD (object is below center)
        speed < 0: Move BACKWARD (object is above center)
        speed = 0: STOP
        """
        try:
            # Both motors get same speed for linear movement
            params_a = {'motor': 'A', 'speed': speed}
            params_b = {'motor': 'B', 'speed': speed}
            
            requests.get(self.esp32_url, params=params_a, timeout=0.5)
            requests.get(self.esp32_url, params=params_b, timeout=0.5)
            return True
        except:
            return False
    
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
        
        # Control parameters
        cv2.createTrackbar('Dead Zone', 'Color Adjustments', self.dead_zone, 200, lambda x: None)
        cv2.createTrackbar('Base Speed', 'Color Adjustments', self.base_speed, 255, lambda x: None)
        
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
        self.dead_zone = cv2.getTrackbarPos('Dead Zone', 'Color Adjustments')
        self.base_speed = cv2.getTrackbarPos('Base Speed', 'Color Adjustments')
    
    def detect_blob(self, frame):
        """Detect the colored blob in the frame"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
        
        # Remove noise
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        return mask
    
    def get_average_position(self, mask):
        """Calculate average position of all white pixels"""
        y_coords, x_coords = np.where(mask == 255)
        
        if len(x_coords) == 0 or len(y_coords) == 0:
            return None, 0
        
        area = len(x_coords)
        
        if area < self.min_blob_area or area > self.max_blob_area:
            return None, 0
        
        avg_x = int(np.mean(x_coords))
        avg_y = int(np.mean(y_coords))
        
        return (avg_x, avg_y), area
    
    def calculate_motor_speed(self, center, frame_shape):
        """
        Calculate motor speed based on vertical position
        Returns: (speed, command_text)
        
        IMPORTANT: Y-axis movement control
        - Object ABOVE center (low Y value) → Move BACKWARD (negative speed)
        - Object BELOW center (high Y value) → Move FORWARD (positive speed)
        - Object in dead zone → STOP
        """
        height, width = frame_shape[:2]
        frame_center_y = height // 2
        
        if center is None:
            return 0, "STOP - Lost tracking"
        
        cx, cy = center
        
        # Calculate vertical error (positive = object is below center)
        error_y = cy - frame_center_y
        
        # Check if in dead zone
        if abs(error_y) < self.dead_zone:
            return 0, "CENTERED - In dead zone"
        
        # Calculate proportional speed based on error
        # Larger error = faster speed
        speed_factor = min(abs(error_y) / height, 1.0)  # Normalize to 0-1
        speed = int(self.base_speed * speed_factor)
        speed = max(50, min(speed, self.max_speed))  # Clamp between 50-255
        
        if error_y > 0:
            # Object is BELOW center → Move FORWARD
            return speed, f"FORWARD {speed} - Object below (Err: +{error_y}px)"
        else:
            # Object is ABOVE center → Move BACKWARD
            return -speed, f"BACKWARD {speed} - Object above (Err: {error_y}px)"
    
    def draw_overlay(self, frame, center, area, command, motor_speed):
        """Draw tracking information on frame"""
        height, width = frame.shape[:2]
        frame_center_y = height // 2
        
        # Draw horizontal center line
        cv2.line(frame, (0, frame_center_y), (width, frame_center_y), (255, 255, 255), 2)
        
        # Draw dead zone (horizontal band)
        cv2.rectangle(frame, 
                     (0, frame_center_y - self.dead_zone), 
                     (width, frame_center_y + self.dead_zone), 
                     (200, 200, 200), 1)
        
        if center:
            # Draw RED circle at average position
            cv2.circle(frame, center, 10, (0, 0, 255), -1)
            cv2.circle(frame, center, 15, (0, 0, 255), 2)
            
            # Draw line from blob to center line
            cv2.line(frame, center, (center[0], frame_center_y), (0, 255, 255), 2)
            
            # Display info
            cv2.putText(frame, f"Pixels: {area}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"Position: {center}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"Motor Speed: {motor_speed}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display command
        cv2.putText(frame, command, (10, height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Draw direction indicator
        if "FORWARD" in command:
            cv2.arrowedLine(frame, (width - 50, height - 50), (width - 50, height - 100), 
                          (0, 255, 0), 3, tipLength=0.3)
        elif "BACKWARD" in command:
            cv2.arrowedLine(frame, (width - 50, height - 100), (width - 50, height - 50), 
                          (0, 0, 255), 3, tipLength=0.3)
        
        return frame

def main():
    print("=" * 60)
    print("AUTONOMOUS BLOB TRACKER WITH ESP32 CONTROL")
    print("=" * 60)
    print("\n📋 SETUP INSTRUCTIONS:")
    print("1. Power on your ESP32")
    print("2. Connect to WiFi network: 'ESP32_Motor_Control'")
    print("3. Password: '12345678'")
    print("4. ESP32 IP Address: 192.168.4.1")
    print("\n🎮 CONTROLS:")
    print("  - Adjust trackbars to tune color detection")
    print("  - 'q' - Quit program")
    print("  - 's' - Save current settings")
    print("  - SPACE - Emergency stop")
    print("\n🤖 TRACKING MODE:")
    print("  - Object ABOVE center → Motors move BACKWARD")
    print("  - Object BELOW center → Motors move FORWARD")
    print("  - Object in dead zone → Motors STOP")
    print("=" * 60)
    
    esp32_ip = input("\nEnter ESP32 IP address (default: 192.168.4.1): ").strip()
    if not esp32_ip:
        esp32_ip = "192.168.4.1"
    
    # Initialize tracker
    tracker = AutonomousBlobTracker(esp32_ip)
    tracker.create_trackbars()
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("\n✓ Camera opened successfully")
    print("✓ System ready - Starting autonomous tracking...\n")
    
    try:
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
            
            
            # Calculate motor speed and command
            motor_speed, command = tracker.calculate_motor_speed(center, frame.shape)
            
            # Send command to ESP32 (with rate limiting)
            current_time = time.time()
            if current_time - tracker.last_command_time >= tracker.command_interval:
                if tracker.send_motor_command(motor_speed):
                    tracker.last_command_time = current_time
            
            # Draw overlay
            frame = tracker.draw_overlay(frame, center, area, command, motor_speed)
            
            # Show frames
            cv2.imshow('Autonomous Blob Tracker', frame)
            # cv2.imshow('Mask', mask)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nStopping motors and exiting...")
                tracker.send_motor_command(0)
                break
            elif key == ord(' '):  # Emergency stop
                print("\n⚠️ EMERGENCY STOP!")
                tracker.send_motor_command(0)
            elif key == ord('s'):
                print(f"\n💾 Saved Settings:")
                print(f"Lower HSV: {tracker.lower_hsv}")
                print(f"Upper HSV: {tracker.upper_hsv}")
                print(f"Min Area: {tracker.min_blob_area}")
                print(f"Max Area: {tracker.max_blob_area}")
                print(f"Dead Zone: {tracker.dead_zone}")
                print(f"Base Speed: {tracker.base_speed}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Keyboard interrupt - Stopping motors...")
        tracker.send_motor_command(0)
    
    finally:
        # Clean shutdown
        tracker.send_motor_command(0)
        cap.release()
        cv2.destroyAllWindows()
        print("✓ System shutdown complete")

if __name__ == "__main__":
    main()