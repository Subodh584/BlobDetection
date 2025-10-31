"""
Advanced usage examples for Blob Tracker
Demonstrates how to extend and integrate the tracker
"""

from blob_tracker import BlobTracker
from settings import Settings
import cv2
import numpy as np

# Example 1: Load preset settings
def example_track_red_blob():
    """Track a red blob instead of orange"""
    tracker = BlobTracker()
    
    # Load red preset
    presets = Settings.list_saved_presets()
    red_preset = presets["red"]
    
    tracker.lower_hsv = np.array(red_preset["lower_hsv"])
    tracker.upper_hsv = np.array(red_preset["upper_hsv"])
    
    print(f"Tracking: {red_preset['description']}")
    print(f"HSV Range: {red_preset['lower_hsv']} - {red_preset['upper_hsv']}")


# Example 2: Custom blob size constraints
def example_track_small_blobs():
    """Detect only small blobs (useful for specific applications)"""
    tracker = BlobTracker()
    
    # Adjust for small objects
    tracker.min_blob_area = 100      # Smaller minimum
    tracker.max_blob_area = 5000     # Smaller maximum
    
    print(f"Tracking small blobs: {tracker.min_blob_area}-{tracker.max_blob_area} pixels")


# Example 3: Custom dead zone
def example_sensitive_tracking():
    """Increase tracking sensitivity with smaller dead zone"""
    tracker = BlobTracker()
    dead_zone = 25  # Reduced from default 50
    
    return dead_zone


# Example 4: Save and load custom settings
def example_save_load_settings():
    """Demonstrate saving and loading configurations"""
    tracker = BlobTracker()
    
    # Customize settings
    tracker.lower_hsv = np.array([10, 80, 100])
    tracker.upper_hsv = np.array([20, 255, 255])
    tracker.min_blob_area = 700
    tracker.max_blob_area = 40000
    
    # Save to file
    Settings.save_settings(tracker, "my_custom_settings.json")
    
    # Load into new tracker instance
    tracker2 = BlobTracker()
    Settings.load_settings(tracker2, "my_custom_settings.json")
    
    print("✓ Settings saved and loaded successfully")


# Example 5: Extract movement commands for rover integration
def example_rover_integration():
    """
    Shows how to use tracker output for rover control
    
    Typical integration pattern:
    1. Get blob position from tracker
    2. Generate direction command
    3. Send command to rover over serial/network
    """
    tracker = BlobTracker()
    
    # Simulated frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Example positions
    test_positions = [
        (320, 240),  # Center - should return "FORWARD - Centered"
        (400, 240),  # Right - should return "TURN RIGHT - Error: 80px"
        (250, 240),  # Left - should return "TURN LEFT - Error: 70px"
        None,        # Lost - should return "STOP - Lost tracking"
    ]
    
    print("\n=== Rover Control Examples ===")
    for position in test_positions:
        command = tracker.get_direction_command(position, frame.shape)
        print(f"Position: {position} → Command: {command}")


# Example 6: Track multiple blobs (advanced)
def example_track_multiple_blobs():
    """
    Demonstrates finding all valid blobs, not just the largest
    Useful for multi-target applications
    """
    tracker = BlobTracker()
    
    # Simulated contours (in real use, these come from detect_blob)
    contours = [
        # Each contour would be a numpy array in real use
    ]
    
    # Modified logic to get all valid blobs instead of largest
    valid_blobs = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if tracker.min_blob_area < area < tracker.max_blob_area:
            valid_blobs.append({
                'contour': contour,
                'area': area,
                'center': tracker.get_blob_center(contour)
            })
    
    print(f"Found {len(valid_blobs)} valid blobs")
    return valid_blobs


# Example 7: Frame rate and performance monitoring
def example_performance_monitoring():
    """
    Add performance monitoring to track FPS and detection speed
    """
    import time
    
    tracker = BlobTracker()
    cap = cv2.VideoCapture(0)
    
    frame_times = []
    detection_times = []
    
    for i in range(30):  # Process 30 frames
        start = time.time()
        
        ret, frame = cap.read()
        if not ret:
            break
        
        # Timing blob detection
        detect_start = time.time()
        mask, contours = tracker.detect_blob(frame)
        detection_times.append(time.time() - detect_start)
        
        frame_times.append(time.time() - start)
    
    cap.release()
    
    if frame_times:
        avg_frame_time = np.mean(frame_times)
        fps = 1 / avg_frame_time if avg_frame_time > 0 else 0
        avg_detection_time = np.mean(detection_times)
        
        print(f"\n=== Performance Metrics ===")
        print(f"Average Frame Time: {avg_frame_time*1000:.2f}ms")
        print(f"FPS: {fps:.1f}")
        print(f"Detection Time: {avg_detection_time*1000:.2f}ms")


# Example 8: Custom visualization
def example_custom_visualization():
    """
    Shows how to add custom overlays to the tracked frame
    """
    def draw_custom_overlay(frame, center, area, command):
        """Enhanced overlay with additional information"""
        height, width = frame.shape[:2]
        
        # Add timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, f"Time: {timestamp}", (10, height - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
        
        # Add grid for reference
        for x in range(0, width, 80):
            cv2.line(frame, (x, 0), (x, height), (50, 50, 50), 1)
        for y in range(0, height, 60):
            cv2.line(frame, (0, y), (width, y), (50, 50, 50), 1)
        
        return frame
    
    print("Custom overlay added")


if __name__ == "__main__":
    print("Blob Tracker - Advanced Examples\n")
    
    print("1. Red blob tracking:")
    example_track_red_blob()
    
    print("\n2. Small blob detection:")
    example_track_small_blobs()
    
    print("\n3. Sensitive tracking (dead zone):")
    dead_zone = example_sensitive_tracking()
    print(f"Dead zone: ±{dead_zone} pixels")
    
    print("\n4. Save/Load settings:")
    # example_save_load_settings()  # Uncomment to run
    
    print("\n5. Rover integration:")
    example_rover_integration()
    
    print("\n6. Performance monitoring:")
    # example_performance_monitoring()  # Uncomment to run (requires camera)
    
    print("\nFor more examples and documentation, see README.md")
