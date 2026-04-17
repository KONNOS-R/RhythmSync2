import time
import asyncio
import mutagen
from mutagen import File
import pygame
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
import os
from re import match


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def format_time(milliseconds):
    min = int((milliseconds // 1000) // 60)
    sec = (milliseconds // 1000) % 60
    mil = milliseconds % 1000
    hund = int(mil // 10)
    return f"{min:02}:{sec:02}.{hund:02}"


def format_lrc(lrc_data):
    timestamp = r"^\[\d{2}:\d{2}\.\d{2}\]"
    lrc_lines = lrc_data.split("\n")
    return [line for line in lrc_lines if match(timestamp, line)]


def get_lrc_from_audio(file_path):
    try:
        audio = File(file_path)

        if audio is None:
            print(f"Error: Could not open file {file_path}")
            return None

        lrc_tag_names = ['LYRICS', 'UNSYNCEDLYRICS', 'LRC', 'USLT::eng']

        for tag_name in lrc_tag_names:
            if tag_name in audio:
                return audio[tag_name][0]

        return None

    except Exception as e:
        print(f"Error extracting LRC data: {e}")
        return None


#main programme
def main():
    clear_screen()
    console = Console()
    pygame.mixer.init()

    console.print('''[#00d0ff]
  _____  _           _   _                _____                  
 |  __ \\| |         | | | |              / ____|                 
 | |__) | |__  _   _| |_| |__  _ __ ___ | (___  _   _ _ __   ___ 
 |  _  /| '_ \\| | | | __| '_ \\| '_ ` _ \\ \___ \\| | | | '_ \\ / __|
 | | \\ \\| | | | |_| | |_| | | | | | | | |____) | |_| | | | | (__ 
 |_|  \\_\\_| |_|\\__, |\\__|_| |_|_| |_| |_|_____/ \__, |_| |_|\\___|
                __/ |                            __/ |           
               |___/                            |___/            
''')

    file_path = "AddMusicHere/"+input("audio name: ")

    try:
        lrc_data = get_lrc_from_audio(file_path)

        if lrc_data:
            lyrics = format_lrc(lrc_data)
        else:
            console.print("[red]No lyrics found in audio file.[/red]")
            lyrics = []

    except Exception as e:
        print(f"Error loading metadata: {e}")
        return None

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Error playing audio file: {e}")
        return None

    total_length = int(pygame.mixer.Sound(file_path).get_length()) * 1000

    clear_screen()

    with Progress(
        TextColumn("{task.description}[/]", justify="right"),
        BarColumn(bar_width=None),
        TextColumn("{task.fields[suffix]}", justify="right"),
    ) as progress:

        playback = progress.add_task(
            f"[#03ad00]Playing: [white]{file_path.split("/")[1]} [red]< [#00d0ff]",
            total=total_length, 
            suffix="[#00d0ff] [red]>")

        i = 0

        try:
            while pygame.mixer.music.get_busy():
                async def loop(i):
                    interval = 0.01
                    next_time = time.perf_counter()
                    
                    while True:
                        next_time += interval

                        #programme inside timer
                        current_time = pygame.mixer.music.get_pos()
                        progress.update(
                            playback, 
                            advance=10, 
                            description=f"[#03ad00]Playing: [white]{file_path.split("/")[1]} [red]< [#00d0ff]{format_time(current_time)}",
                            suffix=f"[#00d0ff]{format_time(total_length - current_time)} [red]>")
                        if i < len(lyrics) and format_time(current_time) >= lyrics[i][1:9]:
                            clear_screen()
                            console.print(lyrics[i][10:], justify="center")
                            i += 1

                        sleep_time = next_time - time.perf_counter()
                        if sleep_time > 0:
                            await asyncio.sleep(sleep_time)
                        else:
                            await asyncio.sleep(0)
                
                asyncio.run(loop(i))                

        except KeyboardInterrupt:
            pass
        finally:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            clear_screen()
            console.print("[yellow]Playback interrupted.[/yellow]")


if __name__ == "__main__":
    main()
