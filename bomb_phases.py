#################################
# CSC 102 Defuse the Bomb Project
# GUI and Phase class definitions
# Team: 
#################################

# Import the configs (to get NUM_STRIKES)
from bomb_configs import NUM_STRIKES  # Import NUM_STRIKES from bomb_configs.py

# import the configs
from bomb_configs import *
# other imports
from tkinter import *
import tkinter
from threading import Thread
from time import sleep
import os
import sys
import pygame  # Additional import for handling audio

#########
# classes
#########
# the LCD display GUI
class Lcd(Frame):
    def __init__(self, window):
        
        super().__init__(window, bg='black')
        #self.bg_photo = PhotoImage(file="panel_notbombmonitor.png")
        #self.bg_label = Label(self, image=self.bg_photo)
        #self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        window.attributes("-fullscreen", True) # Fullscreen
        #self.pack(fill=BOTH, expand=TRUE)
        #self.root = window
        #self.root.geometry('1024x576')  
        #self.root.configure(cursor='none')
        # Load background panel (bomb) using Tkinter
        #self.bg_photo = PhotoImage(file="panel_notbombmonitor.png")
        #self.canvas = Canvas(self.root,
        #                     width=self.bg_photo.width(),
        #                     height=self.bg_photo.height())
        #self.canvas.pack(fill=BOTH, expand=TRUE)
        #self.canvas.create_image(0, 0, anchor=NW, image=self.bg_photo) # Bomb picture
        #self.boot_text = self.canvas.create_text(50, 50, anchor=NW, text="Text example here", font=("Courier New", 20), fill="white", justify=LEFT) # Text just for placement preview

        # we need to know about the timer (7-segment display) to be able to pause/unpause it
        self._timer = None
        # we need to know about the pushbutton to turn off its LED when the program exits
        self._button = None
        # setup the initial "boot" GUI
        self.setupBoot()

    # sets up the LCD "boot" GUI
    def setupBoot(self):
        # set column weights
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        # the scrolling informative "boot" text
        self._lscroll = Label(self, bg="black", fg="white", font=("Courier New", 14), text="", justify=LEFT)
        self._lscroll.grid(row=0, column=0, columnspan=3, sticky=W)
        self.pack(fill=BOTH, expand=True)

    # sets up the LCD GUI
    def setup(self):
        # the timer
        self._ltimer = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Time left: ")
        self._ltimer.grid(row=1, column=0, columnspan=3, sticky=W)
        # the keypad passphrase
        self._lkeypad = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Keypad phase: ")
        self._lkeypad.grid(row=2, column=0, columnspan=3, sticky=W)
        # the jumper wires status
        self._lwires = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Wires phase: ")
        self._lwires.grid(row=3, column=0, columnspan=3, sticky=W)
        # the pushbutton status
        self._lbutton = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Button phase: ")
        self._lbutton.grid(row=4, column=0, columnspan=3, sticky=W)
        # the toggle switches status
        self._ltoggles = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Toggles phase: ")
        self._ltoggles.grid(row=5, column=0, columnspan=2, sticky=W)
        # the strikes left
        self._lstrikes = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Strikes left: ")
        self._lstrikes.grid(row=5, column=2, sticky=W)
        if (SHOW_BUTTONS):
            # the pause button (pauses the timer)
            self._bpause = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Pause", anchor=CENTER, command=self.pause)
            self._bpause.grid(row=6, column=0, pady=40)
            # the quit button
            self._bquit = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Quit", anchor=CENTER, command=self.quit)
            self._bquit.grid(row=6, column=2, pady=40)

    # lets us pause/unpause the timer (7-segment display)
    def setTimer(self, timer):
        self._timer = timer

    # lets us turn off the pushbutton's RGB LED
    def setButton(self, button):
        self._button = button

    # pauses the timer
    def pause(self):
        if (RPi):
            self._timer.pause()

    # setup the conclusion GUI (explosion/defusion)
    def conclusion(self, success=False):
        # destroy/clear widgets that are no longer needed
        self._lscroll["text"] = ""
        self._ltimer.destroy()
        self._lkeypad.destroy()
        self._lwires.destroy()
        self._lbutton.destroy()
        self._ltoggles.destroy()
        self._lstrikes.destroy()
        if (SHOW_BUTTONS):
            self._bpause.destroy()
            self._bquit.destroy()

        # reconfigure the GUI
        # the retry button
        self._bretry = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Retry", anchor=CENTER, command=self.retry)
        self._bretry.grid(row=1, column=0, pady=40)
        # the quit button
        self._bquit = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Quit", anchor=CENTER, command=self.quit)
        self._bquit.grid(row=1, column=2, pady=40)
        
        if success:
            self.win_applause.play()  # Play applause when successfully defused
        else:
            self.lose_explosion.play()  # Play explosion sound when failed

    # re-attempts the bomb (after an explosion or a successful defusion)
    def retry(self):
        # re-launch the program (and exit this one)
        os.execv(sys.executable, ["python3"] + [sys.argv[0]])
        exit(0)

    # quits the GUI, resetting some components
    def quit(self):
        if (RPi):
            # turn off the 7-segment display
            self._timer._running = False
            self._timer._component.blink_rate = 0
            self._timer._component.fill(0)
            # turn off the pushbutton's LED
            for pin in self._button._rgb:
                pin.value = True
        # exit the application
        exit(0)

