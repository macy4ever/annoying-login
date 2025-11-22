import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import random
import pyautogui
import os
import time

# ---------------- SETTINGS ----------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1600x1000")
app.title("Bad Login")

active_entry = None
move_count = 0
max_moves = 25
cooldown = False
cooldown_time = 25000  # 25 seconds
last_mouse_pos = None

# Load 5-letter words from txt file
WORDLE_WORDS = []
word_file_path = "wordlist.txt"
if os.path.exists(word_file_path):
    with open(word_file_path, "r") as f:
        for line in f:
            word = line.strip().upper()
            if len(word) == 5:
                WORDLE_WORDS.append(word)
else:
    WORDLE_WORDS = ["APPLE", "PEACH", "GRAPE", "MANGO", "BERRY"]

# ---------------- ACTIVE ENTRY ----------------
def set_active_entry_username(event):
    global active_entry
    active_entry = user_entry

def set_active_entry_password(event):
    global active_entry
    active_entry = user_pass

def block_physical_keys(event):
    return "break"

def insert_text(char):
    if active_entry is not None:
        active_entry.insert("end", char)

def backspace():
    if active_entry is not None and len(active_entry.get()) > 0:
        active_entry.delete(len(active_entry.get()) - 1, "end")

# ---------------- LOGIN ----------------
def login():
    username = "PE"
    password = "PE"
    if user_entry.get() == username and user_pass.get() == password:
        messagebox.showinfo("Login Successful", "You have logged in Successfully")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

# ---------------- MOVING BUTTON ----------------
def start_cooldown():
    global cooldown
    cooldown = True
    app.after(cooldown_time, end_cooldown)

def end_cooldown():
    global cooldown, move_count
    cooldown = False
    move_count = 0
    move_button()

def move_button(event=None):
    global move_count, max_moves, cooldown
    if cooldown:
        return
    if move_count >= max_moves:
        start_cooldown()
        return
    move_count += 1
    rel_x = random.uniform(0.1, 0.9)
    rel_y = random.uniform(0.1, 0.45)
    login_button.place(relx=rel_x, rely=rel_y, anchor="center")
    login_button.lift()

def check_proximity(event):
    if cooldown:
        return
    bx = login_button.winfo_x()
    by = login_button.winfo_y()
    bw = login_button.winfo_width()
    bh = login_button.winfo_height()
    if abs(event.x - (bx + bw / 2)) < 60 and abs(event.y - (by + bh / 2)) < 60:
        move_button()

# ---------------- MOUSE INVERSION ----------------
def invert_cursor(event):
    global last_mouse_pos
    x, y = event.x_root, event.y_root
    if last_mouse_pos is None:
        last_mouse_pos = (x, y)
        return
    dx = x - last_mouse_pos[0]
    dy = y - last_mouse_pos[1]
    new_x = pyautogui.position().x - dx
    new_y = pyautogui.position().y - dy
    pyautogui.moveTo(new_x, new_y)
    last_mouse_pos = (x, y)

