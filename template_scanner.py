import os
import cv2
import mss
import numpy as np
import logging

logger = logging.getLogger(__name__)

class TemplateScanner:
    """
    High-performance, zero-bounding-box visual event detector using OpenCV template matching.
    Scans entire screen in ~5-15ms against reference image assets.
    """
    def __init__(self, templates_dir: str = None, default_threshold: float = 0.82):
        if templates_dir is None:
            import sys
            base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            candidate = os.path.join(base, "templates")
            self.templates_dir = candidate if os.path.exists(candidate) else "templates"
        else:
            self.templates_dir = templates_dir
        self.default_threshold = default_threshold
        self.templates = {} # {game_id: {event_id: (template_array, threshold)}}
        self.sct = mss.mss()
        self.reload_templates()

    def reload_templates(self):
        """Scans the templates directory and loads all reference images into memory."""
        self.templates = {}
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir, exist_ok=True)
            return

        for game_id in os.listdir(self.templates_dir):
            game_folder = os.path.join(self.templates_dir, game_id)
            if not os.path.isdir(game_folder):
                continue
                
            self.templates[game_id] = {}
            for file_name in os.listdir(game_folder):
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    event_id = os.path.splitext(file_name)[0]
                    file_path = os.path.join(game_folder, file_name)
                    
                    tpl_img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                    if tpl_img is not None:
                        self.templates[game_id][event_id] = (tpl_img, self.default_threshold)
                        logger.debug(f"Loaded visual template for {game_id}: {event_id} ({tpl_img.shape[1]}x{tpl_img.shape[0]})")
                    else:
                        logger.warning(f"Failed to load image asset: {file_path}")

    def scan(self, target_game: str, screen_array: np.ndarray = None):
        """
        Scans full-screen capture against all templates registered for target_game.
        Returns format: [(event_id, extracted_text_or_context), ...]
        """
        detected_events = []
        game_templates = self.templates.get(target_game, {})
        if not game_templates:
            return detected_events

        # Capture screen if not provided
        if screen_array is None:
            monitor = self.sct.monitors[0]
            sct_img = self.sct.grab(monitor)
            screen_array = np.array(sct_img)

        # Convert screen to grayscale
        if len(screen_array.shape) == 3:
            if screen_array.shape[2] == 4:
                screen_gray = cv2.cvtColor(screen_array, cv2.COLOR_BGRA2GRAY)
            else:
                screen_gray = cv2.cvtColor(screen_array, cv2.COLOR_BGR2GRAY)
        else:
            screen_gray = screen_array

        s_h, s_w = screen_gray.shape

        for event_id, (tpl_img, threshold) in game_templates.items():
            t_h, t_w = tpl_img.shape
            # Template cannot be larger than screen
            if t_h > s_h or t_w > s_w:
                continue

            try:
                res = cv2.matchTemplate(screen_gray, tpl_img, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)
                
                if max_val >= threshold:
                    context = f"Visual cue detected for {event_id} at ({max_loc[0]}, {max_loc[1]}) with confidence {max_val:.2f}"
                    logger.info(f"[Template Match] {event_id} detected! Confidence: {max_val:.2f}")
                    detected_events.append((event_id, context))
            except Exception as e:
                logger.error(f"Error matching template for {event_id}: {e}")

        return detected_events
