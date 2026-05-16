import os
from rich.console import Console
console = Console()
from rich.align import Align


#clear the terminal
def clear_screen():
    os.system('clear')

#print logo
def logo():
    console.print(Align.center('''[bold][#5900ab]
[#5900ab] _____  _           _   _                [#00d0ff]_____                  
[#5900ab]|  __ \\| |         | | | |              [#00d0ff]/ ____|                 
[#5900ab]| |__) | |__  _   _| |_| |__  _ __ ___ [#00d0ff]| (___  _   _ _ __   ___ 
[#5900ab]|  _  /| '_ \\| | | | __| '_ \\| '_ ` _ \\ [#00d0ff]\\___ \\| | | | '_ \\ / __|
[#5900ab]| | \\ \\| | | | |_| | |_| | | | | | | | |[#00d0ff]____) | |_| | | | | (__ 
[#5900ab]|_|  \\_\\_| |_|\\__, |\\__|_| |_|_| |_| |_|[#00d0ff]_____/ \__, |_| |_|\\___|
[#5900ab]               __/ |                         [#00d0ff]   __/ |           
[#5900ab]              |___/                           [#00d0ff] |___/            
'''
    ))

#print help message
def help_msg():
    console.print('''COMMAND LIST:
[green]help[/green]  lists all available commands

[green]ls[/green]  lists all files and directories in the current working directory
[green]ls[/green] [cyan]{dir}[/cyan]  lists all files and directories in the specified directory
                                          
[green]cd[/green] [cyan]{dir}[/cyan]  changes the current working directory to the specified directory

[green]clear[/green]  clears the terminal
                   
[green]play[/green] [cyan]{path}[/cyan]  the given audio file plays once
[green]play[/green] [cyan]{option} {path}[/cyan]
    [cyan]-r[/cyan]   the given audio file plays in repeat until stopped
[green]play[/green] [cyan]{option} {dir}[/cyan]
    [cyan]-d[/cyan]   the audio files of given directory play in alphabetical order
    [cyan]-dr[/cyan]  the audio files of given directory play in alphabetical order and loop around until stopped
    [cyan]-ds[/cyan]  the audio files of given directory play in shuffled order and loop around until stopped
    [cyan]-D[/cyan]   the audio files of given directory and its subdirectories play in alphabetical order
    [cyan]-Dr[/cyan]  the audio files of given directory and its subdirectories play in alphabetical order and loop around until stopped
    [cyan]-Ds[/cyan]  the audio files of given directory and its subdirectories play in shuffled order and loop around until stopped
   
[green]info[/green] [cyan]{path}[/cyan]  shows all available tags and their respective values for the given audio file.
[green]info[/green] [cyan]{path} {tags}[/cyan]  hows only the provided tags (separate tags with space for multiple ones) and their respective values
                  
[green]convert[/green] [cyan]{input path} {output path}[/cyan] Converts an audio file to another format (FFmpeg required)
''')