#!/usr/bin/env python3
"""Fancy terminal Pomodoro timer for macOS."""

import argparse
import shutil
import subprocess
import sys
import time

DIGITS = {
    "0": ["█████", "█   █", "█   █", "█   █", "█████"],
    "1": ["  █  ", " ██  ", "  █  ", "  █  ", " ███ "],
    "2": ["█████", "    █", "█████", "█    ", "█████"],
    "3": ["█████", "    █", "█████", "    █", "█████"],
    "4": ["█   █", "█   █", "█████", "    █", "    █"],
    "5": ["█████", "█    ", "█████", "    █", "█████"],
    "6": ["█████", "█    ", "█████", "█   █", "█████"],
    "7": ["█████", "    █", "   █ ", "  █  ", "  █  "],
    "8": ["█████", "█   █", "█████", "█   █", "█████"],
    "9": ["█████", "█   █", "█████", "    █", "█████"],
    ":": ["   ", " █ ", "   ", " █ ", "   "],
}

RED, GREEN, CYAN, DIM, BOLD, RESET = (
    "\033[91m", "\033[92m", "\033[96m", "\033[2m", "\033[1m", "\033[0m"
)
CLEAR = "\033[2J\033[H"
HIDE_CURSOR, SHOW_CURSOR = "\033[?25l", "\033[?25h"

WORK_SOUND = "/System/Library/Sounds/Glass.aiff"
REST_SOUND = "/System/Library/Sounds/Hero.aiff"


def big_text(text):
    return ["  ".join(DIGITS[c][row] for c in text) for row in range(5)]


def center(line, width):
    return " " * max((width - len(line)) // 2, 0) + line


def draw(title, remaining, total, color, cycle):
    cols, rows = shutil.get_terminal_size()
    mins, secs = divmod(int(remaining), 60)
    big = big_text(f"{mins:02d}:{secs:02d}")

    bar_width = min(50, cols - 10)
    done = int(bar_width * (1 - remaining / total))
    bar = "█" * done + "░" * (bar_width - done)

    block_height = 5 + 6
    top = max((rows - block_height) // 2, 0)

    out = [CLEAR, "\n" * top]
    out.append(BOLD + color + center(title, cols) + RESET + "\n")
    out.append(DIM + center(f"Pomodoro #{cycle}", cols) + RESET + "\n\n")
    for line in big:
        out.append(color + center(line, cols) + RESET + "\n")
    out.append("\n" + color + center(bar, cols) + RESET + "\n")
    out.append(DIM + center("Ctrl+C to quit", cols) + RESET)
    sys.stdout.write("".join(out))
    sys.stdout.flush()


def countdown(title, seconds, color, cycle):
    end = time.monotonic() + seconds
    while True:
        remaining = end - time.monotonic()
        if remaining <= 0:
            break
        draw(title, remaining + 0.999, seconds, color, cycle)  # round up display
        time.sleep(min(remaining, 1 - (time.monotonic() % 1) or 1))
    draw(title, 0, seconds, color, cycle)


def alert(message, sound):
    subprocess.Popen(["afplay", sound])
    subprocess.Popen([
        "osascript", "-e",
        f'display notification "{message}" with title "Pomodoro" sound name ""',
    ])


def confirm(prompt, color):
    cols, _ = shutil.get_terminal_size()
    sys.stdout.write(SHOW_CURSOR + "\n\n" + BOLD + color
                     + center(prompt, cols) + RESET + "\n")
    answer = input(center("[Enter] start   [q] quit  > ", cols)).strip().lower()
    sys.stdout.write(HIDE_CURSOR)
    return answer != "q"


def main():
    parser = argparse.ArgumentParser(description="Terminal Pomodoro timer")
    parser.add_argument("-w", "--work", type=float, default=25, help="work minutes")
    parser.add_argument("-r", "--rest", type=float, default=5, help="rest minutes")
    args = parser.parse_args()

    work_s, rest_s = int(args.work * 60), int(args.rest * 60)
    cycle = 1

    sys.stdout.write(HIDE_CURSOR)
    try:
        if not confirm(f"Ready to work {args.work:g} min?", CYAN):
            return
        while True:
            countdown("🍅  WORK", work_s, RED, cycle)
            alert("Work finished! Time for a break.", WORK_SOUND)
            if not confirm("Work done! Start the break?", GREEN):
                break

            countdown("☕  REST", rest_s, GREEN, cycle)
            alert("Break is over! Back to work.", REST_SOUND)
            cycle += 1
            if not confirm("Break over! Start working?", RED):
                break
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(SHOW_CURSOR + RESET + "\n")
        print(f"Bye! Completed pomodoros: {cycle - 1}")


if __name__ == "__main__":
    main()
