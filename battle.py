import tkinter as tk
from PIL import Image, ImageTk
import random
import time
import pygame  # 用于播放音乐
import os

class Character:
    def __init__(self, name, hp, image_path):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.image_path = image_path
        self.image = self.load_image(image_path)
        self.hp_bar = None
        self.frame = None

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)

    def load_image(self, path):
        try:
            img = Image.open(path)
            img = img.resize((80, 80), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"加载图片失败 {path}: {e}")
            return None

class TurnBasedGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("回合制对战游戏")

        # 初始化音乐
        pygame.mixer.init()
        try:
            battle_bgm_path = os.path.join('res', 'bgm', 'battle.mp3')
            pygame.mixer.music.load(battle_bgm_path)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"音乐加载失败: {e}")

        self.boss_hp = 500
        self.boss_max_hp = 500
        boss_img_path = os.path.join('res', 'imgs', 'boss.png')
        self.boss_img = self.load_image(boss_img_path, (150, 150))

        role_img_paths = [
            os.path.join('res', 'imgs', 'characters', '1.png'),
            os.path.join('res', 'imgs', 'characters', '2.png'),
            os.path.join('res', 'imgs', 'characters', '3.png'),
            os.path.join('res', 'imgs', 'characters', '4.png')
        ]
        self.roles = [
            Character("战士", 300, role_img_paths[0]),
            Character("法师", 250, role_img_paths[1]),
            Character("弓箭手", 280, role_img_paths[2]),
            Character("牧师", 260, role_img_paths[3])
        ]

        self.canvas = tk.Canvas(self.root, width=700, height=500, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.resize_background)

        self.bg_image = None
        self.bg_image_path = os.path.join('res', 'imgs', 'background.png')
        self.bg_ref = None

        self.create_ui()
        self.root.after(1000, self.start_battle)

    def resize_background(self, event):
        try:
            new_width = event.width
            new_height = event.height
            self.bg_image = Image.open(self.bg_image_path).resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.bg_ref = ImageTk.PhotoImage(self.bg_image)
            self.canvas.delete("bg")
            self.bg_id = self.canvas.create_image(0, 0, image=self.bg_ref, anchor="nw", tags="bg")
            self.canvas.lower(self.bg_id)
        except Exception as e:
            print("背景图调整失败：", e)

    def load_image(self, path, size):
        try:
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"加载图片失败 {path}: {e}")
            return None

    def create_ui(self):
        boss_frame = tk.Frame(self.canvas, bg="#000000", highlightbackground="white", highlightthickness=1)
        self.canvas.create_window(350, 100, window=boss_frame)

        if self.boss_img:
            tk.Label(boss_frame, image=self.boss_img, bg="#000000").pack()
        else:
            tk.Label(boss_frame, text="BOSS", font=("Arial", 20), fg="red", bg="#000000").pack()

        self.boss_hp_canvas = tk.Canvas(boss_frame, width=300, height=20, bg="black")
        self.boss_hp_canvas.pack()
        self.update_boss_hp_bar()

        role_frame = tk.Frame(self.canvas, bg="#000000")
        self.canvas.create_window(350, 350, window=role_frame)

        for role in self.roles:
            frame = tk.Frame(role_frame, bg="#000000")
            frame.pack(side="left", padx=10)
            role.frame = frame

            if role.image:
                tk.Label(frame, image=role.image, bg="#000000").pack()
            else:
                tk.Label(frame, text=role.name, font=("Arial", 12), bg="#000000").pack()

            hp_canvas = tk.Canvas(frame, width=80, height=15, bg="black")
            hp_canvas.pack()
            role.hp_bar = hp_canvas
            self.update_hp_bar(role)

    def update_boss_hp_bar(self):
        self.boss_hp_canvas.delete("all")
        ratio = self.boss_hp / self.boss_max_hp
        fill = int(300 * ratio)
        self.boss_hp_canvas.create_rectangle(0, 0, fill, 20, fill="red")
        self.boss_hp_canvas.create_rectangle(0, 0, 300, 20, outline="white")
        self.boss_hp_canvas.create_text(150, 10, text=f"{self.boss_hp}/{self.boss_max_hp}", fill="white")

    def update_hp_bar(self, role):
        role.hp_bar.delete("all")
        ratio = role.hp / role.max_hp
        fill = int(80 * ratio)
        role.hp_bar.create_rectangle(0, 0, fill, 15, fill="green")
        role.hp_bar.create_rectangle(0, 0, 80, 15, outline="white")
        role.hp_bar.create_text(40, 8, text=f"{role.hp}/{role.max_hp}", fill="white")

    def start_battle(self):
        self.turn_loop()

    def turn_loop(self):
        if self.boss_hp <= 0:
            self.show_message("胜利！BOSS已被击败！")
            return

        alive_roles = [r for r in self.roles if r.is_alive()]
        if not alive_roles:
            self.show_message("失败！所有角色阵亡！")
            return

        for role in alive_roles:
            if self.boss_hp <= 0:
                break
            damage = random.randint(80, 120)
            self.boss_hp = max(0, self.boss_hp - damage)
            self.update_boss_hp_bar()
            print(f"{role.name} 对BOSS造成了 {damage} 点伤害！")
            self.root.update()
            time.sleep(0.6)

        if self.boss_hp <= 0:
            self.show_message("胜利！BOSS已被击败！")
            return

        target = random.choice(alive_roles)
        damage = random.randint(100, 160)
        target.take_damage(damage)
        self.update_hp_bar(target)
        print(f"BOSS 攻击了 {target.name}，造成了 {damage} 点伤害！")
        self.root.update()
        time.sleep(0.8)

        self.root.after(1000, self.turn_loop)

    def show_message(self, msg):
        win = tk.Toplevel(self.root)
        win.title("战斗结果")
        tk.Label(win, text=msg, font=("Arial", 16)).pack(padx=20, pady=20)
        tk.Button(win, text="关闭", command=self.quit_game).pack(pady=10)
        win.after(3000, self.quit_game)  # 新增：3秒后自动关闭

    def quit_game(self):
        pygame.mixer.music.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("700x500")
    app = TurnBasedGameGUI(root)
    root.mainloop()