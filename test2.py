import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
from rich.console import Console
console = Console()
from rich.console import Group
from rich.panel import Panel
from rich.align import Align
from rich.progress import Progress, BarColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
from mutagen import File
from re import match
from pathlib import Path
from random import shuffle
import shlex
import sys
import termios
import tty
import select
import signal





#cli input
def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch


def complete_path(text):
    if not text:
        return text

    def complete_fragment(fragment):
        fragment = fragment.strip()

        # Remove surrounding quotes
        if (fragment.startswith('"') and fragment.endswith('"')) or (
            fragment.startswith("'") and fragment.endswith("'")
        ):
            fragment = fragment[1:-1]

        fragment = os.path.expanduser(fragment)

        dir_name, prefix = os.path.split(fragment)
        if dir_name in ("", "."):
            dir_name = "."

        try:
            entries = list(os.scandir(dir_name))
        except OSError:
            return None

        exact = [e for e in entries if e.name == prefix]
        if len(exact) == 1:
            chosen = exact[0]
        else:
            matches = [e for e in entries if e.name.startswith(prefix)]
            if len(matches) != 1:
                return None
            chosen = matches[0]

        completed = os.path.join(dir_name, chosen.name)

        if chosen.is_dir():
            completed += os.sep

        return completed

    quote_hits = [
        (text.rfind(q), q)
        for q in ('"', "'")
        if text.count(q) % 2 == 1 and text.rfind(q) != -1
    ]

    if quote_hits:
        start, quote_char = max(quote_hits)
        fragment = text[start + 1:]
        completed = complete_fragment(fragment)
        if completed:
            return text[:start + 1] + completed + quote_char
        return text

    parts = text.split()
    for k in range(len(parts), 0, -1):
        base = " ".join(parts[:-k])
        fragment = " ".join(parts[-k:])

        completed = complete_fragment(fragment)
        if completed:
            if " " in completed:
                completed = f'"{completed}"'
            return (base + " " if base else "") + completed

    return text

def input_cli(prompt="> "):
    global history_index

    sys.stdout.write(prompt)
    sys.stdout.flush()

    buffer = ""
    history_index = len(history)

    while True:
        ch = getch()

         # CTRL+C
        if ch == "\x03":
            print()
            raise KeyboardInterrupt

        # CTRL+Z
        elif ch == "\x1a":
            print("\n[Suspended]")
            # restore terminal before suspending
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, termios.tcgetattr(sys.stdin))
            os.kill(os.getpid(), signal.SIGTSTP)

        # ENTER
        elif ch == "\r" or ch == "\n":
            print()
            if buffer.strip():
                history.append(buffer)
            return buffer

        # BACKSPACE
        elif ch == "\x7f":
            buffer = buffer[:-1]
            sys.stdout.write("\r" + prompt + buffer + " ")
            sys.stdout.write("\r" + prompt + buffer)
            sys.stdout.flush()

        # TAB
        elif ch == "\t":
            buffer = complete_path(buffer)
            sys.stdout.write("\r" + prompt + buffer)
            sys.stdout.flush()

        # ESC sequences
        elif ch == "\x1b":
            next1 = getch()
            next2 = getch()

            # UP arrow
            if next2 == "A":
                if history:
                    history_index = max(0, history_index - 1)
                    buffer = history[history_index]
                    sys.stdout.write("\r" + prompt + buffer + " " * 10)
                    sys.stdout.write("\r" + prompt + buffer)
                    sys.stdout.flush()

            # DOWN arrow
            elif next2 == "B":
                if history:
                    history_index = min(len(history) - 1, history_index + 1)
                    buffer = history[history_index]
                    sys.stdout.write("\r" + prompt + buffer + " " * 10)
                    sys.stdout.write("\r" + prompt + buffer)
                    sys.stdout.flush()

        else:
            buffer += ch
            sys.stdout.write(ch)
            sys.stdout.flush()
#/cliinput


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
    global repeat

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

    except KeyboardInterrupt:
        repeat = False
        pygame.mixer.music.stop()

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        clear_screen()
        print("Exitting...")
        
#main program
def main():
    clear_screen()

    global history
    global history_index
    history = []
    history_index = -1

    rhythmsync_ascii ='''[bold][#5900ab]
[#5900ab] _____  _           _   _                [#00d0ff]_____                  
[#5900ab]|  __ \\| |         | | | |              [#00d0ff]/ ____|                 
[#5900ab]| |__) | |__  _   _| |_| |__  _ __ ___ [#00d0ff]| (___  _   _ _ __   ___ 
[#5900ab]|  _  /| '_ \\| | | | __| '_ \\| '_ ` _ \\ [#00d0ff]\\___ \\| | | | '_ \\ / __|
[#5900ab]| | \\ \\| | | | |_| | |_| | | | | | | | |[#00d0ff]____) | |_| | | | | (__ 
[#5900ab]|_|  \\_\\_| |_|\\__, |\\__|_| |_|_| |_| |_|[#00d0ff]_____/ \__, |_| |_|\\___|
[#5900ab]               __/ |                         [#00d0ff]   __/ |           
[#5900ab]              |___/                           [#00d0ff] |___/            
'''
    console.print(Align.center(rhythmsync_ascii))
    while True:
        try:
            global repeat

            raw_command = input_cli("> ")
            
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
                    clear_screen()
                    console.print(Align.center(rhythmsync_ascii))

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
                    if command_parts == 2:
                        file_path = str(Path(command[1]).expanduser().resolve())
                        if os.path.exists(file_path):
                            run_player(file_path)
                            clear_screen()
                            console.print(Align.center(rhythmsync_ascii))
                        else:
                            print("Please enter a valid file path.")
                    elif command_parts == 3:
                        par = command[1]
                        file_path = str(Path(command[2]).expanduser().resolve())
                        if os.path.exists(file_path):
                            if par == "-r":
                                repeat = True
                                while repeat:
                                    run_player(file_path, "repeat")
                                clear_screen()
                                console.print(Align.center(rhythmsync_ascii))
                            elif par == "-d":
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
                                    run_player(file, f"directory {i} {len(audio_files)}")
                                    if repeat == False:
                                        break
                                clear_screen()
                                console.print(Align.center(rhythmsync_ascii))
                            elif par == "-ds":
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
                                    run_player(file, f"directory-shuffle {i} {len(audio_files)}")
                                    if repeat == False:
                                        break
                                clear_screen()
                                console.print(Align.center(rhythmsync_ascii))
                            elif par == "-dr":
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
                                        run_player(file, f"directory-repeat {i} {len(audio_files)}")
                                        if repeat == False:
                                            break
                                clear_screen()
                                console.print(Align.center(rhythmsync_ascii))
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
                           console.print(get_metadata(file_path, par), highlight=False)
                       else:
                           print("Please enter a valid file path.")
                    else:
                        print("Please enter a valid file path and parameters.")

                #invalid command
                else:
                    print("Invalid command! Enter 'help' to display command list.")
    
        except KeyboardInterrupt:
            print(f"Exitting...")
            break
        except Exception as e:
            clear_screen()
            console.print(Align.center(rhythmsync_ascii))
            print(f"Error: {e}")
    

if __name__ == "__main__":
    main()
