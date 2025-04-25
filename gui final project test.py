import os
import threading
from tkinter import *
import tkinter
import pygame  # Import pygame for audio
from bomb_configs import COUNTDOWN, NUM_PHASES, NUM_STRIKES

class BombGUI :
    def __init__(self):
        # Initialize pygame mixer for audio
        pygame.mixer.init()

        # Load audio files
        self.timer_sound = pygame.mixer.Sound('timer.mp3')
        self.final_countdown_alarm = pygame.mixer.Sound('final_countdown_alarm.mp3')
        self.win_applause = pygame.mixer.Sound('win_applause.mp3')
        self.lose_explosion = pygame.mixer.Sound('lose_explosion.mp3')

        # Start playing the timer sound loop
        self.timer_sound.play(loops=-1, maxtime=0)  # Loop the timer sound indefinitely
        
        
        self.root = Tk()
        #self.root.attributes('-fullscreen', True)
        self.root.geometry('1024x576')  
        self.root.configure(cursor='none')
        
        # Load background panel (bomb) using Tkinter
        self.bg_photo = PhotoImage(file="panel_notbombmonitor.png")
        self.canvas = Canvas(self.root,
                             width=self.bg_photo.width(),
                             height=self.bg_photo.height())
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=NW, image=self.bg_photo)

        # Overlays “boot” screen on LCD area
        self.boot_photo = PhotoImage(file='boot.png')
        self.tft_x, self.tft_y = 50, 200
        self.canvas.create_image(
            self.tft_x, self.tft_y, anchor=NW, image=self.boot_photo)

        # Live timer text 
        self.timer_text = self.canvas.create_text(
            850, 600,
            text='05:00', font=('Courier', 32),
            fill='#00ff00', anchor=NW)

        # Starts live countdown
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
            # Stop the timer sound and play the final countdown alarm
            self.timer_sound.stop()
            self.final_countdown_alarm.play()

        if self.time_left > 0:
            self.time_left -= 1
            self.root.after(1000, self._run_timer)
        else:
            self._blow_up()

    def _blow_up(self):
        # Stop all sounds except for the lose explosion
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
        # Stop all sounds and play the win applause
        self.timer_sound.stop()
        self.final_countdown_alarm.stop()
        self.lose_explosion.stop()
        self.win_applause.play()

if __name__ == '__main__':
    BombGUI()
