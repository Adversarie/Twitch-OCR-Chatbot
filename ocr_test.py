import os
import cv2
import mss
import numpy as np
import pytesseract
from config import Config
from ocr_scanner import OCRScanner, load_zones

def test_ocr():
    print("=" * 60)
    print("TWITCH OCR CHATBOT - DIAGNOSTIC SCREEN CAPTURE & OCR TEST")
    print("=" * 60)
    
    # Configure Tesseract path
    pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD
    print(f"Using Tesseract executable: {Config.TESSERACT_CMD}")
    print(f"Target Game: {Config.TARGET_GAME}")
    
    # Create debug directory
    debug_dir = "debug"
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
        print(f"Created '{debug_dir}/' directory for debug screenshots.")
        
    all_zones = load_zones()
    game_zones = all_zones.get(Config.TARGET_GAME, {})
    if not game_zones:
        print(f"Error: No scan zones configured for game '{Config.TARGET_GAME}' in ocr_scanner.py.")
        return
        
    print(f"Found {len(game_zones)} zone(s) to test.\n")
    sct = mss.MSS()
    scanner = OCRScanner()
    
    for event_id, config in game_zones.items():
        box = config["box"]
        keywords = config["keywords"]
        print(f"Testing Zone: {event_id}")
        print(f"  Coordinates: top={box['top']}, left={box['left']}, width={box['width']}, height={box['height']}")
        print(f"  Keywords to look for: {keywords}")
        
        try:
            # Capture
            sct_img = sct.grab(box)
            img_array = np.array(sct_img)
            
            # Preprocess
            processed_img = scanner.preprocess_image(img_array)
            
            # Save raw and processed images
            raw_path = os.path.join(debug_dir, f"raw_{event_id}.png")
            processed_path = os.path.join(debug_dir, f"processed_{event_id}.png")
            
            # Convert BGRA to BGR for saving raw image
            cv2.imwrite(raw_path, cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR))
            cv2.imwrite(processed_path, processed_img)
            
            print(f"  [Saved] Raw image to: {raw_path}")
            print(f"  [Saved] Processed thresholded image to: {processed_path}")
            
            # Run OCR
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(processed_img, config=custom_config)
            text_lower = text.lower()
            
            print(f"  --- OCR Raw Output ---")
            if text.strip():
                # Print indented lines of detected text
                for line in text.splitlines():
                    if line.strip():
                        print(f"    | {line}")
            else:
                print("    (No text detected)")
            print(f"  ----------------------")
            
            # Check keywords
            matched_keywords = [kw for kw in keywords if kw in text_lower]
            if matched_keywords:
                print(f"  SUCCESS! Matched keywords: {matched_keywords}")
            else:
                print(f"  WARNING: No keywords matched.")
                
        except Exception as e:
            print(f"  ERROR testing zone '{event_id}': {e}")
            
        print("-" * 60)

if __name__ == "__main__":
    test_ocr()
