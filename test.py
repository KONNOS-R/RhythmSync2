import os
from rich.align import Align
import sys
import termios
import tty
import signal

import player
import terminal_disp
import command_parser


#cli input
def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

def complete_path(text):
    if not text:
        return text

    def complete_fragment(fragment):
        fragment = fragment.strip()

        # Remove surrounding quotes
        if (fragment.startswith('"') and fragment.endswith('"')) or (
            fragment.startswith("'") and fragment.endswith("'")
        ):
            fragment = fragment[1:-1]

        fragment = os.path.expanduser(fragment)

        dir_name, prefix = os.path.split(fragment)
        if dir_name in ("", "."):
            dir_name = "."

        try:
            entries = list(os.scandir(dir_name))
        except OSError:
            return None

        exact = [e for e in entries if e.name == prefix]
        if len(exact) == 1:
            chosen = exact[0]
        else:
            matches = [e for e in entries if e.name.startswith(prefix)]
            if len(matches) != 1:
                return None
            chosen = matches[0]

        completed = os.path.join(dir_name, chosen.name)

        if chosen.is_dir():
            completed += os.sep

        return completed

    quote_hits = [
        (text.rfind(q), q)
        for q in ('"', "'")
        if text.count(q) % 2 == 1 and text.rfind(q) != -1
    ]

    if quote_hits:
        start, quote_char = max(quote_hits)
        fragment = text[start + 1:]
        completed = complete_fragment(fragment)
        if completed:
            return text[:start + 1] + completed + quote_char
        return text

    parts = text.split()
    for k in range(len(parts), 0, -1):
        base = " ".join(parts[:-k])
        fragment = " ".join(parts[-k:])

        completed = complete_fragment(fragment)
        if completed:
            if " " in completed:
                completed = f'"{completed}"'
            return (base + " " if base else "") + completed

    return text

def input_cli(prompt="> "):
    global history_index

    sys.stdout.write(prompt)
    sys.stdout.flush()

    buffer = ""
    history_index = len(history)

    while True:
        ch = getch()

         # CTRL+C
        if ch == "\x03":
            print()
            raise KeyboardInterrupt

        # CTRL+Z
        elif ch == "\x1a":
            print("\n[Suspended]")
            # restore terminal before suspending
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, termios.tcgetattr(sys.stdin))
            os.kill(os.getpid(), signal.SIGTSTP)

        # ENTER
        elif ch == "\r" or ch == "\n":
            print()
            if buffer.strip():
                history.append(buffer)
            return buffer

        # BACKSPACE
        elif ch == "\x7f":
            buffer = buffer[:-1]
            sys.stdout.write("\r" + prompt + buffer + " ")
            sys.stdout.write("\r" + prompt + buffer)
            sys.stdout.flush()

        # TAB
        elif ch == "\t":
            buffer = complete_path(buffer)
            sys.stdout.write("\r" + prompt + buffer)
            sys.stdout.flush()

        # ESC sequences
        elif ch == "\x1b":
            next1 = getch()
            next2 = getch()

            # UP arrow
            if next2 == "A":
                if history:
                    history_index = max(0, history_index - 1)
                    buffer = history[history_index]
                    sys.stdout.write("\r" + prompt + buffer + " " * 10)
                    sys.stdout.write("\r" + prompt + buffer)
                    sys.stdout.flush()

            # DOWN arrow
            elif next2 == "B":
                if history:
                    history_index = min(len(history) - 1, history_index + 1)
                    buffer = history[history_index]
                    sys.stdout.write("\r" + prompt + buffer + " " * 10)
                    sys.stdout.write("\r" + prompt + buffer)
                    sys.stdout.flush()

        else:
            buffer += ch
            sys.stdout.write(ch)
            sys.stdout.flush()
#/cliinput
        

#main program
def main():
    terminal_disp.clear_screen()

    global history
    global history_index
    history = []
    history_index = -1

    terminal_disp.logo()
    while True:
        try:
            command_parser.parse_command(input_cli("> "))

        except KeyboardInterrupt:
            print(f"Exitting...")
            break

        except Exception as e:
            terminal_disp.clear_screen()
            terminal_disp.logo()
            print(f"Error: {e}")
    

if __name__ == "__main__":
    main()
