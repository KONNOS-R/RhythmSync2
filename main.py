import pygame
from rich.console import Console
from rich.console import Group
from rich.panel import Panel
from rich.align import Align
from rich.progress import Progress, BarColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
from rich import box
import mutagen
from mutagen import File
import os
from re import match

#create rich layout
def make_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=5),
        Layout(name="lyrics", ratio=1),
        Layout(name="player", size=3)
    )
    return layout

def make_header(title, artist):
        return Panel(
        Group(Align.center(f"[bold]{title}[/bold]\n"),Align.center(f"[cyan]{artist}[/cyan]")),
        style="white",
    )

def make_lyrics(lyrics):
    line1, line2, line3 = lyrics
    return Align.center(Group(Align.center(f"[bold white]{line1}[/bold white]"),
                Align.center(f"[bold cyan]{line2}[/bold cyan]"),
                Align.center(f"[bold white]{line3}[/bold white]")
                ),
            vertical="middle"
    )
                 
    Align.center(f"[bold white]{line1}[/bold white]",
                vertical="middle"
                )

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
    title = [line[4:-1] for line in lrc_lines if line[:4] == "[ti:"][0]
    artist = [line[4:-1] for line in lrc_lines if line[:4] == "[ar:"][0]
    lyrics = [[line[1:9],line[10:]] for line in lrc_lines if match(timestamp, line)]
    lyrics.insert(0,['00:00.00', ""])
    for x in lyrics:
        if x[1] == "":
            x[1] = "♫"
    lyrics.append(["", ""])
    return title, artist, lyrics

#main programme
def main():
    clear_screen()
    layout = make_layout()

    file_path = "test.flac"

    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    total_length = int(pygame.mixer.Sound(file_path).get_length()*1000)
    print(format_time(total_length))

    raw_lrc = get_lrc(file_path)
    title, artist, lyrics = format_lrc(raw_lrc)
    print("title:", title)
    print("artist:", artist)
    print("lyrics:", lyrics)

    layout["header"].update(make_header(title, artist))

#'''
    progress = make_player()
    
    layout["player"].update(progress)

    with Live(layout, refresh_per_second=30):
        playback = progress.add_task(
        f"[red]< [#00d0ff]",
        total=total_length, 
        suffix="[#00d0ff] [red]>")

        layout["lyrics"].update("")

        lyric_index = 0

        while pygame.mixer.music.get_busy(): #music starts
            current_time = pygame.mixer.music.get_pos()

            if lyric_index < len(lyrics)-1:
                if unformat_time(lyrics[lyric_index][0]) <= current_time:
                    layout["lyrics"].update(make_lyrics((lyrics[lyric_index-1][1], lyrics[lyric_index][1], lyrics[lyric_index+1][1])))
                    lyric_index += 1

            progress.update(playback, 
                            completed=current_time,
                            description=f"[red]< [#00d0ff]{format_time(current_time)}",
                            suffix=f"[#00d0ff]{format_time(total_length - current_time)} [red]>"
                            )

#'''



if __name__ == "__main__":
    main()