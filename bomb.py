#################################
# CSC 102 Defuse the Bomb Project
# Main program
# Team:
#################################

from tkinter import Tk, Button, messagebox
from tkinter.ttk import Progressbar
# import the configs
from bomb_configs import *
# import the phases
from bomb_phases import *

###########
# functions
###########

# Visual Effects: Progress Bar for Timer
def create_timer_progress():
    progress = Progressbar(window, orient="horizontal", length=200, mode="determinate")
    progress.grid(row=1, column=0)

    def update_progress():
        progress["value"] = (timer.time_left / COUNTDOWN) * 100
        window.after(1000, update_progress)

    window.after(1000, update_progress)

# Update timer display and color
def update_timer():
    if timer._running:
        if timer.time_left <= 10:
            gui._ltimer["fg"] = "red"  # Change color when time is running low
        else:
            gui._ltimer["fg"] = "black"  # Reset color
        gui._ltimer["text"] = f"Time left: {timer}"

# Exit/Quit Confirmation
def confirm_exit():
    if messagebox.askyesno("Exit", "Are you sure you want to quit?"):
        window.quit()

# Game Over Animation (Bomb Exploded)
def game_over():
    gui._lscroll["text"] = "Game Over! The bomb exploded!"
    window.config(bg="red")  # Change background color to red

# Defuse Success Animation
def game_won():
    gui._lscroll["text"] = "Congratulations! You defused the bomb!"
    window.config(bg="green")  # Change background color to green

# generates the bootup sequence on the LCD
def bootup(n=0):
    if (not ANIMATE or n == len(boot_text)):
        if (not ANIMATE):
            gui._lscroll["text"] = boot_text.replace("\x00", "")
        gui.setup()
        if (RPi):
            setup_phases()
            check_phases()
    else:
        if (boot_text[n] != "\x00"):
            gui._lscroll["text"] += boot_text[n]
        gui.after(25 if boot_text[n] != "\x00" else 750, bootup, n + 1)

# sets up the phase threads
def setup_phases():
    global timer, keypad, wires, button, toggles

    timer = Timer(component_7seg, COUNTDOWN)
    gui.setTimer(timer)

    keypad = Keypad(component_keypad, keypad_answer)
    wires = Wires(component_wires, wires_target)
    button = Button(component_button_state, component_button_RGB, button_target, button_color, timer)
    gui.setButton(button)
    toggles = Toggles(component_toggles, toggles_target)

    timer.start()
    keypad.start()
    wires.start()
    button.start()
    toggles.start()

# checks the phase threads
def check_phases():
    global active_phases

    # check the timer
    if (timer._running):
        gui._ltimer["text"] = f"Time left: {timer}"
    else:
        turn_off()
        gui.after(100, gui.conclusion, False)
        return

    # check the keypad
    if (keypad._running):
        gui._lkeypad["text"] = f"Keypad: {keypad_target} → {keypad}"
        if (keypad._defused):
            keypad._running = False
            active_phases -= 1
        elif (keypad._failed):
            strike()
            keypad._failed = False
            keypad._value = ""

    # check the wires
    if (wires._running):
        signed_target = wires._target if wires._target < 16 else wires._target - 32
        #gui._lwires["text"] = f"Wires: {wires} | Target: {bin(wires._target)[2:].zfill(5)} (= {signed_target})"
        gui._lwires["text"] = f"Wires: {wires} | Target: {signed_target}"
        if (wires._defused):
            wires._running = False
            active_phases -= 1
        elif (wires._failed):
            strike()
            wires._failed = False

    # check the button
    if (button._running):
        gui._lbutton["text"] = f"Button: {button}"
        if (button._defused):
            button._running = False
            active_phases -= 1
        elif (button._failed):
            strike()
            button._failed = False

    # check the toggles
    if (toggles._running):
        gui._ltoggles["text"] = f"Toggles: {toggles}"
        if (toggles._defused):
            toggles._running = False
            active_phases -= 1
            gui._ltoggles["text"] = "Toggles: DEFUSED"
    elif toggles._defused:
        gui._ltoggles["text"] = "Toggles: DEFUSED"
    elif (toggles._failed):
        strike()
        toggles._failed = False

    gui._lstrikes["text"] = f"Strikes left: {strikes_left}"
    if (strikes_left == 0):
        turn_off()
        gui.after(1000, gui.conclusion, False)
        return

    if (active_phases == 0):
        turn_off()
        gui.after(100, gui.conclusion, True)
        return

    gui.after(100, check_phases)

# handles a strike
def strike():
    global strikes_left
    strikes_left -= 1

# turns off the bomb
def turn_off():
    timer._running = False
    keypad._running = False
    wires._running = False
    button._running = False
    toggles._running = False

    component_7seg.blink_rate = 0
    component_7seg.fill(0)
    for pin in button._rgb:
        pin.value = True

######
# MAIN
######

window = Tk()
window.title("Bomb Defusal")
gui = Lcd(window)

strikes_left = NUM_STRIKES
active_phases = NUM_PHASES

# Call the function to create the timer progress bar
create_timer_progress()

gui.after(1000, bootup)
window.mainloop()
