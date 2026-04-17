import pygame
from rich.progress import Progress, BarColumn, TextColumn
from rich.console import Console
import mutagen
from mutagen import File
import os
from re import match

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
    title = [line for line in lrc_lines if line[:4] == "[ti:"][0]
    artist = [line for line in lrc_lines if line[:4] == "[ar:"][0]
    lyrics = [line for line in lrc_lines if match(timestamp, line)]
    return title, artist, lyrics

#main programme
def main():
    clear_screen()

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


'''
    lyric_index = 0
    
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

            #if

            progress.update(playback, 
                            completed=current_time,
                            description=f"[#03ad00]Playing: [white]{file_path} [red]< [#00d0ff]{format_time(current_time)}",
                            suffix=f"[#00d0ff]{format_time(total_length - current_time)} [red]>"
                            )

'''



if __name__ == "__main__":
    main()