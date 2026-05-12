import os
from rich.console import Console
console = Console()
from rich.align import Align
from pathlib import Path
from random import shuffle
import shlex

import player

def parse_command(raw_command):
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
            player.logo()
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
            if command_parts == 2: #single
                file_path = str(Path(command[1]).expanduser().resolve())
                if os.path.exists(file_path):
                    player.run_player(file_path)
                    player.clear_screen()
                    player.logo()
                else:
                    print("Please enter a valid file path.")
            elif command_parts == 3:
                par = command[1]
                file_path = str(Path(command[2]).expanduser().resolve())
                if os.path.exists(file_path):
                    if par == "-r": #single repeat
                        repeat = True
                        while repeat:
                            repeat = player.run_player(file_path, "repeat")
                        player.clear_screen()
                        player.logo()
                    elif par == "-d": #dir
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
                        player.logo()
                    elif par == "-ds": #dir shuffle
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
                        player.logo()
                    elif par == "-dr": #dir repeat
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
                        player.logo()
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