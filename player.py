import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
from rich.live import Live
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.layout import Layout
from mutagen import File
from re import match
import sys
import termios
import tty
import select

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
def make_header(title, artist, mode = None):
        if mode is not None:
            mode = mode.split()
            if mode[0] == "repeat":
                return Panel(
                    Group(
                        Align.center(f"[bold]{title}[/bold]"),
                        Align.center(f"[#5900ab]{artist}[/#5900ab]")
                        ),
                title="⭮",
                title_align="right",
                style="white",
                )
            elif mode[0][:9] == "directory":
                now, total = mode[1:3]
                if mode[0] == "directory-shuffle":
                    return Panel(
                        Group(
                            Align.center(f"[bold]{title}[/bold]"),
                            Align.center(f"[#5900ab]{artist}[/#5900ab]")
                            ),
                    title=f"🔀︎Playing {now} of {total}",
                    title_align="right",
                    style="white",
                    )
                elif mode[0] == "directory-repeat":
                    return Panel(
                        Group(
                            Align.center(f"[bold]{title}[/bold]"),
                            Align.center(f"[#5900ab]{artist}[/#5900ab]")
                            ),
                    title=f"⭮ Playing {now} of {total}",
                    title_align="right",
                    style="white",
                    )
    
                return Panel(
                    Group(
                        Align.center(f"[bold]{title}[/bold]"),
                        Align.center(f"[#5900ab]{artist}[/#5900ab]")
                        ),
                title=f"Playing {now} of {total}",
                title_align="right",
                style="white",
                )
            
        return Panel(
        Group(Align.center(f"[bold]{title}[/bold]"),
              Align.center(f"[#5900ab]{artist}[/#5900ab]")),
              style="white",
    )

#lyrics section
def make_lyrics(lyrics):
    line1, line2, line3, line4, line5 = lyrics
    return Align.center(Group(
            Align.center(f"[#1f1f1f]{line1}[#1f1f1f]"),
            Align.center(f"[#2f2f2f]{line2}[#2f2f2f]"),
            Align.center(f"[bold #00d0ff]{line3}[/bold #00d0ff]"),
            Align.center(f"[white]{line4}[white]"),
            Align.center(f"[#afafaf]{line5}[#afafaf]")
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

#get meatadata
def get_metadata(file_path, tags = None):
    try:
        audio = File(file_path)

        if audio is None:
            print(f"Error: Could not open file {file_path}")
            return None
        
        lines = []

        if tags is None:
            for key, value in audio.items():
                if isinstance(value, list):
                    value = "; ".join(str(v) for v in value)

                    lines.append(f"[green]{key}[/green]: {value}")
        else:
            for key, value in audio.items():
                if isinstance(value, list):

                    if key in tags:
                        value = "; ".join(str(v) for v in value)

                        lines.append(f"[green]{key}[/green]: {value}")
        
        return "\n".join(lines)
    
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return None

#get title and artist info
def get_ti_ar(file_path):
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

        lrc_tag_names = ['SYLT', 'SYLT::eng', 'LYRICS', 'LYRICS:eng', 'LYRICS-ENG', 'LYRICS_EN', 'LYRICS_SYNCED', 'SYNCEDLYRICS']

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
    lyrics = [[line[1:9],line[10:].strip()] for line in lrc_lines if match(timestamp, line)]
    lyrics.insert(0,['00:00.00', ""])
    for x in lyrics:
        if x[1] == "":
            x[1] = "♫"
    return lyrics

# music player
def run_player(file_path, mode=None):
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)

        layout = make_layout()

        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        total_length = int(pygame.mixer.Sound(file_path).get_length() * 1000)

        title, artist = get_ti_ar(file_path)

        lyrics_exist = False
        raw_lrc = get_lrc(file_path)
        if raw_lrc is not None:
            lyrics = format_lrc(raw_lrc)
            lyrics_exist = True

        clear_screen()

        layout["header"].update(make_header(title, artist, mode))
        layout["lyrics"].update(
            Align.center("No lyrics to display", vertical="middle")
        )
        progress = make_player()
        layout["player"].update(progress)

        with Live(layout, refresh_per_second=100):
            playback = progress.add_task(
                f"[red]< [#00d0ff]",
                total=total_length,
                suffix="[#00d0ff] [red]>"
            )

            lyric_index = 0
            paused = False

            while pygame.mixer.music.get_busy() or paused:
                current_time = pygame.mixer.music.get_pos()

                # keyboard input
                ready, _, _ = select.select([sys.stdin], [], [], 0)

                if ready:
                    key = sys.stdin.read(1)

                    if key == " ":
                        if paused:
                            pygame.mixer.music.unpause()
                            paused = False
                        else:
                            progress.update(
                                playback,
                                completed=current_time,
                                description=f"[red]< [/red]▶ [#00d0ff]{format_time(current_time)}",
                                suffix=f"[#00d0ff]{format_time(total_length - current_time)} [red]>"
                            )
                            pygame.mixer.music.pause()
                            paused = True

                if not paused:
                    if lyrics_exist and lyric_index < len(lyrics):
                        if unformat_time(lyrics[lyric_index][0]) <= current_time:
                            layout["lyrics"].update(make_lyrics((
                                lyrics[lyric_index - 2][1] if lyric_index > 1 else "",
                                lyrics[lyric_index - 1][1] if lyric_index > 0 else "",
                                lyrics[lyric_index][1],
                                lyrics[lyric_index + 1][1] if lyric_index < len(lyrics) - 1 else "",
                                lyrics[lyric_index + 2][1] if lyric_index < len(lyrics) - 2 else ""
                            )))
                            lyric_index += 1

                    progress.update(
                        playback,
                        completed=current_time,
                        description=f"[red]< [/red]⏸ [#00d0ff]{format_time(current_time)}",
                        suffix=f"[#00d0ff]{format_time(total_length - current_time)} [red]>"
                    )
            return True
            
    except KeyboardInterrupt:
        pygame.mixer.music.stop()
        return False
    
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        clear_screen()
        print("Exitting...")