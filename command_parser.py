import os
from rich.console import Console
console = Console()
from rich.align import Align
from pathlib import Path
from random import shuffle
import shlex

import player
import metadata
import converter
import terminal_disp


def parse_command(raw_command):
    if raw_command.strip():
        command = shlex.split(raw_command)
        command_parts = len(command)
    
        #help command
        if command[0] == "help" and command_parts == 1:
            terminal_disp.help_msg()
        
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
            terminal_disp.clear_screen()
            terminal_disp.logo()
        
        #play command
        elif command[0] == "play":
            if command_parts == 2: #single
                file_path = str(Path(command[1]).expanduser().resolve())
                if os.path.exists(file_path):
                    repeat = True
                    while repeat:
                        repeat = player.run_player(file_path, "single")[0]
                    terminal_disp.clear_screen()
                    terminal_disp.logo()
                else:
                    print("Please enter a valid file path.")

            elif command_parts == 3:
                par = command[1]
                file_path = str(Path(command[2]).expanduser().resolve())
                if os.path.exists(file_path):
                    if par == "-r": #single repeat
                        repeat = True
                        while repeat:
                            repeat = player.run_player(file_path, "repeat")[0]
                        terminal_disp.clear_screen()
                        terminal_disp.logo()



                    elif par[:2] == "-d": #directory modes
                        extensions = (".mp3", ".flac", ".wav", ".ogg")
                        audio_files = [
                        f for f in Path(file_path).iterdir()
                        if f.suffix.lower() in extensions
                        ]

                        if par == "-d": #dir
                            if audio_files:
                                audio_files.sort()
                                repeat = True
                                i = 1
                                while i-1 < len(audio_files) and i >= 1 and repeat:
                                    for j in range(i-1, len(audio_files)):
                                        repeat, i = player.run_player(audio_files[j], f"directory {i} {len(audio_files)}")
                                        if i < 1:
                                            i = 1
                                        break
                                terminal_disp.clear_screen()
                                terminal_disp.logo()
                            else:
                                print("No audio files found.")

                        elif par == "-dr": #dir repeat
                            if audio_files:
                                audio_files.sort()
                                repeat = True
                                i = 1
                                while repeat:
                                    for j in range(i-1, len(audio_files)):
                                        repeat, i = player.run_player(audio_files[j], f"directory {i} {len(audio_files)}")
                                        if i < 1:
                                            i = len(audio_files)
                                        elif i > len(audio_files):
                                            i = 1
                                        break
                                terminal_disp.clear_screen()
                                terminal_disp.logo()
                            else:
                                print("No audio files found.")

                        elif par == "-ds": #dir shuffle
                            if audio_files:
                                shuffle(audio_files)
                                repeat = True
                                i = 1
                                while repeat:
                                    for j in range(i-1, len(audio_files)):
                                        repeat, i = player.run_player(audio_files[j], f"directory {i} {len(audio_files)}")
                                        if i < 1:
                                            i = len(audio_files)
                                        elif i > len(audio_files):
                                            i = 1
                                        break
                                terminal_disp.clear_screen()
                                terminal_disp.logo()
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
                   console.print(metadata.get_metadata(file_path, par), highlight=False)
               else:
                   print("Please enter a valid file path.")
            else:
                print("Please enter a valid file path and parameters.")

        #convert command
        elif command[0] == "convert" and command_parts == 3:
            input_path = Path(command[1]).expanduser().resolve()
            output_path = Path(command[2]).expanduser().resolve()
            output_dir = Path("/".join(command[2].split("/")[:-1])).expanduser().resolve()
            if os.path.exists(input_path) and os.path.exists(output_dir):
                converter.convert(input_path, output_path)
            else:
                print("Please enter valid file paths.")
        #invalid command
        else:
            print("Invalid command! Enter 'help' to display command list.")