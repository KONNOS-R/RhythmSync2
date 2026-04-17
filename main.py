import pygame
from rich.progress import Progress, BarColumn, TextColumn
from rich.console import Console
import os

#clear the terminal
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

#format time in mm:ss.xx format
def format_time(milliseconds):
    min = int((milliseconds // 1000) // 60)
    sec = (milliseconds // 1000) % 60
    mil = milliseconds % 1000
    hund = int(mil // 10)
    return f"{min:02}:{sec:02}.{hund:02}"

#main programme
def main():
    clear_screen()

    file_path = "test.flac"

    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    total_length = int(pygame.mixer.Sound(file_path).get_length()*1000)
    print(format_time(total_length))


    with Progress(
            TextColumn("{task.description}[/]", justify="right"),
            BarColumn(bar_width=None),
            TextColumn("{task.fields[suffix]}", justify="right"),
        ) as progress:

        playback = progress.add_task(
        f"[#03ad00]Playing: [white]{file_path} [red]< [#00d0ff]",
        total=total_length, 
        suffix="[#00d0ff] [red]>")

        while pygame.mixer.music.get_busy(): #music starts
            current_time = pygame.mixer.music.get_pos()

            progress.update(playback, 
                            completed=current_time,
                            description=f"[#03ad00]Playing: [white]{file_path} [red]< [#00d0ff]{format_time(current_time)}",
                            suffix=f"[#00d0ff]{format_time(total_length - current_time)} [red]>"
                            )





if __name__ == "__main__":
    main()