import os
from rich.console import Console
console = Console()
from pathlib import Path
from random import shuffle
import shlex

import rhythmsync.player as player
import rhythmsync.metadata as metadata
import rhythmsync.converter as converter
import rhythmsync.terminal_disp as terminal_disp


#resets the cli
def reset_cli():
    terminal_disp.clear_screen()
    terminal_disp.logo()

#supported extensions
def is_audio_file(path: Path):
    return path.is_file() and path.suffix.lower() in (".mp3", ".flac", ".wav", ".ogg")

#returns audio files in dir
def get_audio_files(path: Path, recursive: bool = False):
    if recursive:
        files = path.rglob("*")
    else:
        files = path.iterdir()

    return sorted([f for f in files if is_audio_file(f)])

#single loop mode logic
def player_loop(file_path: Path, mode: str):
    repeat = True

    while repeat:
        result = player.run_player(str(file_path), mode)
        repeat = result[0]

#directory modes logic
def player_directory(files, mode, repeat_mode=False):
    if not files:
        print("No audio files found.")
        return

    repeat = True
    i = 1

    if repeat_mode:
        while repeat:
            for j in range(i-1, len(files)):
                repeat, i = player.run_player(files[j], f"directory {i} {len(files)}")
                if i < 1:
                    i = len(files)
                elif i > len(files):
                    i = 1
                break
    else:
        while i-1 < len(files) and i >= 1 and repeat:
            for j in range(i-1, len(files)):
                repeat, i = player.run_player(files[j], f"directory {i} {len(files)}")
                if i < 1:
                    i = 1
                break
        terminal_disp.clear_screen()
        terminal_disp.logo() 

# command parser
def parse_command(raw_command):
    if not raw_command.strip():
        return

    command = shlex.split(raw_command)
    cmd = command[0]
    args = command[1:]
    command_parts = len(command)

    # help command
    if cmd == "help" and command_parts == 1:
        terminal_disp.help_msg()

    # list command
    elif cmd == "ls":

        if command_parts == 1:
            console.print(f"[blue]{'   '.join(os.listdir())}", highlight=False)

        elif command_parts == 2:
            directory = Path(command[1]).expanduser().resolve()

            if directory.exists():
                console.print(f"[blue]{'   '.join(os.listdir(directory))}", highlight=False)

        else:
            print("Please enter valid parameters.")

    # change directory command
    elif cmd == "cd" and command_parts == 2:
        directory = Path(command[1]).expanduser().resolve()

        if directory.exists():
            os.chdir(directory)
        else:
            print("Please enter a valid file path.")

    # clear command
    elif cmd == "clear" and command_parts == 1:
        reset_cli()

    # play command
    elif cmd == "play":

        if command_parts == 2:
            file_path = Path(command[1]).expanduser().resolve()

            if file_path.exists():
                player_loop(file_path, "single")
                reset_cli()
            else:
                print("Please enter a valid file path.")

        elif command_parts == 3:

            par = command[1]
            file_path = Path(command[2]).expanduser().resolve()

            if not file_path.exists():
                print("Please enter a valid file path.")
                return

            # single repeat mode
            if par == "-r":
                player_loop(file_path, "repeat")
                reset_cli()

            # directory modes
            elif par in ("-d", "-dr", "-ds"):

                directory = file_path
                audio_files = get_audio_files(directory, recursive=False)

                if par == "-d":
                    audio_files.sort()
                    player_directory(audio_files, "directory")

                elif par == "-dr":
                    audio_files.sort()
                    player_directory(audio_files, "directory", repeat_mode=True)

                elif par == "-ds":
                    shuffle(audio_files)
                    player_directory(audio_files, "directory", repeat_mode=True)

                reset_cli()

            # recursive directory modes
            elif par in ("-D", "-Dr", "-Ds"):

                directory = file_path
                audio_files = get_audio_files(directory, recursive=True)

                if par == "-D":
                    audio_files.sort()
                    player_directory(audio_files, "directory")

                elif par == "-Dr":
                    audio_files.sort()
                    player_directory(audio_files, "directory", repeat_mode=True)

                elif par == "-Ds":
                    shuffle(audio_files)
                    player_directory(audio_files, "directory", repeat_mode=True)

                reset_cli()

        else:
            print("Please enter a valid file path and parameters.")

    # info command
    elif cmd == "info":

        if command_parts >= 2:
            file_path = Path(command[1]).expanduser().resolve()
            tags = tuple(command[2:]) or None

            if file_path.exists():
                console.print(
                    metadata.get_metadata(file_path, tags),
                    highlight=False
                )
            else:
                print("Please enter a valid file path.")

        else:
            print("Please enter a valid file path and parameters.")

    # convert command
    elif cmd == "convert" and command_parts == 3:

        input_path = Path(command[1]).expanduser().resolve()
        output_path = Path(command[2]).expanduser().resolve()
        output_dir = output_path.parent

        if input_path.exists() and output_dir.exists():
            converter.convert(input_path, output_path)
        else:
            print("Please enter valid file paths.")

    # invalid command           
    else:
        print("Invalid command! Enter 'help' to display command list.")
