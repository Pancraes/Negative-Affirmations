import os
import random
import requests
import tkinter as tk
from tkinter import font
from dotenv import load_dotenv
import pygame

load_dotenv('keys.env')
api_key = os.getenv('OPENAI_API_KEY')
pygame.mixer.init()
buzzer_sound = pygame.mixer.Sound("buzzer.mp3")

def play_buzzer():
    """Play the buzzer sound."""
    pygame.mixer.Sound.play(buzzer_sound)

def not_correct(answer):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": """You are the game master behind a game called Negative Affirmations. The code selects a number between 1 and 1000000. 
                by the way, the only way for them to quit is for them to restart their device (assuming they dont win), so maybe say some insults like get off the game for me, or restart your laptop already
                Everytime I prompt you, that means the user did not get it right, and your goal is to negatively affirm the player with something very similar to any of the following:
                Output: youre stupid, quit the game now
                Output: you wont win, youre horrible at this game
                Output: go ahead and log off for me
                Output: youre as good as guessing as the worst guesser on the planet (you)
                Output: restart your computer already you cant win
                Output: restart your laptop already
                (just like my examples, keep the negative affirmations at most under 15 words)"""
            },
            {
                "role": "user",
                "content": f"{answer}"
            }
        ],
        "temperature": 0.5,
        "max_tokens": 50,
        "top_p": 0.85,
        "frequency_penalty": 0.2,
        "presence_penalty": 0.2
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_json = response.json()
    message_content = response_json['choices'][0]['message']['content']
    return message_content

def show_full_screen_message():
    full_screen_win = tk.Tk()
    full_screen_win.attributes('-fullscreen', True)
    full_screen_win.config(bg="green")
    full_screen_win.title("You Guessed Correctly")
    label_font = font.Font(family="Comic Sans MS", size=48)
    label = tk.Label(full_screen_win, text="I HATE YOU", font=label_font, bg="green", fg="white")
    label.pack(expand=True, fill=tk.BOTH)
    full_screen_win.update()
    full_screen_win.after(5000, full_screen_win.quit)


def show_guess_window(correct_number):
    def check_guess(event=None):
        guess = entry.get()
        entry.config(state='disabled')
        entry.pack_forget()
        try:
            guess = int(guess)
        except ValueError:
            label.config(text="Enter a number, idiot", bg="red", wraplength=win.winfo_width())
            win.config(bg="red")
            incorrect_popups.append(win)
            show_guess_window(correct_number)
            play_buzzer()
            return

        if guess == correct_number:
            label.config(text="", bg="green")
            win.config(bg="green")
            for popup in incorrect_popups:
                popup.destroy()
            for popup in escape_popups:
                popup.destroy()
            show_full_screen_message()
        else:
            response = not_correct("no")
            label.config(text=response, bg="red", wraplength=win.winfo_width())
            win.config(bg="red")
            play_buzzer()
            incorrect_popups.append(win)
            show_guess_window(correct_number)



    def on_closing():
        play_buzzer()
        def move_window(win, dx, dy):
            screen_width = win.winfo_screenwidth()
            screen_height = win.winfo_screenheight()
            x = win.winfo_x() + dx
            y = win.winfo_y() + dy
            if x < 0 or x > screen_width - win.winfo_width():
                dx = -dx
            if y < 0 or y > screen_height - win.winfo_height():
                dy = -dy
            win.geometry(f"+{x}+{y}")
            win.after(50, move_window, win, dx, dy)

        for _ in range(6):
            new_win = tk.Toplevel(root)
            new_win.geometry("300x100")
            new_win.title("Escape Attempt")
            screen_width = new_win.winfo_screenwidth()
            screen_height = new_win.winfo_screenheight()
            x = random.randint(0, screen_width - 300)
            y = random.randint(0, screen_height - 100)
            new_win.geometry(f"300x100+{x}+{y}")
            new_win.update_idletasks()
            label_font = font.Font(family="Comic Sans MS", size=16)
            label = tk.Label(new_win, text="you cant escape me", font=label_font, bg="red", fg="white")
            label.pack(expand=True, fill=tk.BOTH, pady=10)
            new_win.config(bg="red")
            new_win.protocol("WM_DELETE_WINDOW", on_closing)
            move_window(new_win, random.randint(1, 5), random.randint(1, 5))
            escape_popups.append(new_win)
    
    win = tk.Toplevel(root)
    win.geometry("300x200")
    win.title("Negative Affirmations")
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = random.randint(0, screen_width - 300)
    y = random.randint(0, screen_height - 200)
    win.geometry(f"300x200+{x}+{y}")
    label_font = font.Font(family="Comic Sans MS", size=16)
    entry_font = font.Font(family="Comic Sans MS", size=16)
    label = tk.Label(win, text="Guess the number I chose\n between 1 and 1000000", font=label_font, bg="white")
    label.pack(pady=10)
    entry = tk.Entry(win, font=entry_font)
    entry.pack(pady=10)
    entry.bind('<Return>', check_guess)
    win.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    correct_number = 6 #random.randint(1, 1000000)
    incorrect_popups = []
    escape_popups = []
    show_guess_window(correct_number)
    root.mainloop()