import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
from rich.console import Console
from rich.console import Group
from rich.panel import Panel
from rich.align import Align
from rich.progress import Progress, BarColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
from mutagen import File
from re import match
from pathlib import Path


#create rich layout
def make_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=4),
        Layout(name="lyrics", ratio=1),
        Layout(name="player", size=3)
    )
    return layout

#header section
def make_header(title, artist):
        return Panel(
        Group(Align.center(f"[bold]{title}[/bold]"),Align.center(f"[cyan]{artist}[/cyan]")),
        style="white",
    )

#lyrics section
def make_lyrics(lyrics):
    line1, line2, line3 = lyrics
    return Align.center(Group(Align.center(f"[bold white]{line1}[/bold white]"),
                Align.center(f"[bold cyan]{line2}[/bold cyan]"),
                Align.center(f"[bold white]{line3}[/bold white]")
                ),
            vertical="middle"
    )

#player section
def make_player():
    return Progress(
        TextColumn("{task.description}[/]", justify="right"),
        BarColumn(bar_width=None),
        TextColumn("{task.fields[suffix]}", justify="right"),
    )

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

#format time to milliseconds
def unformat_time(time_str):
    min, sec = time_str.split(":")
    sec, hund = sec.split(".")
    milliseconds = (
        int(min) * 60 * 1000 + int(sec) * 1000 + int(hund) * 10)
    return milliseconds

#get metadata
def get_metadata(file_path):
    try:
        audio = File(file_path)

        if audio is None:
            return "Unknown Title", "Unknown Artist"
        
        title = audio.get("title", ["Unknown Title"])[0]
        artist = audio.get("artist", ["Unknown Artist"])[0]

        return title, artist
    
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return "Unknown Title", "Unknown Artist"

#get lrc data from the audio file
def get_lrc(file_path):
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

#get lyric lines without the tags from the lrc data
def format_lrc(lrc_data):
    timestamp = r"^\[\d{2}:\d{2}\.\d{2}\]"
    lrc_lines = lrc_data.split("\n")
    lyrics = [[line[1:9],line[10:]] for line in lrc_lines if match(timestamp, line)]
    lyrics.insert(0,['00:00.00', ""])
    for x in lyrics:
        if x[1] == "":
            x[1] = "♫"
    return lyrics


def run_player(file_path):
    try:
        layout = make_layout()

        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        total_length = int(pygame.mixer.Sound(file_path).get_length()*1000)

        print(format_time(total_length))

        title, artist = get_metadata(file_path)

        print("title:", title)
        print("artist:", artist)

        lyrics_exist = False
        raw_lrc = get_lrc(file_path)
        if raw_lrc is not None:
            lyrics = format_lrc(raw_lrc)
            lyrics_exist = True

            print("lyrics:", lyrics)

        clear_screen()
        
        layout["header"].update(make_header(title, artist))

        layout["lyrics"].update(Align.center("No lyrics to display", vertical="middle"))

        progress = make_player()
        layout["player"].update(progress)

        with Live(layout, refresh_per_second=100):
            playback = progress.add_task(
            f"[red]< [#00d0ff]",
            total=total_length, 
            suffix="[#00d0ff] [red]>")

            lyric_index = 0

            while pygame.mixer.music.get_busy(): #music starts
                current_time = pygame.mixer.music.get_pos()

                if lyrics_exist and lyric_index < len(lyrics):
                    if unformat_time(lyrics[lyric_index][0]) <= current_time:
                        layout["lyrics"].update(make_lyrics((lyrics[lyric_index-1][1] if lyric_index > 0 else "", lyrics[lyric_index][1], lyrics[lyric_index+1][1] if lyric_index < len(lyrics)-1 else "")))
                        lyric_index += 1

                progress.update(playback, 
                                completed=current_time,
                                description=f"[red]< [#00d0ff]{format_time(current_time)}",
                                suffix=f"[#00d0ff]{format_time(total_length - current_time)} [red]>"
                                )
    except KeyboardInterrupt:
        clear_screen()
        print(f"Exitting...")
        pygame.mixer.music.stop()
        

#main program
def main():
    while True:
        try:
            Console().print(Align.center('''[#5900ab]
[#5900ab] _____  _           _   _                [#00d0ff]_____                  
[#5900ab]|  __ \\| |         | | | |              [#00d0ff]/ ____|                 
[#5900ab]| |__) | |__  _   _| |_| |__  _ __ ___ [#00d0ff]| (___  _   _ _ __   ___ 
[#5900ab]|  _  /| '_ \\| | | | __| '_ \\| '_ ` _ \\ [#00d0ff]\\___ \\| | | | '_ \\ / __|
[#5900ab]| | \\ \\| | | | |_| | |_| | | | | | | | |[#00d0ff]____) | |_| | | | | (__ 
[#5900ab]|_|  \\_\\_| |_|\\__, |\\__|_| |_|_| |_| |_|[#00d0ff]_____/ \__, |_| |_|\\___|
[#5900ab]               __/ |                         [#00d0ff]   __/ |           
[#5900ab]              |___/                           [#00d0ff] |___/            
'''))
            file_path = str(Path(input("Path to audio file: ")).expanduser().resolve())

            run_player(file_path)

            clear_screen()

        except KeyboardInterrupt:
            print(f"Exitting...")
            break
        except BaseException as e:
            clear_screen()
            print(f"Error: {e}")
    

if __name__ == "__main__":
    clear_screen()
    main()