# ---------------- NUMBER SHUFFLE ----------------
class NumberShuffleGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Number Shuffle")
        self.master.geometry("400x450")
        self.master.resizable(False, False)
        self.numbers = list(range(1, 16)) + [0]
        self.shuffle_board()
        self.buttons = []
        self.clicks = 0
        self.running_timer = True
        self.create_widgets()

    def create_widgets(self):
        self.board_frame = tk.Frame(self.master, bg="#00a86b")
        self.board_frame.pack(pady=20)
        self.draw_board()

    def draw_board(self):
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        self.buttons = []
        for i in range(16):
            num = self.numbers[i]
            btn = tk.Button(
                self.board_frame,
                text=str(num) if num != 0 else "",
                font=("Arial", 16),
                width=4,
                height=2,
                command=lambda i=i: self.move_tile(i)
            )
            btn.grid(row=i // 4, column=i % 4, padx=3, pady=3)
            self.buttons.append(btn)

    def move_tile(self, index):
        zero_index = self.numbers.index(0)
        valid_moves = [zero_index - 1, zero_index + 1, zero_index - 4, zero_index + 4]
        if zero_index % 4 == 0 and index == zero_index - 1:
            return
        if zero_index % 4 == 3 and index == zero_index + 1:
            return
        if index in valid_moves:
            self.numbers[zero_index], self.numbers[index] = self.numbers[index], self.numbers[zero_index]
            self.clicks += 1
            self.draw_board()
            self.check_win()

    def check_win(self):
        if self.numbers[:-1] == list(range(1, 16)):
            self.running_timer = False

    def shuffle_board(self):
        while True:
            random.shuffle(self.numbers)
            if self.is_solvable():
                break

    def is_solvable(self):
        arr = self.numbers
        inversions = 0
        for i in range(15):
            for j in range(i + 1, 15):
                if arr[i] and arr[j] and arr[i] > arr[j]:
                    inversions += 1
        zero_row = arr.index(0) // 4
        return (inversions + zero_row) % 2 == 0

# ---------------- PUZZLE LOGIC ----------------
def generate_puzzle(char, on_success):
    puzzle_type = random.choice(["number_shuffle", "wordle", "snake"])

    if puzzle_type == "number_shuffle":
        win = tk.Toplevel(app)
        win.attributes("-topmost", True)
        game = NumberShuffleGame(win)
        def check_win_loop():
            if not game.running_timer:
                win.destroy()
                on_success()
            else:
                win.after(500, check_win_loop)
        check_win_loop()

    elif puzzle_type == "wordle":
        words_5 = [w for w in WORDLE_WORDS if len(w) == 5]
        word = random.choice(words_5) if words_5 else "APPLE"

        def start_wordle():
            win = ctk.CTkToplevel(app)
            win.attributes("-topmost", True)
            win.geometry("350x200")
            win.title("Wordle Mini Puzzle")

            ctk.CTkLabel(win, text=f"Guess the 5-letter word").pack(pady=10)
            entry = ctk.CTkEntry(win)
            entry.pack(pady=10)
            feedback_label = ctk.CTkLabel(win, text="")
            feedback_label.pack()
            attempts = 10

            def check():
                nonlocal attempts
                guess = entry.get().upper()
                if guess == word:
                    win.destroy()
                    on_success()
                    return
                else:
                    feedback = ""
                    for i in range(5):
                        if i < len(guess):
                            if guess[i] == word[i]:
                                feedback += f"[{guess[i]}]"
                            elif guess[i] in word:
                                feedback += f"({guess[i]})"
                            else:
                                feedback += guess[i]
                        else:
                            feedback += "_"
                    feedback_label.configure(text=f"Feedback: {feedback}")
                    attempts -= 1
                    if attempts <= 0:
                        win.destroy()
                        start_wordle()  # restart puzzle

            ctk.CTkButton(win, text="Submit", command=check).pack(pady=10)

        start_wordle()

    elif puzzle_type == "snake":
        win = tk.Toplevel(app)
        win.attributes("-topmost", True)
        win.title("Snake Mini Puzzle")
        win.geometry("400x400")
        canvas = tk.Canvas(win, bg="#FEB6C1", height=350, width=350)
        canvas.pack(pady=10)

        SPEED = 300
        score = 0
        direction = "right"

        class Snake:
            def __init__(self):
                self.size = 2
                self.location = []
                self.body = []
                for i in range(self.size):
                    self.location.append([0, 0])
                for x, y in self.location:
                    segment = canvas.create_rectangle(x, y, x + 70, y + 70, fill="#9bdeac")
                    self.body.append(segment)

        class Food:
            def __init__(self, snake):
                x = random.randint(0, 4) * 70
                y = random.randint(0, 4) * 70
                self.location = [x, y]
                canvas.create_oval(x + 10, y + 10, x + 50, y + 50, fill="#67001e", tag="food")

        snake = Snake()
        food = Food(snake)

        def movement():
            nonlocal score, food, direction
            x, y = snake.location[0]
            if direction == "up":
                y -= 70
            elif direction == "down":
                y += 70
            elif direction == "left":
                x -= 70
            elif direction == "right":
                x += 70

            snake.location.insert(0, [x, y])
            segment = canvas.create_rectangle(x, y, x + 70, y + 70, fill="#9bdeac")
            snake.body.insert(0, segment)

            if x == food.location[0] and y == food.location[1]:
                canvas.delete("food")
                score += 1
                food = Food(snake)
            else:
                del snake.location[-1]
                canvas.delete(snake.body[-1])
                del snake.body[-1]

            if check_collisions(snake):
                canvas.delete("all")
                canvas.create_text(175, 175, text="You failed :(", fill="red", font=("Arial", 14))
                win.after(1000, lambda: (win.destroy(), generate_puzzle(char, on_success)))
                return

            if score >= 5:
                canvas.delete("all")
                canvas.create_text(175, 175, text="You Win! Puzzle Solved!", fill="green", font=("Arial", 14))
                win.after(500, lambda: (win.destroy(), on_success()))
                return

            win.after(SPEED, movement)

        def check_collisions(snake_obj):
            x, y = snake_obj.location[0]
            if x < 0 or x >= 350 or y < 0 or y >= 350:
                return True
            for segment in snake_obj.location[1:]:
                if x == segment[0] and y == segment[1]:
                    return True
            return False

        def change_direction(event):
            nonlocal direction
            key = event.keysym.lower()
            if key == "left" and direction != "right":
                direction = "left"
            elif key == "right" and direction != "left":
                direction = "right"
            elif key == "up" and direction != "down":
                direction = "up"
            elif key == "down" and direction != "up":
                direction = "down"

        win.bind("<Left>", change_direction)
        win.bind("<Right>", change_direction)
        win.bind("<Up>", change_direction)
        win.bind("<Down>", change_direction)

        movement()

# ---------------- INSERT TEXT WITH PUZZLE ----------------
def insert_text_with_puzzle(char):
    for child in keyboard_frame.winfo_children():
        for btn in child.winfo_children():
            btn.configure(state="disabled")
    def on_success():
        messagebox.showinfo("Success!", "Puzzle solved! Letter unlocked.")
        for child in keyboard_frame.winfo_children():
            for btn in child.winfo_children():
                btn.configure(state="normal")
        insert_text(char)
    generate_puzzle(char, on_success)

# ---------------- UI ----------------
frame = ctk.CTkFrame(app)
frame.pack(fill="both", expand=True, padx=30, pady=30)

ctk.CTkLabel(frame, text="Annoying Login").pack(pady=10)

user_entry = ctk.CTkEntry(frame, placeholder_text="Username")
user_entry.pack(pady=10)
user_entry.bind("<FocusIn>", set_active_entry_username)
user_entry.bind("<Key>", block_physical_keys)

user_pass = ctk.CTkEntry(frame, placeholder_text="Password", show="*")
user_pass.pack(pady=10)
user_pass.bind("<FocusIn>", set_active_entry_password)
user_pass.bind("<Key>", block_physical_keys)

login_button = ctk.CTkButton(frame, text="Login", command=login)
login_button.place(relx=0.5, rely=0.55, anchor="center")

checkbox = ctk.CTkCheckBox(frame, text="Remember Me")
checkbox.pack(pady=10)

# ---------------- ON-SCREEN KEYBOARD ----------------
keyboard_frame = ctk.CTkFrame(frame)
keyboard_frame.pack(pady=40)

keys_row1 = "QWERTYUIOP"
keys_row2 = "ASDFGHJKL"
keys_row3 = "ZXCVBNM"

def make_keyboard_row(chars):
    row = ctk.CTkFrame(keyboard_frame)
    row.pack(pady=5)
    for c in chars:
        ctk.CTkButton(row, text=c, width=50,
                      command=lambda ch=c: insert_text_with_puzzle(ch)).pack(side="left", padx=3)
    return row

make_keyboard_row(keys_row1)
make_keyboard_row(keys_row2)
make_keyboard_row(keys_row3)

numbers_row = ctk.CTkFrame(keyboard_frame)
numbers_row.pack(pady=5)
for n in "1234567890":
    ctk.CTkButton(numbers_row, text=n, width=50,
                  command=lambda ch=n: insert_text_with_puzzle(ch)).pack(side="left", padx=3)

bottom_row = ctk.CTkFrame(keyboard_frame)
bottom_row.pack(pady=10)
ctk.CTkButton(bottom_row, text="Space", width=200,
              command=lambda: insert_text_with_puzzle(" ")).pack(side="left", padx=5)
ctk.CTkButton(bottom_row, text="⌫ Backspace", width=150, command=backspace).pack(side="left", padx=5)

# ---------------- ARE YOU STILL THERE ----------------
def ask_user():
    messagebox.askyesno("Still there?", "Are you still there?")
    app.after(15000, ask_user)

app.after(15000, ask_user)

# ---------------- BINDINGS ----------------
def combined_motion(event):
    invert_cursor(event)
    check_proximity(event)

frame.bind("<Motion>", combined_motion)
login_button.bind("<Enter>", move_button)
app.bind("<Key>", block_physical_keys)

# ---------------- RUN APP ----------------
app.mainloop()
