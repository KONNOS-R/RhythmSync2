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
import sys
import termios
import tty
import select

import metadata
import terminal_disp


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

#format time in mm:ss.xx format
def format_time(milliseconds):
    min = int((milliseconds // 1000) // 60)
    sec = (milliseconds // 1000) % 60
    mil = milliseconds % 1000
    hund = int(mil // 10)
    return f"{min:02}:{sec:02}.{hund:02}"

# music player
def run_player(file_path, mode=None):
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)

    mode = mode.split()

    try:
        tty.setcbreak(fd)

        layout = make_layout()

        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        total_length = int(pygame.mixer.Sound(file_path).get_length() * 1000)

        title, artist = metadata.get_ti_ar(file_path)

        lyrics_exist = False
        raw_lrc = metadata.get_lrc(file_path)
        if raw_lrc is not None:
            lyrics = metadata.format_lrc(raw_lrc)
            lyrics_exist = True

        terminal_disp.clear_screen()

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
                    #SPACE
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
                    #ESC seq
                    elif key == "\x1b":
                            seq = sys.stdin.read(2)
                            # LEFT arrow
                            if seq == "[D":
                                if mode[0] == "single":
                                    pygame.mixer.music.stop()
                                    return (True, 0)
                                elif mode[0] == "repeat":
                                    pygame.mixer.music.stop()
                                    return (True, 0)
                                elif mode[0][:9] == "directory":
                                    pygame.mixer.music.stop()
                                    return (True, int(mode[1])-1)
                                
                            #RIGHT arrow
                            elif seq == "[C":
                                if mode[0] == "single":
                                    pygame.mixer.music.stop()
                                    return (False, 0)
                                elif mode[0] == "repeat":
                                    pygame.mixer.music.stop()
                                    return (True, 0)
                                elif mode[0][:9] == "directory":
                                    pygame.mixer.music.stop()
                                    return (True, int(mode[1])+1)

                if not paused:
                    if lyrics_exist and lyric_index < len(lyrics):
                        if metadata.unformat_time(lyrics[lyric_index][0]) <= current_time:
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

            if mode[0] == "single":
                return (False, 0)
            if mode[0] == "repeat":
                return (True, 0)
            elif mode[0][:9] == "directory":
                return (True, int(mode[1])+1)
            
    except KeyboardInterrupt:
        pygame.mixer.music.stop()
        return (False, 0)
    
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        terminal_disp.clear_screen()
        print("Exitting...")