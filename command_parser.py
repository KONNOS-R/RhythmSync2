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
            console.print('''COMMAND LIST:
[green]help[/green]  lists all available commands

[green]ls[/green]  lists all files and directories in the current working directory
[green]ls[/green] [cyan]{dir}[/cyan]  lists all files and directories in given directory
                                          
[green]cd[/green] [cyan]{dir}[/cyan]  changes current working directory to given directory

[green]clear[/green]  clears the terminal
                   
[green]play[/green] [cyan]{path}[/cyan]  the given audio file plays once
[green]play[/green] [cyan]{option} {path}[/cyan]
    [cyan]-r[/cyan]   the given audio file plays in repeat until stopped
[green]play[/green] [cyan]{option} {dir}[/cyan]
    [cyan]-d[/cyan]   the audio files of given directory play in alphabetical order
    [cyan]-dr[/cyan]  the audio files of given directory play in alphabetical order and loop around until stopped
    [cyan]-ds[/cyan]  the audio files of given directory play in shuffled order
   
[green]info[/green] [cyan]{path}[/cyan]  shows all available tags and their respective values for the given audio file.
[green]info[/green] [cyan]{path} {tags}[/cyan]  hows only the provided tags (separate tags with space for multiple ones) and their respective values
'''
                            )
        
        #list command
        elif command[0] == "ls":
            if command_parts == 1:
                console.print(f"[blue]{"   ".join(os.listdir())}", highlight=False)
            elif command_parts == 2:
                directory = str(Path(command[1]).expanduser().resolve())
                if os.path.exists(directory):
                    console.print(f"[blue]{"   ".join(os.listdir(directory))}", highlight=False)
            else:
                print("Please enter valid parameters.")

        #change dir command
        elif command[0] == "cd" and command_parts == 2:
            directory = str(Path(command[1]).expanduser().resolve())
            if os.path.exists(directory):
                os.chdir(directory)
            else:
                print("Please enter a valid file path.")

        #clear command
        elif command[0] == "clear" and command_parts == 1:
            player.clear_screen()
            player.logo()
        
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
                        if audio_files:
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
                        else:
                            print("No audio files found.")
                    elif par == "-ds": #dir shuffle
                        extensions = (".mp3", ".flac", ".wav", ".ogg")
                        audio_files = [
                        f for f in Path(file_path).iterdir()
                        if f.suffix.lower() in extensions
                        ]
                        if audio_files:
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
                        else:
                            print("No audio files found.")

                    elif par == "-dr": #dir repeat
                        extensions = (".mp3", ".flac", ".wav", ".ogg")
                        audio_files = [
                        f for f in Path(file_path).iterdir()
                        if f.suffix.lower() in extensions
                        ]
                        if audio_files:
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
                            print("No audio files found.")
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