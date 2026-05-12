import os
from rich.console import Console
console = Console()
from rich.align import Align
from pathlib import Path
from random import shuffle
import shlex
import sys
import termios
import tty
import signal

import player



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
    player.clear_screen()

    global history
    global history_index
    history = []
    history_index = -1

    rhythmsync_ascii ='''[bold][#5900ab]
[#5900ab] _____  _           _   _                [#00d0ff]_____                  
[#5900ab]|  __ \\| |         | | | |              [#00d0ff]/ ____|                 
[#5900ab]| |__) | |__  _   _| |_| |__  _ __ ___ [#00d0ff]| (___  _   _ _ __   ___ 
[#5900ab]|  _  /| '_ \\| | | | __| '_ \\| '_ ` _ \\ [#00d0ff]\\___ \\| | | | '_ \\ / __|
[#5900ab]| | \\ \\| | | | |_| | |_| | | | | | | | |[#00d0ff]____) | |_| | | | | (__ 
[#5900ab]|_|  \\_\\_| |_|\\__, |\\__|_| |_|_| |_| |_|[#00d0ff]_____/ \__, |_| |_|\\___|
[#5900ab]               __/ |                         [#00d0ff]   __/ |           
[#5900ab]              |___/                           [#00d0ff] |___/            
'''
    console.print(Align.center(rhythmsync_ascii))
    while True:
        try:
            raw_command = input_cli("> ")
            
            if raw_command.strip():
                command = shlex.split(raw_command)
                command_parts = len(command)
            
                #help command
                if command[0] == "help" and command_parts == 1:
                    console.print('''command list:
        [green]help[/green] - Lists all available commands.
        [green]clear[/green] - Clears the terminal.
        [green]play[/green] [cyan]{par} {path}[/cyan] - Plays the audio file located at the specified [cyan]{path}[/cyan].
            If [cyan]{par}[/cyan] is "-r", the audio file plays in repeat until stopped.
            If [cyan]{par}[/cyan] is "-d" and [cyan]{path}[/cyan] is a directory, the audio files of given directory play in alphabetical order.
            If [cyan]{par}[/cyan] is "-dr" and [cyan]{path}[/cyan] is a directory, the audio files of given directory play in alphabetical order and loop around until stopped.
            If [cyan]{par}[/cyan] is "-ds" and [cyan]{path}[/cyan] is a directory, the audio files of given directory play in shuffled order.
            If [cyan]{par}[/cyan] is omitted, the audio file plays once.
        [green]info[/green] [cyan]{path} {tags}[/cyan] - Displays metadata for the file at [cyan]{path}[/cyan].
            If [cyan]{tags}[/cyan] is provided (separate them with space for multiple tags), shows only those specific tags and their respective values.
            If [cyan]{tags}[/cyan] is omitted, shows all available tags and their respective values.
        '''
                                    )
                
                #clear command
                elif command[0] == "clear" and command_parts == 1:
                    player.clear_screen()
                    console.print(Align.center(rhythmsync_ascii))

                elif command[0] == "ls" and command_parts == 1:
                    print(os.listdir())

                elif command[0] == "cd" and command_parts == 2:
                    directory = str(Path(command[1]).expanduser().resolve())
                    if os.path.exists(directory):
                        os.chdir(directory)
                    else:
                        print("Please enter a valid file path.")
                
                #play command
                elif command[0] == "play":
                    if command_parts == 2:
                        file_path = str(Path(command[1]).expanduser().resolve())
                        if os.path.exists(file_path):
                            player.run_player(file_path)
                            player.clear_screen()
                            console.print(Align.center(rhythmsync_ascii))
                        else:
                            print("Please enter a valid file path.")
                    elif command_parts == 3:
                        par = command[1]
                        file_path = str(Path(command[2]).expanduser().resolve())
                        if os.path.exists(file_path):
                            if par == "-r":
                                repeat = True
                                while repeat:
                                    repeat = player.run_player(file_path, "repeat")
                                player.clear_screen()
                                console.print(Align.center(rhythmsync_ascii))
                            elif par == "-d":
                                extensions = (".mp3", ".flac", ".wav", ".ogg")
                                audio_files = [
                                f for f in Path(file_path).iterdir()
                                if f.suffix.lower() in extensions
                                ]
                                audio_files.sort()
                                repeat = True
                                i = 0
                                for file in audio_files:
                                    i += 1
                                    repeat = player.run_player(file, f"directory {i} {len(audio_files)}")
                                    if not repeat:
                                        break
                                player.clear_screen()
                                console.print(Align.center(rhythmsync_ascii))
                            elif par == "-ds":
                                extensions = (".mp3", ".flac", ".wav", ".ogg")
                                audio_files = [
                                f for f in Path(file_path).iterdir()
                                if f.suffix.lower() in extensions
                                ]
                                shuffle(audio_files)
                                repeat = True
                                i = 0
                                for file in audio_files:
                                    i += 1
                                    repeat = player.run_player(file, f"directory-shuffle {i} {len(audio_files)}")
                                    if not repeat:
                                        break
                                player.clear_screen()
                                console.print(Align.center(rhythmsync_ascii))
                            elif par == "-dr":
                                extensions = (".mp3", ".flac", ".wav", ".ogg")
                                audio_files = [
                                f for f in Path(file_path).iterdir()
                                if f.suffix.lower() in extensions
                                ]
                                audio_files.sort()
                                repeat = True
                                while repeat:
                                    i = 0
                                    for file in audio_files:
                                        i += 1
                                        repeat = player.run_player(file, f"directory-repeat {i} {len(audio_files)}")
                                        if repeat == False:
                                            break
                                player.clear_screen()
                                console.print(Align.center(rhythmsync_ascii))
                        else:
                            print("Please enter a valid file path.") 
                    else:
                        print("Please enter a valid file path and parameters.")
                
                #info command
                elif command[0] == "info":
                    if command_parts >= 2:
                       file_path = Path(command[1]).expanduser().resolve()
                       par = tuple(command[2:]) or None
                       if os.path.exists(file_path):
                           console.print(player.get_metadata(file_path, par), highlight=False)
                       else:
                           print("Please enter a valid file path.")
                    else:
                        print("Please enter a valid file path and parameters.")

                #invalid command
                else:
                    print("Invalid command! Enter 'help' to display command list.")
    
        except KeyboardInterrupt:
            print(f"Exitting...")
            break
        except Exception as e:
            player.clear_screen()
            console.print(Align.center(rhythmsync_ascii))
            print(f"Error: {e}")
    

if __name__ == "__main__":
    main()
