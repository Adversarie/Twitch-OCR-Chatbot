import json
import os
import cv2
import mss
import numpy as np
import pytesseract
import logging
from config import Config

logger = logging.getLogger(__name__)

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD

def load_zones():
    zones_path = os.path.join(os.path.dirname(__file__), "zones.json")
    try:
        with open(zones_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load zones.json: {e}")
        return {}

class OCRScanner:
    def __init__(self, target_game: str = Config.TARGET_GAME):
        self.target_game = target_game
        self.sct = mss.MSS()
        self.all_zones = load_zones()
        
        if self.target_game not in self.all_zones:
            logger.warning(f"Target game '{self.target_game}' not found in zones.json. Using empty configuration.")
            self.zones = {}
        else:
            self.zones = self.all_zones[self.target_game]

    def reload_zones(self):
        """Reloads the zones from the JSON file. Useful when edited by the GUI."""
        self.all_zones = load_zones()
        if self.target_game in self.all_zones:
            self.zones = self.all_zones[self.target_game]
        else:
            self.zones = {}

    def preprocess_image(self, img_array):
        """Convert to grayscale and apply thresholding to improve OCR."""
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGRA2GRAY)
        # Apply inverse thresholding: makes white text black and everything else white (or vice versa depending on game UI)
        # We use a simple binary threshold, may need adjustment per game.
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        return thresh

    def scan(self):
        """
        Scans all defined zones for the target game.
        Returns a list of detected event_ids and the extracted text.
        Returns format: [(event_id, extracted_text), ...]
        """
        detected_events = []
        for event_id, config in self.zones.items():
            box = config["box"]
            keywords = config["keywords"]
            
            try:
                # Capture the screen region
                sct_img = self.sct.grab(box)
                img_array = np.array(sct_img)
                
                # Preprocess
                processed_img = self.preprocess_image(img_array)
                
                # Run OCR
                custom_config = r'--oem 3 --psm 6'
                text = pytesseract.image_to_string(processed_img, config=custom_config).lower()
                
                # Check for keywords
                for keyword in keywords:
                    if keyword in text:
                        detected_events.append((event_id, text))
                        break # Prevent multiple triggers for the same zone
                        
            except Exception as e:
                logger.error(f"Error scanning zone {event_id}: {e}")
                
        return detected_events
