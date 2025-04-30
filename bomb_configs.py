#################################
# CSC 102 Defuse the Bomb Project
# Configuration file
# Team: 
#################################

# constants
DEBUG = True        # debug mode?
RPi = True        # is this running on the RPi?
ANIMATE = True     # animate the LCD text?
SHOW_BUTTONS = True # show the Pause and Quit buttons on the main LCD GUI?
COUNTDOWN = 300      # the initial bomb countdown value (seconds)
NUM_STRIKES = 5      # the total strikes allowed before the bomb "explodes"
NUM_PHASES = 4       # the total number of initial active bomb phases

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
# 4 pins: 5V(+), GND(-), SDA, SCL
#         ----------7SEG---------
if (RPi):
    i2c = board.I2C()
    component_7seg = Seg7x4(i2c)
    # set the 7-segment display brightness (0 -> dimmest; 1 -> brightest)
    component_7seg.brightness = 0.5

# keypad
# 8 pins: 10, 9, 11, 5, 6, 13, 19, NA
#         -----------KEYPAD----------
if (RPi):
    # the pins
    keypad_cols = [DigitalInOut(i) for i in (board.D10, board.D9, board.D11)]
    keypad_rows = [DigitalInOut(i) for i in (board.D5, board.D6, board.D13, board.D19)]
    # the keys
    keypad_keys = ((1, 2, 3), (4, 5, 6), (7, 8, 9), ("*", 0, "#"))

    component_keypad = Matrix_Keypad(keypad_rows, keypad_cols, keypad_keys)

# jumper 
# 10 pins: 14, 15, 18, 23, 24, 3V3, 3V3, 3V3, 3V3, 3V3
#          -------JUMP1------  ---------JUMP2---------
# the jumper wire pins
if (RPi):
    # the pins
    component_wires = [DigitalInOut(i) for i in (board.D14, board.D15, board.D18, board.D23, board.D24)]
    for pin in component_wires:
        # pins are input and pulled down
        pin.direction = Direction.INPUT
        pin.pull = Pull.DOWN

# pushbutton
# 6 pins: 4, 17, 27, 22, 3V3, 3V3
#         -BUT1- -BUT2-  --BUT3--
if (RPi):
    # the state pin (state pin is input and pulled down)
    component_button_state = DigitalInOut(board.D4)
    component_button_state.direction = Direction.INPUT
    component_button_state.pull = Pull.DOWN
    # the RGB pins
    component_button_RGB = [DigitalInOut(i) for i in (board.D17, board.D27, board.D22)]
    for pin in component_button_RGB:
        # RGB pins are output
        pin.direction = Direction.OUTPUT
        pin.value = True

# toggle switches
# 3x3 pins: 12, 16, 20, 21, 3V3, 3V3, 3V3, 3V3, GND, GND, GND, GND
#           -TOG1-  -TOG2-  --TOG3--  --TOG4--  --TOG5--  --TOG6--
if (RPi):
    # the pins
    component_toggles = [DigitalInOut(i) for i in (board.D12, board.D16, board.D20, board.D21)]
    for pin in component_toggles:
        # pins are input and pulled down
        pin.direction = Direction.INPUT
        pin.pull = Pull.DOWN

###########
# functions
###########
# generates the bomb's serial number
#  it should be made up of alphaneumeric characters, and include 3/4/5 digits and at least 3 letters
#  the sum of the digits is in the range 2..15 to set the toggles target
#  the first three letters should be distinct and in the range 0..4 such that A=0, B=1, etc, to match the jumper wires
#  the last letter should be outside of the range
def genSerial():
    serial_digits = []

    # Generate a random toggle value between 2..15 to ensure 'usage' of at least 2 toggles
    toggle_value = randint(2, 15)
    print("toggle_value", toggle_value)

    # Randomly choose number of digits (3/4/5)
    num_digits = randint(3, 5)
    print("num_digits", num_digits)
    
    remaining = toggle_value

    for i in range(num_digits):
        digits_left = num_digits - i

        # Minimum sum needed for remaining digits (each digit at least 0)
        min_sum = 0
        # Maximum value for this digit
        max_digit = min(9, remaining - min_sum)

        # If it's the last digit, take exactly the remaining
        if digits_left == 1:
            d = remaining
        else:
            d = randint(0, max_digit)
        
        serial_digits.append(d)
        remaining -= d

    # set the letters (for jumper wires phase)
    jumper_indexes = [0] * 5
    while sum(jumper_indexes) < 3:
        jumper_indexes[randint(0, len(jumper_indexes) - 1)] = 1
    jumper_value = int("".join([str(n) for n in jumper_indexes]), 2)
    jumper_letters = [chr(i + 65) for i, n in enumerate(jumper_indexes) if n == 1]

    # form the serial number
    serial = [str(d) for d in serial_digits] + jumper_letters
    shuffle(serial)
    serial += [choice([chr(n) for n in range(70, 91)])]  # F-Z
    serial = "".join(serial)

    return serial, toggle_value, jumper_value

# generates the keypad combination from a keyword and rotation key
def genKeypadCombination():
    from random import choice

    # Choose a random hex value
    hex_values = ["1F", "3A", "2C", "FF", "B4", "A0", "C3", "4D"]
    hex_code = choice(hex_values)
    decimal_value = str(int(hex_code, 16))  # Convert to decimal as a string

    return hex_code, decimal_value

    keypad_target, keypad_answer = genKeypadCombination()


###############################
# generate the bomb's specifics
###############################
# generate the bomb's serial number (which also gets us the toggle and jumper target values)
#  serial: the bomb's serial number
#  toggles_target: the toggles phase defuse value
#  wires_target: the wires phase defuse value
serial, toggles_target, wires_target = genSerial()

# generate the combination for the keypad phase
#  keyword: the plaintext keyword for the lookup table
#  cipher_keyword: the encrypted keyword for the lookup table
#  rot: the key to decrypt the keyword
#  keypad_target: the keypad phase defuse value (combination)
#  passphrase: the target plaintext passphrase
keyword, cipher_keyword, rot, keypad_target, passphrase = genKeypadCombination()

# generate the color of the pushbutton (which determines how to defuse the phase)
button_color = choice(["R", "G", "B"])
# appropriately set the target (R is None)
button_target = None
# G is the first numeric digit in the serial number
if (button_color == "G"):
    button_target = [ n for n in serial if n.isdigit() ][0]
# B is the last numeric digit in the serial number
elif (button_color == "B"):
    button_target = [ n for n in serial if n.isdigit() ][-1]

if (DEBUG):
    print(f"Serial number: {serial}")
    print(f"Toggles target: {bin(toggles_target)[2:].zfill(4)}/{toggles_target}")
    print(f"Wires target: {bin(wires_target)[2:].zfill(5)}/{wires_target}")
    print(f"Keypad target: {keypad_target} (Hex) → {keypad_answer} (Decimal)")
    print(f"Button target: {button_target}")

# set the bomb's LCD bootup text
boot_text = (
    f"Booting...\n\x00\x00"
    f"*Kernel v3.1.4-159 loaded.\n"
    f"Initializing subsystems...\n\x00"
    f"*System model: 102BOMBv4.2\n"
    f"*Serial number: {serial}\n"
    f"Encrypting keypad...\n\x00"
    f"*Hex challenge: {keypad_target}\n"
    f"*{' '.join(ascii_uppercase)}\n"
    f"*{' '.join([str(n % 10) for n in range(26)])}\n"
    f"Rendering phases...\x00"
)

