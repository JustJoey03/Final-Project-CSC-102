import os
import threading
from tkinter import *
import pygame  # Import pygame for the audios
from bomb_configs import COUNTDOWN, NUM_PHASES, NUM_STRIKES
from string import ascii_uppercase

class BombGUI:
    def __init__(self, serial, cipher_keyword, rot):
        # Initialize pygame mixer for audio
        pygame.mixer.init()

        # Load audio files
        self.timer_sound = pygame.mixer.Sound('timer.mp3')
        self.final_countdown_alarm = pygame.mixer.Sound('final_countdown_alarm.mp3')
        self.win_applause = pygame.mixer.Sound('win_applause.mp3')
        self.lose_explosion = pygame.mixer.Sound('lose_explosion.mp3')

        # Start playing the timer sound loop
        self.timer_sound.play(loops=-1, maxtime=0)  # Loop the timer sound indefinitely

        # Set up main window
        self.root = Tk()
        self.root.geometry('1024x576')
        self.root.configure(cursor='none')

        # Load background panel (bomb) using Tkinter
        self.bg_photo = PhotoImage(file="panel_notbombmonitor.png")
        self.canvas = Canvas(self.root,
                             width=self.bg_photo.width(),
                             height=self.bg_photo.height())
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=NW, image=self.bg_photo)

        # ───────────────────────────────────────────────
        # Boot‐screen text overlay (not an image because i previously put a screenshot)
        self.tft_x, self.tft_y = 50, 200
        boot_text = (
            f"Booting...\n\x00\x00\n"
            f"*Kernel v3.1.4-159 loaded.\n"
            f"Initializing subsystems...\n\x00\n"
            f"*System model: 102BOMBv4.2\n"
            f"*Serial number: {serial}\n"
            f"Encrypting keypad...\n\x00\n"
            f"*Keyword: {cipher_keyword}; key: {rot}\n"
            f"*{' '.join(ascii_uppercase)}\n"
            f"*{' '.join(str(n % 10) for n in range(26))}\n"
            f"Rendering phases...\x00"
        )
        
        self.boot_text_id = self.canvas.create_text(
            self.tft_x, self.tft_y,
            text=boot_text,
            font=('Courier', 14),
            fill='#00ff00',
            anchor=NW
        )
        # Removes the boot screen after 3 seconds
        self.root.after(3000, lambda: self.canvas.delete(self.boot_text_id))
        # ───────────────────────────────────────────────

        # Live timer text
        self.timer_text = self.canvas.create_text(
            850, 600,
            text='05:00', font=('Courier', 32),
            fill='#00ff00', anchor=NW
        )

        # Start countdown
        self.time_left = COUNTDOWN
        self._run_timer()

        self.root.mainloop()

    def _run_timer(self):
        mins = self.time_left // 60
        secs = self.time_left % 60
        self.canvas.itemconfigure(
            self.timer_text,
            text=f'{mins:02d}:{secs:02d}'
        )

        if self.time_left == 10:
            # Transition sounds at 10 seconds
            self.timer_sound.stop()
            self.final_countdown_alarm.play()

        if self.time_left > 0:
            self.time_left -= 1
            self.root.after(1000, self._run_timer)
        else:
            self._blow_up()

    def _blow_up(self):
        # Explosion sequence
        self.timer_sound.stop()
        self.final_countdown_alarm.stop()
        self.lose_explosion.play()

        self.canvas.delete('all')
        self.canvas.create_text(
            self.bg_photo.width() // 2,
            self.bg_photo.height() // 2,
            text='💥 BOOM! 💥', font=('Impact', 72),
            fill='red', anchor=CENTER
        )

    def win(self):
        # Win sequence
        self.timer_sound.stop()
        self.final_countdown_alarm.stop()
        self.lose_explosion.stop()
        self.win_applause.play()


if __name__ == '__main__':
    
    serial = "SN-102BOMB-0001"
    cipher_keyword = "SECRET"
    rot = 7

    BombGUI(serial, cipher_keyword, rot)
