import os
import json
import threading
import subprocess
import time
import customtkinter as ctk
import mss
from PIL import Image, ImageTk

# Initialize Settings
from dotenv import load_dotenv, set_key

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path, override=True)

class ZoneEditor(ctk.CTkToplevel):
    def __init__(self, master, game, event_id, current_box, callback):
        super().__init__(master)
        self.game = game
        self.event_id = event_id
        self.callback = callback
        
        self.title(f"Editing Zone: {event_id}")
        self.attributes('-fullscreen', True)
        self.attributes("-topmost", True)
        
        # Take screenshot
        with mss.MSS() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            self.img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
            
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.canvas = ctk.CTkCanvas(self, width=monitor["width"], height=monitor["height"], highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        
        # Draw current box
        if current_box:
            self.canvas.create_rectangle(
                current_box["left"], current_box["top"], 
                current_box["left"] + current_box["width"], current_box["top"] + current_box["height"], 
                outline="red", width=3, dash=(4, 4), tags="current"
            )
            self.canvas.create_text(
                current_box["left"], current_box["top"] - 10,
                text="Current Zone", fill="red", anchor="sw", tags="current", font=("Arial", 16, "bold")
            )
            
        # Add instructions overlay
        self.canvas.create_rectangle(10, 10, 500, 100, fill="black", stipple="gray50")
        self.canvas.create_text(20, 20, anchor="nw", fill="white", font=("Arial", 14, "bold"),
                               text=f"Editing: {event_id}\n1. Click and drag to draw the new zone.\n2. Press ENTER to save, or ESC to cancel.")

        self.start_x = None
        self.start_y = None
        self.rect = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.bind("<Return>", self.on_save)
        self.bind("<Escape>", self.on_cancel)
        
        self.focus_force()

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="green", width=3)

    def on_drag(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_save(self, event):
        if not self.rect:
            self.destroy()
            return
            
        coords = self.canvas.coords(self.rect)
        if not coords or len(coords) < 4:
            self.destroy()
            return
            
        left = int(min(coords[0], coords[2]))
        top = int(min(coords[1], coords[3]))
        width = int(abs(coords[2] - coords[0]))
        height = int(abs(coords[3] - coords[1]))
        
        new_box = {
            "monitor": 1,
            "top": top,
            "left": left,
            "width": width,
            "height": height
        }
        self.callback(self.game, self.event_id, new_box)
        self.destroy()

    def on_cancel(self, event):
        self.destroy()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Twitch OCR Chatbot")
        self.geometry("900x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.bot_process = None
        self.log_tail_thread = None
        self.stop_logging = False

        # Build layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="OCR Chatbot", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_dash = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=lambda: self.select_frame("dashboard"))
        self.btn_dash.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_settings = ctk.CTkButton(self.sidebar_frame, text="Settings", command=lambda: self.select_frame("settings"))
        self.btn_settings.grid(row=2, column=0, padx=20, pady=10)

        self.btn_zones = ctk.CTkButton(self.sidebar_frame, text="Edit Zones", command=lambda: self.select_frame("zones"))
        self.btn_zones.grid(row=3, column=0, padx=20, pady=10)

        # Content Frames
        self.frames = {}
        
        # DASHBOARD
        self.frames["dashboard"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frames["dashboard"].grid_columnconfigure(0, weight=1)
        self.frames["dashboard"].grid_rowconfigure(1, weight=1)
        
        self.dash_header = ctk.CTkLabel(self.frames["dashboard"], text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        self.dash_header.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.btn_toggle_bot = ctk.CTkButton(self.frames["dashboard"], text="Start Bot", fg_color="green", hover_color="darkgreen", command=self.toggle_bot, width=200, height=50, font=("Arial", 16, "bold"))
        self.btn_toggle_bot.grid(row=0, column=0, padx=20, pady=20, sticky="e")
        
        self.log_textbox = ctk.CTkTextbox(self.frames["dashboard"], state="disabled", wrap="word", font=("Consolas", 12))
        self.log_textbox.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # SETTINGS
        self.frames["settings"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frames["settings"].grid_columnconfigure(1, weight=1)
        
        settings_label = ctk.CTkLabel(self.frames["settings"], text="Configuration Settings", font=ctk.CTkFont(size=24, weight="bold"))
        settings_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")
        
        self.entries = {}
        row_idx = 1
        for key in ["TWITCH_CHANNEL", "TWITCH_OAUTH_TOKEN", "TWITCH_CLIENT_ID", "TWITCH_CLIENT_SECRET", "TARGET_GAME", "SCAN_INTERVAL", "EVENT_COOLDOWN", "USE_OLLAMA"]:
            lbl = ctk.CTkLabel(self.frames["settings"], text=key)
            lbl.grid(row=row_idx, column=0, padx=20, pady=10, sticky="w")
            
            # Use password masking for sensitive fields
            show_char = "*" if "TOKEN" in key or "SECRET" in key else ""
            ent = ctk.CTkEntry(self.frames["settings"], width=400, show=show_char)
            ent.insert(0, os.getenv(key, ""))
            ent.grid(row=row_idx, column=1, padx=20, pady=10, sticky="ew")
            self.entries[key] = ent
            row_idx += 1
            
        btn_save_settings = ctk.CTkButton(self.frames["settings"], text="Save Settings", command=self.save_settings)
        btn_save_settings.grid(row=row_idx, column=1, padx=20, pady=20, sticky="e")

        # ZONES
        self.frames["zones"] = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frames["zones"].grid_columnconfigure(0, weight=1)
        self.frames["zones"].grid_rowconfigure(1, weight=1)
        
        zones_label = ctk.CTkLabel(self.frames["zones"], text="Visual Zone Editor", font=ctk.CTkFont(size=24, weight="bold"))
        zones_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.zones_scroll = ctk.CTkScrollableFrame(self.frames["zones"])
        self.zones_scroll.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        self.load_zones_ui()

        # Init
        self.select_frame("dashboard")
        self.start_log_tailing()

    def select_frame(self, name):
        for frame in self.frames.values():
            frame.grid_remove()
        self.frames[name].grid(row=0, column=1, sticky="nsew")

    def save_settings(self):
        for key, ent in self.entries.items():
            set_key(env_path, key, ent.get())
        # Reload current zones UI in case game changed
        load_dotenv(dotenv_path=env_path, override=True)
        self.load_zones_ui()

    def load_zones_ui(self):
        # Clear existing
        for widget in self.zones_scroll.winfo_children():
            widget.destroy()
            
        target_game = os.getenv("TARGET_GAME", "poe1")
        zones_file = os.path.join(os.path.dirname(__file__), "zones.json")
        try:
            with open(zones_file, "r", encoding="utf-8") as f:
                self.zones_data = json.load(f)
        except Exception:
            self.zones_data = {}
            
        game_zones = self.zones_data.get(target_game, {})
        
        lbl = ctk.CTkLabel(self.zones_scroll, text=f"Target Game: {target_game}", font=("Arial", 16, "bold"))
        lbl.pack(pady=10, anchor="w")
        
        for event_id, config in game_zones.items():
            frame = ctk.CTkFrame(self.zones_scroll)
            frame.pack(fill="x", pady=5, padx=5)
            
            lbl_id = ctk.CTkLabel(frame, text=event_id, width=150, anchor="w")
            lbl_id.pack(side="left", padx=10, pady=10)
            
            box = config.get("box", {})
            lbl_coords = ctk.CTkLabel(frame, text=f"Box: {box}", text_color="gray")
            lbl_coords.pack(side="left", padx=10, pady=10)
            
            btn_edit = ctk.CTkButton(frame, text="Visually Edit", width=100,
                                     command=lambda g=target_game, e=event_id, b=box: self.open_zone_editor(g, e, b))
            btn_edit.pack(side="right", padx=10, pady=10)

    def open_zone_editor(self, game, event_id, box):
        ZoneEditor(self, game, event_id, box, self.on_zone_saved)

    def on_zone_saved(self, game, event_id, new_box):
        if game not in self.zones_data:
            self.zones_data[game] = {}
        if event_id not in self.zones_data[game]:
            self.zones_data[game][event_id] = {}
            
        self.zones_data[game][event_id]["box"] = new_box
        
        zones_file = os.path.join(os.path.dirname(__file__), "zones.json")
        with open(zones_file, "w", encoding="utf-8") as f:
            json.dump(self.zones_data, f, indent=4)
        self.load_zones_ui()

    def toggle_bot(self):
        if self.bot_process is None:
            # Start Bot
            python_exe = os.path.join("venv", "Scripts", "python.exe") if os.path.exists(os.path.join("venv", "Scripts", "python.exe")) else "python"
            self.bot_process = subprocess.Popen([python_exe, "main.py"], cwd=os.path.dirname(__file__))
            self.btn_toggle_bot.configure(text="Stop Bot", fg_color="red", hover_color="darkred")
        else:
            # Stop Bot
            self.bot_process.terminate()
            self.bot_process = None
            self.btn_toggle_bot.configure(text="Start Bot", fg_color="green", hover_color="darkgreen")
            self.append_log("--- BOT STOPPED BY USER ---\n")

    def append_log(self, text):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", text)
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def start_log_tailing(self):
        def tail_log():
            log_file = "bot.log"
            if not os.path.exists(log_file):
                open(log_file, 'a').close()
                
            with open(log_file, "r", encoding="utf-8") as f:
                f.seek(0, 2) # go to end
                while not self.stop_logging:
                    line = f.readline()
                    if not line:
                        time.sleep(0.5)
                        continue
                    # Schedule GUI update
                    self.after(0, self.append_log, line)
                    
        self.log_tail_thread = threading.Thread(target=tail_log, daemon=True)
        self.log_tail_thread.start()

    def on_closing(self):
        self.stop_logging = True
        if self.bot_process:
            self.bot_process.terminate()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
