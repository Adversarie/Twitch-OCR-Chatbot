import os
import cv2
import numpy as np

def make_text_template(text: str, width: int, height: int, border_color=(200, 200, 200), text_color=(255, 255, 255), bg_color=(20, 20, 20)):
    """Creates a clean reference template with styling and centered text."""
    img = np.full((height, width, 3), bg_color, dtype=np.uint8)
    # Add border
    cv2.rectangle(img, (2, 2), (width - 3, height - 3), border_color, 2)
    # Add inner decorative line
    cv2.rectangle(img, (5, 5), (width - 6, height - 6), (border_color[0]//2, border_color[1]//2, border_color[2]//2), 1)
    
    # Calculate text position
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    
    text_x = (width - text_size[0]) // 2
    text_y = (height + text_size[1]) // 2
    
    cv2.putText(img, text, (text_x, text_y), font, font_scale, text_color, thickness, cv2.LINE_AA)
    return img

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    
    templates = {
        "poe2/poe2_disconnect.png": ("Disconnected", 320, 60, (180, 160, 100), (255, 255, 255), (15, 15, 20)),
        "poe2/poe2_out_of_mana.png": ("Out of Mana", 280, 50, (60, 60, 220), (80, 80, 255), (20, 10, 10)),
        "poe2/poe2_inventory_full.png": ("Inventory is full", 320, 50, (60, 60, 200), (90, 90, 255), (20, 10, 10)),
        "poe2/poe2_boss_kill.png": ("DEFEATED", 240, 60, (50, 180, 220), (80, 220, 255), (15, 15, 25)),
        "poe1/poe1_exalted_mirror_drop.png": ("Mirror of Kalandra", 320, 50, (50, 150, 220), (255, 255, 255), (30, 20, 15)),
        "wow/wow_achievement.png": ("Achievement Earned", 320, 55, (50, 200, 240), (255, 255, 255), (20, 20, 30)),
    }
    
    for rel_path, (text, w, h, border, text_c, bg) in templates.items():
        out_path = os.path.join(base_dir, rel_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        img = make_text_template(text, w, h, border, text_c, bg)
        cv2.imwrite(out_path, img)
        print(f"Generated template: {out_path} ({w}x{h})")

if __name__ == "__main__":
    main()
