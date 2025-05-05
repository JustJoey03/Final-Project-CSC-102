#Keypad Memory Trap Game: A memory puzzle where players press keys in the right order over several stages.

import random
from time import sleep

from bomb_configs import keypad_keys, NUM_PHASES, NUM_STRIKES, component_keypad

#Collapse the 2D keypad grid into a single list of symbols for easy use
def flatten_keypad(keys):
    """Flatten nested keypad_keys into a simple list of string symbols."""
    return [str(k) for row in keys for k in row]


def ordinal(n):
    """Return ordinal string (1st, 2nd, 3rd, etc.) for integer n."""
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}{['th','st','nd','rd','th','th','th','th','th','th'][n%10]}"


def play_game():
    symbols = flatten_keypad(keypad_keys)
    strikes = NUM_STRIKES
    sequences = []

    print("=== Keypad Memory Trap ===")
    # Generates and displays the memory sequences
    for round_num in range(1, NUM_PHASES + 1):
        seq = random.sample(symbols, 4)
        sequences.append(seq)
        print(f"Round {round_num}: {' '.join(seq)}")
        input("Press Enter to continue...")

    # Memory trap challenge phase
    for stage in range(1, NUM_PHASES + 1):
        # Pick a past round and a position within that round
        round_to_use = random.randint(1, stage)
        pos = random.randint(1, len(sequences[round_to_use - 1]))
        target = sequences[round_to_use - 1][pos - 1]
        rule = f"Press the {ordinal(pos)} symbol from round {round_to_use}"
        print(rule)
        choice = input("Your choice: ").strip()
        if choice == target:
            print("Correct!\n")
        else:
            strikes -= 1
            print(f"Incorrect! The correct symbol was {target}. Strikes left: {strikes}\n")
            if strikes <= 0:
                print("Game Over! You ran out of strikes.")
                return

    print("Congratulations! You completed the Keypad Memory Trap.")


if __name__ == "__main__":
    play_game()