# template (superclass) for various bomb components/phases
class PhaseThread(Thread):
    def __init__(self, name, component=None, target=None):
        super().__init__(name=name, daemon=True)
        # phases have an electronic component (which usually represents the GPIO pins)
        self._component = component
        # phases have a target value (e.g., a specific combination on the keypad, the proper jumper wires to "cut", etc)
        self._target = target
        # phases can be successfully defused
        self._defused = False
        # phases can be failed (which result in a strike)
        self._failed = False
        # phases have a value (e.g., a pushbutton can be True/Pressed or False/Released, several jumper wires can be "cut"/False, etc)
        self._value = None
        # phase threads are either running or not
        self._running = False

# the timer phase
class Timer(PhaseThread):
    def __init__(self, component, initial_value, name="Timer"):
        super().__init__(name, component)
        # the default value is the specified initial value
        self._value = initial_value
        # is the timer paused?
        self._paused = False
        # initialize the timer's minutes/seconds representation
        self._min = ""
        self._sec = ""
        # by default, each tick is 1 second
        self._interval = 1
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        # Load audio files
        self.timer_sound = pygame.mixer.Sound("timer.mp3")
        self.final_countdown_alarm = pygame.mixer.Sound("final_countdown_alarm.mp3")
        self.lose_explosion = pygame.mixer.Sound("lose_explosion.mp3")
        self.win_applause = pygame.mixer.Sound("win_applause.mp3")
        
        # Temporary flag to signal when to stop the timer sound
        self.timer_sound_playing = False

    # runs the thread
    def run(self):
        self._running = True
        self.timer_sound.play(loops=-1)  # Start playing timer sound on loop
        
        while (self._running):
            if (not self._paused):
                # update the timer and display its value on the 7-segment display
                self._update()
                self._component.print(str(self))
                
                # Check for countdown audio effects
                if self._value == 10 and not self.timer_sound_playing:
                    self.final_countdown_alarm.play()  # Play final countdown alarm
                    self.timer_sound_playing = True  # Prevent replaying the countdown alarm
                    
                
                # the timer has expired -> phase failed (explode)
                if (self._value == 0):
                    self.timer_sound.stop()  # Stop the timer sound
                    self.lose_explosion.play()  # Play explosion sound
                    self._running = False
                    # Check for game over (e.g., player lost)
                    if NUM_STRIKES == 0:
                        self.lose_explosion.play()  # Play lose sound
                    sleep(1)

                    # wait 1s (default) and continue
                sleep(self._interval)
                self._value -= 1
            else:
                sleep(0.1)

    # updates the timer (only internally called)
    def _update(self):
        self._min = f"{self._value // 60}".zfill(2)
        self._sec = f"{self._value % 60}".zfill(2)

    # pauses and unpauses the timer
    def pause(self):
        # toggle the paused state
        self._paused = not self._paused
        # blink the 7-segment display when paused
        self._component.blink_rate = (2 if self._paused else 0)
        if self._paused:
            self.timer_sound.stop()  # Stop playing sound when paused
        else:
            if self._value > 0:  # Only restart if there's time left
                self.timer_sound.play(loops=-1)

    # returns the timer as a string (mm:ss)
    def __str__(self):
        return f"{self._min}:{self._sec}"

