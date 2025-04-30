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
