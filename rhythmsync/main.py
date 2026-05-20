import os
import sys
import termios
import tty
import signal

import rhythmsync.terminal_disp as terminal_disp
import rhythmsync.command_parser as command_parser


#capture key strokes
def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

    return ch

#history redraw logic
def redraw_input(prompt, buffer):
    global last_rendered_lines

    cols = os.get_terminal_size().columns
    full = prompt + buffer

    lines = max(1, (len(full) // cols) + 1)

    for _ in range(last_rendered_lines - 1):
        sys.stdout.write("\x1b[F")

    for i in range(last_rendered_lines):
        sys.stdout.write("\r\x1b[2K")

        if i < last_rendered_lines - 1:
            sys.stdout.write("\x1b[E")

    for _ in range(last_rendered_lines - 1):
        sys.stdout.write("\x1b[F")

    sys.stdout.write("\r" + full)
    sys.stdout.flush()

    last_rendered_lines = lines

#path autocompletion
def complete_path(text):
    if not text:
        return text

    def escape_spaces(s: str) -> str:
        return s.replace(" ", r"\ ")

    def unescape_spaces(s: str) -> str:
        return s.replace(r"\ ", " ")

    def complete_fragment(fragment):
        fragment = fragment.strip()
        fragment = fragment.replace('"', '').replace("'", "")

        fragment = unescape_spaces(fragment)

        fragment = os.path.expanduser(fragment)

        dir_name, prefix = os.path.split(fragment)

        if not dir_name:
            dir_name = "."

        try:
            entries = list(os.scandir(dir_name))
        except OSError:
            return None

        matches = [e for e in entries if e.name.startswith(prefix)]

        if not matches:
            return None

        if len(matches) == 1:
            chosen_name = matches[0].name
        else:
            common = os.path.commonprefix([m.name for m in matches])
            if not common or common == prefix:
                return None
            chosen_name = common

        completed = os.path.join(dir_name, chosen_name)

        try:
            if os.path.isdir(completed):
                completed += os.sep
        except Exception:
            pass

        return escape_spaces(completed)

    parts = text.split()

    for k in range(len(parts), 0, -1):
        base = " ".join(parts[:-k])
        fragment = " ".join(parts[-k:])

        completed = complete_fragment(fragment)

        if completed:
            return (base + " " if base else "") + completed

    return text

#cli input
def input_cli(prompt="> "):
    global history_index

    buffer = ""
    history_index = len(history)
    redraw_input(prompt, buffer)

    while True:
        ch = getch()

        #CTRL+C
        if ch == "\x03":
            print()
            raise KeyboardInterrupt

        #CTRL+Z
        elif ch == "\x1a":
            print("\n[Suspended]")
            termios.tcsetattr(
                sys.stdin.fileno(),
                termios.TCSADRAIN,
                termios.tcgetattr(sys.stdin)
            )
            os.kill(os.getpid(), signal.SIGTSTP)

        #ENTER
        elif ch == "\r" or ch == "\n":
            print()
            if buffer.strip():
                history.append(buffer)
            return buffer

        #BACKSPACE
        elif ch == "\x7f":
            if buffer:
                buffer = buffer[:-1]
                redraw_input(prompt, buffer)

        #TAB
        elif ch == "\t":
            buffer = complete_path(buffer)
            redraw_input(prompt, buffer)

        #ESC Sequences
        elif ch == "\x1b":
            next1 = getch()
            next2 = getch()

            #UP Arrow
            if next2 == "A":
                if history:
                    history_index = max(0, history_index - 1)
                    buffer = history[history_index]
                    redraw_input(prompt, buffer)

            #DOWN Arrow
            elif next2 == "B":
                if history:
                    history_index = min(len(history) - 1, history_index + 1)
                    buffer = history[history_index]
                    redraw_input(prompt, buffer)

        else:
            buffer += ch
            redraw_input(prompt, buffer)

#main program
def main():
    terminal_disp.clear_screen()

    global history
    global history_index
    global last_rendered_lines

    history = []
    history_index = -1
    last_rendered_lines = 1

    terminal_disp.logo()

    while True:
        try:
            command_parser.parse_command(input_cli("> "))
        except KeyboardInterrupt:
            print("Exitting...")
            break
        except Exception as e:
            terminal_disp.clear_screen()
            terminal_disp.logo()
            print(f"Error: {e}")

#entry point
if __name__ == "__main__":
    main()