# the keypad phase
class Keypad(PhaseThread):
    def __init__(self, component, target, name="Keypad"):
        super().__init__(name, component, target)
        # the default value is an empty string
        self._value = ""

    # runs the thread
    def run(self):
        self._running = True
        while (self._running):
            # process keys when keypad key(s) are pressed
            if (self._component.pressed_keys):
                # debounce
                while (self._component.pressed_keys):
                    try:
                        # just grab the first key pressed if more than one were pressed
                        key = self._component.pressed_keys[0]
                    except:
                        key = ""
                    sleep(0.1)
                # log the key
                self._value += str(key)
                # the combination is correct -> phase defused
                if (self._value == self._target):
                    self._defused = True
                # the combination is incorrect -> phase failed (strike)
                elif (self._value != self._target[0:len(self._value)]):
                    self._failed = True
            sleep(0.1)

    # returns the keypad combination as a string
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return self._value

# the jumper wires phase
class Wires(PhaseThread):
    """
    PhaseThread that reads five GPIO pins (your jumper wires),
    builds a bit-string from them, and defuses when that integer
    matches the configured wires_target.
    """
    def __init__(self, component, target, name="Wires"):
        super().__init__(name, component, target)
        # will hold e.g. "10110"
        self._value = ""

    def run(self):
        self._running = True
        # continuously poll the five pins
        while self._running:
            # build a list of '0' or '1' strings from each pin.value
            bits = [str(int(pin.value)) for pin in self._component]
            self._value = "".join(bits)               # e.g. "10011"
            # compare the binary→int to the target
            if int(self._value, 2) == self._target:
                self._defused = True
                self._running = False
            sleep(0.1)

    def __str__(self):
        # once defused, show DEFUSED
        if self._defused:
            return "DEFUSED"
        # otherwise show the live bits and their decimal
        return f"{self._value} (= {int(self._value, 2)})"

# the pushbutton phase
class Button(PhaseThread):
    def __init__(self, component_state, component_rgb, target, color, timer, name="Button"):
        super().__init__(name, component_state, target)
        # the default value is False/Released
        self._value = False
        # has the pushbutton been pressed?
        self._pressed = False
        # we need the pushbutton's RGB pins to set its color
        self._rgb = component_rgb
        # the pushbutton's randomly selected LED color
        self._color = color
        # we need to know about the timer (7-segment display) to be able to determine correct pushbutton releases in some cases
        self._timer = timer

    # runs the thread
    def run(self):
        self._running = True
        # set the RGB LED color
        self._rgb[0].value = False if self._color == "R" else True
        self._rgb[1].value = False if self._color == "G" else True
        self._rgb[2].value = False if self._color == "B" else True
        while (self._running):
            # get the pushbutton's state
            self._value = self._component.value
            # it is pressed
            if (self._value):
                # note it
                self._pressed = True
            # it is released
            else:
                # was it previously pressed?
                if (self._pressed):
                    # check the release parameters
                    # for R, nothing else is needed
                    # for G or B, a specific digit must be in the timer (sec) when released
                    if (not self._target or self._target in self._timer._sec):
                        self._defused = True
                    else:
                        self._failed = True
                    # note that the pushbutton was released
                    self._pressed = False
            sleep(0.1)

    # returns the pushbutton's state as a string
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return str("Pressed" if self._value else "Released")

# the toggle switches phase
class Toggles(PhaseThread):
    def __init__(self, component, target, name="Toggles"):
        super().__init__(name, component, target)
        self._value = 0  # Initialize the toggle state

    # runs the thread
    def run(self):
        self._running = True
        while self._running:
            # Check the state of the toggle switches
            num_toggles = len(self._component) # Needed for making sure binary digits are in correct order
            self._value = sum(1 << (num_toggles - 1 - i) for i, pin in enumerate(self._component) if pin.value) # Calculate the binary value

            # Check if the toggle value matches the target
            if self._value == self._target:
                self._defused = True
                self._running = False
            sleep(0.1)

    # returns the toggle switches state as a string
    def __str__(self):
        if self._defused:
            return "DEFUSED"
        else:
            return f"{bin(self._value)[2:].zfill(4)}" # Show the current binary value