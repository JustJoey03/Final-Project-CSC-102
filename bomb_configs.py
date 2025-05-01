#################################
# CSC 102 Defuse the Bomb Project
# Configuration file
# Team:
#################################

# constants
DEBUG = True        # debug mode?
RPi = True          # is this running on the RPi?
ANIMATE = False     # animate the LCD text?
SHOW_BUTTONS = True # show the Pause and Quit buttons on the main LCD GUI?
COUNTDOWN = 300     # the initial bomb countdown value (seconds)
NUM_STRIKES = 5     # the total strikes allowed before the bomb "explodes"
NUM_PHASES = 4      # the total number of initial active bomb phases

# imports
from random import randint, shuffle, choice
from string import ascii_uppercase
if (RPi):
    import board
    from adafruit_ht16k33.segments import Seg7x4
    from digitalio import DigitalInOut, Direction, Pull
    from adafruit_matrixkeypad import Matrix_Keypad

#################################
# setup the electronic components
#################################
# 7-segment display
if (RPi):
    i2c = board.I2C()
    component_7seg = Seg7x4(i2c)
    component_7seg.brightness = 0.5

# keypad
if (RPi):
    keypad_cols = [DigitalInOut(i) for i in (board.D10, board.D9, board.D11)]
    keypad_rows = [DigitalInOut(i) for i in (board.D5, board.D6, board.D13, board.D19)]
    keypad_keys = ((1, 2, 3), (4, 5, 6), (7, 8, 9), ("*", 0, "#"))
    component_keypad = Matrix_Keypad(keypad_rows, keypad_cols, keypad_keys)

# jumper wires
if (RPi):
    component_wires = [DigitalInOut(i) for i in (board.D14, board.D15, board.D18, board.D23, board.D24)]
    for pin in component_wires:
        pin.direction = Direction.INPUT
        pin.pull = Pull.DOWN

# pushbutton
if (RPi):
    component_button_state = DigitalInOut(board.D4)
    component_button_state.direction = Direction.INPUT
    component_button_state.pull = Pull.DOWN
    component_button_RGB = [DigitalInOut(i) for i in (board.D17, board.D27, board.D22)]
    for pin in component_button_RGB:
        pin.direction = Direction.OUTPUT
        pin.value = True

# toggle switches
if (RPi):
    component_toggles = [DigitalInOut(i) for i in (board.D12, board.D16, board.D20, board.D21)]
    for pin in component_toggles:
        pin.direction = Direction.INPUT
        pin.pull = Pull.DOWN

###########
# functions
###########

# generate serial with jumper & toggle logic
def genSerial():
    serial_digits = []
    toggle_value = randint(2, 15)
    print("toggle_value", toggle_value)

    num_digits = randint(3, 5)
    print("num_digits", num_digits)
    remaining = toggle_value

    for i in range(num_digits):
        digits_left = num_digits - i
        min_sum = 0
        max_digit = min(9, remaining - min_sum)
        d = remaining if digits_left == 1 else randint(0, max_digit)
        serial_digits.append(d)
        remaining -= d

    jumper_indexes = [0] * 5
    while sum(jumper_indexes) < 3:
        jumper_indexes[randint(0, len(jumper_indexes) - 1)] = 1
    jumper_value = int("".join([str(n) for n in jumper_indexes]), 2)
    jumper_letters = [chr(i + 65) for i, n in enumerate(jumper_indexes) if n == 1]

    serial = [str(d) for d in serial_digits] + jumper_letters
    shuffle(serial)
    serial += [choice([chr(n) for n in range(70, 91)])]  # F-Z
    serial = "".join(serial)

    return serial, toggle_value, jumper_value

# keypad combination generator
def genKeypadCombination():
    from random import choice
    hex_values = ["1F", "3A", "2C", "FF", "B4", "A0", "C3", "4D"]
    hex_code = choice(hex_values)
    decimal_value = str(int(hex_code, 16))
    return hex_code, decimal_value

# generate Two's Complement wires target
def generate_twos_complement_target():
    value = randint(-16, 15)
    if value < 0:
        value = (1 << 5) + value
    return value

###############################
# generate the bomb's specifics
###############################

# Get serial and toggle target (ignore jumper-based wire target)
serial, toggles_target, _ = genSerial()

# Use Two's Complement for wires_target
wires_target = generate_twos_complement_target()

# generate keypad challenge
keypad_target, keypad_answer = genKeypadCombination()

# pushbutton color logic
button_color = choice(["R", "G", "B"])
button_target = None
if (button_color == "G"):
    button_target = [ n for n in serial if n.isdigit() ][0]
elif (button_color == "B"):
    button_target = [ n for n in serial if n.isdigit() ][-1]

if (DEBUG):
    signed_value = wires_target if wires_target < 16 else wires_target - 32
    print(f"Serial number: {serial}")
    print(f"Toggles target: {bin(toggles_target)[2:].zfill(4)}/{toggles_target}")
    print(f"Wires target (Two's Complement): {bin(wires_target)[2:].zfill(5)} (= {signed_value})")
    print(f"Keypad target: {keypad_target} (Hex) → {keypad_answer} (Decimal)")
    print(f"Button target: {button_target}")

# LCD boot text
boot_text = (
    f"Booting...\n\x00\x00"
    f"*Kernel v3.1.4-159 loaded.\n"
    f"Initializing subsystems...\n\x00"
    f"*System model: 102BOMBv4.2\n"
    f"*Serial number: {serial}\n"
    f"Encrypting keypad...\n\x00"
    f"*Hex challenge: {keypad_target}\n"
    #f"*{' '.join(ascii_uppercase)}\n"
    #f"*{' '.join([str(n % 10) for n in range(26)])}\n"
    f"Rendering phases...\x00"
)