"""
Settings configuration for Blob Tracker
Save and load tracking parameters
"""

import json
import os
from pathlib import Path

class Settings:
    """Manages saving and loading blob tracker settings"""
    
    SETTINGS_FILE = "tracker_settings.json"
    
    @staticmethod
    def get_default_settings():
        """Return default settings"""
        return {
            "lower_hsv": [5, 100, 100],
            "upper_hsv": [15, 255, 255],
            "min_blob_area": 500,
            "max_blob_area": 50000,
            "dead_zone": 50,
            "description": "Default orange blob tracking settings"
        }
    
    @staticmethod
    def save_settings(tracker, filename=None):
        """Save current tracker settings to JSON file"""
        if filename is None:
            filename = Settings.SETTINGS_FILE
        
        settings = {
            "lower_hsv": tracker.lower_hsv.tolist(),
            "upper_hsv": tracker.upper_hsv.tolist(),
            "min_blob_area": tracker.min_blob_area,
            "max_blob_area": tracker.max_blob_area,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(settings, f, indent=2)
            print(f"✓ Settings saved to {filename}")
            return True
        except Exception as e:
            print(f"✗ Failed to save settings: {e}")
            return False
    
    @staticmethod
    def load_settings(tracker, filename=None):
        """Load tracker settings from JSON file"""
        if filename is None:
            filename = Settings.SETTINGS_FILE
        
        if not os.path.exists(filename):
            print(f"⚠ Settings file not found: {filename}")
            return False
        
        try:
            with open(filename, 'r') as f:
                settings = json.load(f)
            
            import numpy as np
            tracker.lower_hsv = np.array(settings.get("lower_hsv", [5, 100, 100]))
            tracker.upper_hsv = np.array(settings.get("upper_hsv", [15, 255, 255]))
            tracker.min_blob_area = settings.get("min_blob_area", 500)
            tracker.max_blob_area = settings.get("max_blob_area", 50000)
            
            print(f"✓ Settings loaded from {filename}")
            return True
        except Exception as e:
            print(f"✗ Failed to load settings: {e}")
            return False
    
    @staticmethod
    def list_saved_presets():
        """List all available setting presets"""
        presets = {
            "orange": {
                "lower_hsv": [5, 100, 100],
                "upper_hsv": [15, 255, 255],
                "description": "Default orange blob"
            },
            "red": {
                "lower_hsv": [0, 100, 100],
                "upper_hsv": [10, 255, 255],
                "description": "Red blob"
            },
            "blue": {
                "lower_hsv": [100, 100, 100],
                "upper_hsv": [130, 255, 255],
                "description": "Blue blob"
            },
            "green": {
                "lower_hsv": [40, 50, 50],
                "upper_hsv": [90, 255, 255],
                "description": "Green blob"
            },
            "yellow": {
                "lower_hsv": [20, 100, 100],
                "upper_hsv": [30, 255, 255],
                "description": "Yellow blob"
            }
        }
        return presets
