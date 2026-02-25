import sys
import json
import os
import requests
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import pygame

DATA_FILE = "games.json"
SETTINGS_FILE = "settings.json"
COVER_DIR = "covers"
RAWG_API_KEY = "5d00c46fe8f744b290208aad28418859"

class GameTracker(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Game Vault - Pro Edition")
        self.geometry("1300x900")
        self.configure(fg_color="#0d0d12")
        
        try: pygame.mixer.init()
        except: pass
        
        if not os.path.exists(COVER_DIR): os.makedirs(COVER_DIR)
            
        self.games = self.load_data()
        self.settings = self.load_settings()
        self.image_path_var = None
        self.current_index = {"Completed": 0, "Playing": 0, "Plan to Play": 0}
        self.is_downloading = False
        
        self.bg_hex = "#0d0d12"
        self.logo_hex = "#00ffcc"
        self.text_hex = "#ffffff"
        self.dev_hex = "#aaaaaa"
        
        self.show_splash()

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f: return json.load(f)
            except: return []
        return []

    def save_data(self):
        with open(DATA_FILE, "w") as f: json.dump(self.games, f, indent=4)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f: return json.load(f)
        return {}

    def save_settings(self, name):
        with open(SETTINGS_FILE, "w") as f: json.dump({"user_name": name}, f)

    def play_sfx(self, sound):
        try: 
            sound_file = self.resource_path(f"{sound}.wav")
            pygame.mixer.Sound(sound_file).play()
        except: pass

    def interpolate_color(self, color1, color2, factor):
        c1 = [int(color1.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
        c2 = [int(color2.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
        res = [int(c1[i] + (c2[i] - c1[i]) * factor) for i in range(3)]
        return f"#{res[0]:02x}{res[1]:02x}{res[2]:02x}"

    def fade_text(self, label, start, end, callback=None, current=0):
        if current <= 25:
            label.configure(text_color=self.interpolate_color(start, end, current/25))
            self.after(25, lambda: self.fade_text(label, start, end, callback, current + 1))
        elif callback: callback()

    def show_splash(self):
        self.splash_frame = ctk.CTkFrame(self, fg_color=self.bg_hex, corner_radius=0)
        self.splash_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.splash_center = ctk.CTkFrame(self.splash_frame, fg_color="transparent")
        self.splash_center.place(relx=0.5, rely=0.5, anchor="center")
        
        self.sp_logo = ctk.CTkLabel(self.splash_center, text="GameTracker 🎮", font=("Segoe UI", 65, "bold"), text_color=self.bg_hex)
        self.sp_logo.pack()
        self.fade_text(self.sp_logo, self.bg_hex, self.logo_hex, self.splash_logo_hold)

    def splash_logo_hold(self):
        self.after(1500, self.splash_logo_fade_out)

    def splash_logo_fade_out(self):
        self.fade_text(self.sp_logo, self.logo_hex, self.bg_hex, self.splash_dev_in)

    def splash_dev_in(self):
        self.sp_logo.pack_forget()
        self.sp_dev = ctk.CTkLabel(self.splash_center, text="Developed By", font=("Segoe UI", 24), text_color=self.bg_hex)
        self.sp_dev.pack()
        self.sp_name = ctk.CTkLabel(self.splash_center, text="Eng. Khalid Mabrouk", 
                                    font=ctk.CTkFont("Palatino Linotype", 50, "bold", "italic"), text_color=self.bg_hex)
        self.sp_name.pack()
        self.fade_text(self.sp_dev, self.bg_hex, self.dev_hex)
        self.after(1000, lambda: self.fade_text(self.sp_name, self.bg_hex, self.text_hex, self.splash_dev_hold))

    def splash_dev_hold(self):
        self.after(2000, self.splash_dev_fade_out)

    def splash_dev_fade_out(self):
        self.fade_text(self.sp_dev, self.dev_hex, self.bg_hex)
        self.fade_text(self.sp_name, self.text_hex, self.bg_hex, self.check_user_name_flow)

    def check_user_name_flow(self):
        self.splash_frame.destroy()
        if "user_name" not in self.settings:
            self.show_mario_input()
        else:
            self.user_name = self.settings["user_name"]
            self.start_main_app()

    def show_mario_input(self):
        self.mario_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        self.mario_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        lbl = ctk.CTkLabel(self.mario_frame, text="إزيك أيها الجيمر\n...إكتب إسمك", font=("Courier New", 50, "bold"), text_color="#000000")
        lbl.place(relx=0.5, rely=0.35, anchor="center")
        self.name_entry = ctk.CTkEntry(self.mario_frame, width=350, height=50, placeholder_text="NAME...", font=("Courier New", 25), fg_color="#ffffff", text_color="#000000", border_color="#000000")
        self.name_entry.place(relx=0.5, rely=0.5, anchor="center")
        self.name_entry.focus_set()
        btn = ctk.CTkButton(self.mario_frame, text="START", font=("Courier New", 20, "bold"), fg_color="#000000", text_color="#ffffff", command=self.set_user_name)
        btn.place(relx=0.5, rely=0.6, anchor="center")
        
        note_text = "💡 ملحوظة: تقدر تختار غلاف اللعبة من جهازك، أو تسيب البرنامج يجيبه من النت أوتوماتيك"
        note_lbl = ctk.CTkLabel(self.mario_frame, text=note_text, font=("Courier New", 18, "bold"), text_color="#666666")
        note_lbl.place(relx=0.5, rely=0.75, anchor="center")

    def set_user_name(self):
        name = self.name_entry.get().strip().upper()
        if name:
            self.play_sfx("success")
            self.user_name = name
            self.save_settings(name)
            self.mario_frame.destroy()
            self.start_main_app()

    def start_main_app(self):
        self.setup_ui()
        self.refresh_display()

    def setup_ui(self):
        self.grid_rowconfigure(0, weight=1); self.grid_columnconfigure(1, weight=1)
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#171721")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="GameTracker 🎮", font=("Impact", 35), text_color="#00ffcc").pack(pady=(40, 5), padx=20, anchor="w")
        self.user_lbl = ctk.CTkLabel(self.sidebar, text=f"{self.user_name} Dashboard", font=("Segoe UI", 16, "bold"), text_color="#ffffff")
        self.user_lbl.pack(padx=20, anchor="w")
        ctk.CTkButton(self.sidebar, text="EDIT NAME", height=25, fg_color="#2d2d3f", command=self.edit_name).pack(padx=20, pady=10, anchor="w")
        
        self.stats = ctk.CTkFrame(self.sidebar, fg_color="#222230", corner_radius=15)
        self.stats.pack(padx=20, pady=20, fill="x")
        self.total_lbl = ctk.CTkLabel(self.stats, text="Total: 0", font=("Segoe UI", 14), text_color="#a0a0b5")
        self.total_lbl.pack(pady=(15, 5), padx=15, anchor="w")
        self.rate_lbl = ctk.CTkLabel(self.stats, text="Completed: 0%", font=("Segoe UI", 14, "bold"), text_color="#00ffcc")
        self.rate_lbl.pack(pady=5, padx=15, anchor="w")
        
        self.prog_bar = ctk.CTkProgressBar(self.stats, height=8, fg_color="#171721", progress_color="#00ffcc")
        self.prog_bar.pack(pady=(10, 20), padx=15, fill="x")
        self.prog_bar.set(0)

        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.ctrl = ctk.CTkFrame(self.main, fg_color="#1a1a24", corner_radius=15)
        self.ctrl.pack(fill="x", pady=(0, 20))
        self.title_entry = ctk.CTkEntry(self.ctrl, placeholder_text="Game Title...", height=45)
        self.title_entry.pack(side="left", padx=20, pady=20, expand=True, fill="x")
        self.status_menu = ctk.CTkOptionMenu(self.ctrl, values=["Completed", "Playing", "Plan to Play"], fg_color="#222230")
        self.status_menu.pack(side="left", padx=10, pady=20)
        self.file_btn = ctk.CTkButton(self.ctrl, text="🖼️ Browse Cover", width=130, height=45, fg_color="#2d2d3f", command=self.browse_image)
        self.file_btn.pack(side="left", padx=10, pady=20)
        self.add_btn = ctk.CTkButton(self.ctrl, text="ADD GAME", fg_color="#00ffcc", text_color="#0d0d12", font=("Segoe UI", 14, "bold"), command=self.add_or_update_game)
        self.add_btn.pack(side="left", padx=(10, 20), pady=20)

        self.tabview = ctk.CTkTabview(self.main, fg_color="#1a1a24", segmented_button_selected_color="#00ffcc")
        self.tabview.pack(expand=True, fill="both")
        self.tabs = {}
        for s in ["Completed", "Playing", "Plan to Play"]:
            self.tabs[s] = self.tabview.add(s)
            self.setup_tab_ui(s)

    def setup_tab_ui(self, status):
        tab = self.tabs[status]

        tab.grid_columnconfigure(0, weight=1) 
        tab.grid_columnconfigure(1, weight=3) 
        tab.grid_rowconfigure(0, weight=1)
        tab.list_frame = ctk.CTkScrollableFrame(tab, width=220, corner_radius=15, fg_color="#222230")
        tab.list_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=15)

        tab.main_frame = ctk.CTkFrame(tab, fg_color="transparent")
        tab.main_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=15)

        self.img_w, self.img_h = 750, 420
        tab.img = ctk.CTkLabel(tab.main_frame, text="", width=self.img_w, height=self.img_h, corner_radius=15, fg_color="#000000")
        tab.img.pack(pady=5)
        
        tab.name = ctk.CTkLabel(tab.main_frame, text="EMPTY", font=("Segoe UI", 35, "bold"))
        tab.name.pack(pady=5)
        
        btns = ctk.CTkFrame(tab.main_frame, fg_color="transparent")
        btns.pack(pady=10)
        ctk.CTkButton(btns, text="◄", width=70, fg_color="#2d2d3f", command=lambda s=status: self.change_game(s, -1)).grid(row=0, column=0, padx=10)
        ctk.CTkButton(btns, text="DELETE", width=120, fg_color="#ff3366", font=("Segoe UI", 12, "bold"), command=lambda s=status: self.delete_game(s)).grid(row=0, column=1, padx=10)
        ctk.CTkButton(btns, text="►", width=70, fg_color="#2d2d3f", command=lambda s=status: self.change_game(s, 1)).grid(row=0, column=2, padx=10)

    def select_game(self, status, index):
        self.play_sfx("click")
        self.current_index[status] = index
        self.update_tab_view(status)

    def browse_image(self):
        self.play_sfx("click")
        p = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if p:
            self.image_path_var = p
            self.file_btn.configure(text="✔️ Ready", fg_color="#00ffcc", text_color="#0d0d12")

    def edit_name(self):
        self.play_sfx("click")
        d = ctk.CTkInputDialog(text="New Player Name:", title="Edit Name")
        res = d.get_input()
        if res:
            self.user_name = res; self.save_settings(res)
            self.user_lbl.configure(text=f"{res} Dashboard")

    def add_or_update_game(self):
        if self.is_downloading: return
        t = self.title_entry.get().strip().title()
        s = self.status_menu.get()
        if not t: return
        self.play_sfx("click"); self.is_downloading = True
        self.add_btn.configure(text="Searching...", state="disabled")
        threading.Thread(target=self.thread_fetch, args=(t, s, self.image_path_var), daemon=True).start()

    def thread_fetch(self, title, status, manual):
        path = manual if manual else ""
        if not manual:
            url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={title}&page_size=1"
            try:
                r = requests.get(url, timeout=10).json()
                if r.get("results"):
                    u = r["results"][0].get("background_image")
                    if u:
                        b = requests.get(u, timeout=10).content
                        safe = "".join(x for x in title if x.isalnum())
                        path = os.path.join(COVER_DIR, f"{safe}.jpg")
                        with open(path, "wb") as f: f.write(b)
            except: pass
        self.after(0, lambda: self.finalize_add(title, status, path))

    def finalize_add(self, title, status, path):
        self.games = [g for g in self.games if g["Title"].lower() != title.lower()]
        self.games.append({"Title": title, "Status": status, "Image": path})
        self.save_data(); self.play_sfx("success")
        self.title_entry.delete(0, "end"); self.image_path_var = None
        self.file_btn.configure(text="🖼️ Browse Cover", fg_color="#2d2d3f", text_color="#ffffff")
        self.add_btn.configure(text="ADD GAME", state="normal")
        self.is_downloading = False; self.refresh_display()

    def delete_game(self, status):
        sg = [g for g in self.games if g["Status"] == status]
        if not sg: return
        self.play_sfx("delete")
        target = sg[self.current_index[status]]
        self.games = [g for g in self.games if not (g["Title"] == target["Title"] and g["Status"] == target["Status"])]
        self.save_data(); self.refresh_display()

    def change_game(self, status, direction):
        sg = [g for g in self.games if g["Status"] == status]
        if not sg: return
        self.play_sfx("click")
        self.current_index[status] = (self.current_index[status] + direction) % len(sg)
        self.update_tab_view(status)

    def refresh_display(self):
        total = len(self.games); self.total_lbl.configure(text=f"Total: {total}")
        comp = sum(1 for g in self.games if g["Status"] == "Completed")
        rate = round((comp/total*100), 1) if total > 0 else 0
        self.rate_lbl.configure(text=f"Completed: {rate}%")
        self.prog_bar.set(rate / 100) 
        for s in ["Completed", "Playing", "Plan to Play"]:
            sg = [g for g in self.games if g["Status"] == s]
            if not sg: self.current_index[s] = 0
            elif self.current_index[s] >= len(sg): self.current_index[s] = max(0, len(sg)-1)
            self.update_tab_view(s)

    def update_tab_view(self, status):
        tab = self.tabs[status]; sg = [g for g in self.games if g["Status"] == status]
        
        for widget in tab.list_frame.winfo_children():
            widget.destroy()

        if not sg:
            tab.name.configure(text="NO GAMES"); tab.img.configure(image=None); return
            
        for i, game in enumerate(sg):
            is_selected = (i == self.current_index[status])
            bg_col = "#00ffcc" if is_selected else "#2d2d3f"
            txt_col = "#0d0d12" if is_selected else "#ffffff"
            
            btn = ctk.CTkButton(tab.list_frame, text=game["Title"], 
                                fg_color=bg_col, text_color=txt_col,
                                font=("Segoe UI", 14, "bold"), anchor="w",
                                command=lambda s=status, idx=i: self.select_game(s, idx))
            btn.pack(fill="x", pady=5, padx=5)

        curr = sg[self.current_index[status]]
        tab.name.configure(text=f"{curr['Title']} ({self.current_index[status]+1}/{len(sg)})")
        try:
            if curr.get("Image") and os.path.exists(curr["Image"]):
                with Image.open(curr["Image"]) as img:
                    tab.img.configure(image=ctk.CTkImage(img, size=(self.img_w, self.img_h)))
            else: tab.img.configure(image=None)
        except: tab.img.configure(image=None)

if __name__ == "__main__":
    app = GameTracker(); app.mainloop()