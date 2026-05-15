from mutagen import File
from re import match


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
            print(f"Player error: Could not open file {file_path}")
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
        print(f"Player error: Error extracting metadata: {e}")
        return None

#get title and artist info
def get_ti_ar(file_path):
    try:
        audio = File(file_path)

        if audio is None:
            return f"Unknown Title ({file_path})", "Unknown Artist"
        
        title = audio.get("title", [f"Unknown Title ({file_path})"])[0]
        artist = audio.get("artist", ["Unknown Artist"])[0]

        return title, artist
    
    except Exception as e:
        print(f"Player error: Error extracting metadata: {e}")
        return f"Unknown Title ({file_path})", "Unknown Artist"

#get lrc data from the audio file
def get_lrc(file_path):
    try:
        audio = File(file_path)

        if audio is None:
            print(f"Player error: Could not open file {file_path}")
            return None

        lrc_tag_names = ['SYLT', 'SYLT::eng', 'LYRICS', 'LYRICS:eng', 'LYRICS-ENG', 'LYRICS_EN', 'LYRICS_SYNCED', 'SYNCEDLYRICS']

        for tag_name in lrc_tag_names:
            if tag_name in audio:
                return audio[tag_name][0]
        return None

    except Exception as e:
        print(f"Player error: Error extracting LRC data: {e}")
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