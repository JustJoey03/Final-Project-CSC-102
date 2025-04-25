#Keypad Memory Trap with a GUI
#A memory puzzle game with a timer and interactive keypad.

import tkinter as tk
from tkinter import messagebox
import random
from bomb_configs import keypad_keys, NUM_PHASES, NUM_STRIKES

class KeypadMemoryTrapGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Keypad Memory Trap")
        self.resizable(False, False)

        # Game variables
        self.rows = len(keypad_keys)
        self.cols = len(keypad_keys[0])
        self.sequences = []          # list of rounds: each is list of symbols
        self.stage = 0               # current challenge stage
        self.strikes = NUM_STRIKES
        self.time_left = 60          # global countdown (seconds)

        # interface setup
        self._create_widgets()
        self._layout_widgets()
        self._bind_events()

        # Starts the countdown timer
        self._update_timer()

    def _create_widgets(self):
        self.label_info = tk.Label(self, text="Welcome to Keypad Memory Trap!", font=("Arial", 14))
        self.label_timer = tk.Label(self, text=f"Time: {self.time_left}s", font=("Arial", 12))
        self.label_strikes = tk.Label(self, text=f"Strikes: {self.strikes}", font=("Arial", 12))
        self.label_round = tk.Label(self, text="", font=("Arial", 16))
        # Frame for keypad buttons
        self.frame_keys = tk.Frame(self)
        self.buttons = {}
        for r in range(self.rows):
            for c in range(self.cols):
                symbol = str(keypad_keys[r][c])
                btn = tk.Button(self.frame_keys, text=symbol, width=4, height=2,
                                font=("Courier", 14), state=tk.DISABLED,
                                command=lambda s=symbol: self._on_key_press(s))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.buttons[symbol] = btn
        self.button_start = tk.Button(self, text="Start Game", font=("Arial", 12), command=self._start_game)

    def _layout_widgets(self):
        self.label_info.grid(row=0, column=0, columnspan=2, pady=5)
        self.label_timer.grid(row=1, column=0, sticky="w", padx=5)
        self.label_strikes.grid(row=1, column=1, sticky="e", padx=5)
        self.label_round.grid(row=2, column=0, columnspan=2, pady=10)
        self.frame_keys.grid(row=3, column=0, columnspan=2)
        self.button_start.grid(row=4, column=0, columnspan=2, pady=10)

    def _bind_events(self):
        self.bind('<Return>', lambda e: self._next_round())

    def _update_timer(self):
        if self.time_left <= 0:
            messagebox.showinfo("Time's up!", "Game Over — Time expired.")
            self.destroy()
            return
        self.label_timer.config(text=f"Time: {self.time_left}s")
        self.time_left -= 1
        self.after(1000, self._update_timer)

    def _start_game(self):
        self.button_start.config(state=tk.DISABLED)
        self.label_info.config(text="Memorize the sequences. Press Enter to advance.")
        # Generates the sequences
        symbols_flat = [str(k) for row in keypad_keys for k in row]
        for rnd in range(NUM_PHASES):
            seq = random.sample(symbols_flat, 4)
            self.sequences.append(seq)
        self.current_round = 0
        self._show_round()

    def _show_round(self):
        if self.current_round < NUM_PHASES:
            seq = self.sequences[self.current_round]
            self.label_round.config(text=f"Round {self.current_round+1}: {' '.join(seq)}")
        else:
            # All rounds shown which begins the challenges 
            self.stage = 1
            self.label_info.config(text="Challenges: Click the correct key.")
            self._next_challenge()

    def _next_round(self):
        if self.button_start['state'] == tk.NORMAL:
            return  # game not started
        self.current_round += 1
        self._show_round()

    def _next_challenge(self):
        for btn in self.buttons.values():
            btn.config(state=tk.NORMAL)
        # Determine challenges
        rnd = random.randint(1, self.stage)
        pos = random.randint(1, 4)
        self.current_target = self.sequences[rnd-1][pos-1]
        self.label_round.config(
            text=f"Stage {self.stage}: Press the {pos}ⁿᵈ symbol from round {rnd}")

    def _on_key_press(self, symbol):
        if symbol == self.current_target:
            self.label_info.config(text="Correct!")
            # disables until nextt
            for btn in self.buttons.values(): btn.config(state=tk.DISABLED)
            self.stage += 1
            if self.stage > NUM_PHASES:
                messagebox.showinfo("Success", "Congratulations! You defused the trap.")
                self.destroy()
                return
            self.after(500, self._next_challenge)
        else:
            self.strikes -= 1
            self.label_strikes.config(text=f"Strikes: {self.strikes}")
            self.label_info.config(text=f"Wrong! The correct was {self.current_target}")
            if self.strikes <= 0:
                messagebox.showinfo("Game Over", "You’ve run out of strikes.")
                self.destroy()

if __name__ == "__main__":
    app = KeypadMemoryTrapGUI()
    app.mainloop()
