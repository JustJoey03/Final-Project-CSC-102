#################################
# CSC 102 Defuse the Bomb Project
# Main program
# Team:
#################################

# import the configs
from bomb_configs import *
# import the phases
from bomb_phases import *

###########
# functions
###########
# generates the bootup sequence on the LCD
def bootup(n=0):
    # if we're not animating (or we're at the end of the bootup text)
    if (not ANIMATE or n == len(boot_text)):
        # if we're not animating, render the entire text at once (and don't process \x00)
        if (not ANIMATE):
            gui._lscroll["text"] = boot_text.replace("\x00", "")
        # configure the remaining GUI widgets
        gui.setup()
        # setup the phase threads, execute them, and check their statuses
        if (RPi):
            setup_phases()
            check_phases()
    else:
        # add the next character (but don't render \x00 since it specifies a longer pause)
        if (boot_text[n] != "\x00"):
            gui._lscroll["text"] += boot_text[n]
        # scroll the next character after a slight delay (\x00 is a longer delay)
        gui.after(25 if boot_text[n] != "\x00" else 750, bootup, n + 1)

# sets up the phase threads
def setup_phases():
    global timer, keypad, wires, button, toggles

    # setup the timer thread
    timer = Timer(component_7seg, COUNTDOWN)
    gui.setTimer(timer)

    # setup the keypad thread
    keypad = Keypad(component_keypad, keypad_answer)

    # setup the jumper wires thread
    wires = Wires(component_wires, wires_target)

    # setup the pushbutton thread
    button = Button(component_button_state, component_button_RGB, button_target, button_color, timer)
    gui.setButton(button)

    # setup the toggle switches thread
    toggles = Toggles(component_toggles, toggles_target)

    # start the phase threads
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
        gui._lkeypad["text"] = f"Convert HEX {keypad_target} → Decimal: {keypad}"
        if (keypad._defused):
            keypad._running = False
            active_phases -= 1
        elif (keypad._failed):
            strike()
            keypad._failed = False
            keypad._value = ""

    # check the wires
    if (wires._running):
        gui._lwires["text"] = f"Wires: {wires}"
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

    # update strikes left
    gui._lstrikes["text"] = f"Strikes left: {strikes_left}"
    if (strikes_left == 0):
        turn_off()
        gui.after(1000, gui.conclusion, False)
        return

    # all phases defused
    if (active_phases == 0):
        turn_off()
        gui.after(100, gui.conclusion, True)
        return

    # repeat check
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

gui.after(1000, bootup)
window.mainloop()
