import json
import os
import customtkinter as ctk

DATA_FILE = "games.json"

class GameTracker(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Game Backlog Tracker")
        self.geometry("500x580")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.games = self.load_data()
        
        self.header_title = ctk.CTkLabel(self, text="🎮 Game Tracker", font=("Arial", 26, "bold"))
        self.header_title.pack(pady=(20, 5))
        
        self.header_subtitle = ctk.CTkLabel(self, text="Eng/Khalid Mabrouk", font=("Arial", 16), text_color="gray70")
        self.header_subtitle.pack(pady=(0, 20))
        
        self.title_entry = ctk.CTkEntry(self, width=300, placeholder_text="Enter Game Title (e.g., Elden Ring)")
        self.title_entry.pack(pady=(0, 15))
        
        self.status_option = ctk.CTkOptionMenu(self, width=300, values=["Completed", "Playing", "Plan to Play"])
        self.status_option.pack(pady=(0, 20))
        
        self.add_button = ctk.CTkButton(self, text="Add / Update Game", width=300, command=self.add_or_update_game)
        self.add_button.pack(pady=(0, 20))
        
        self.display_box = ctk.CTkTextbox(self, width=400, height=250, font=("Consolas", 14))
        self.display_box.pack(pady=(0, 20))
        
        self.refresh_display()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return []

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.games, f, indent=4)

    def add_or_update_game(self):
        title = self.title_entry.get().strip().title()
        status = self.status_option.get()
        
        if not title:
            return
            
        found = False
        for game in self.games:
            if game["Title"].lower() == title.lower():
                game["Status"] = status
                found = True
                break
                
        if not found:
            self.games.append({"Title": title, "Status": status})
            
        self.save_data()
        self.title_entry.delete(0, "end")
        self.refresh_display()

    def refresh_display(self):
        self.display_box.configure(state="normal")
        self.display_box.delete("1.0", "end")
        
        if not self.games:
            self.display_box.insert("end", "Your backlog is empty. Add some games!\n")
        else:
            completed = sum(1 for g in self.games if g["Status"] == "Completed")
            rate = round((completed / len(self.games)) * 100, 2)
            
            self.display_box.insert("end", f"🏆 Completion Rate: {rate}%\n")
            self.display_box.insert("end", "-" * 40 + "\n")
            
            for game in self.games:
                self.display_box.insert("end", f"• {game['Title']} [{game['Status']}]\n")
                
        self.display_box.configure(state="disabled")

if __name__ == "__main__":
    app = GameTracker()
    app.mainloop()