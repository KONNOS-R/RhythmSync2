from mutagen import File
from re import match


def get_tag_map():
    return {
        "title": ["title", "TIT2", "TITLE", "©nam"],
        "artist": ["artist", "TPE1", "ARTIST", "©ART"],
        "album": ["album", "TALB", "ALBUM", "©alb"],
        "albumartist": ["albumartist", "TPE2", "ALBUMARTIST", "aART"],
        "date": ["date", "TDRC", "YEAR", "©day"],
        "copyright": ["copyright", "TCOP", "copyright"],
        "publisher": ["publisher", "TPUB"],
        "tracknumber": ["tracknumber", "TRCK"],
        "discnumber": ["discnumber", "TPOS"],
        "description": ["description", "COMM", "desc"],
        "lyrics": ["SYLT", "SYLT::eng", "LYRICS", "LYRICS:eng", "LYRICS-ENG", "LYRICS_EN", "LYRICS_SYNCED", "SYNCEDLYRICS", "USLT", "USLT::eng"],
        "genre": ["genre", "TCON", "©gen"]
    }

#get meatadata
def get_metadata(file_path, tags=None):
    try:
        audio = File(file_path)

        if audio is None or audio.tags is None:
            print(f"Metadata error: Unsupported or unreadable file: {file_path}")
            return None

        print(audio.pprint())
        tag_map = get_tag_map()
        lines = []
        reverse_map = {}

        for normal, variants in tag_map.items():
            for v in variants:
                reverse_map[v.lower()] = normal

        def clean(value):
            if isinstance(value, (list, tuple)):
                return "; ".join(str(v) for v in value)
            return str(value)

        for key, value in audio.tags.items():

            norm_key = reverse_map.get(key.lower())

            if norm_key is None:
                continue

            if tags is not None and norm_key not in tags:
                continue

            lines.append(f"[green]{norm_key}[/green]: {clean(value)}")

        return "\n".join(lines)

    except Exception as e:
        print(f"Metadata error: {e}")
        return None
    
    except Exception as e:
        print(f"Metadata error: Error extracting metadata: {e}")
        return None

#get title and artist info
def get_ti_ar(file_path):
    try:
        audio = File(file_path)

        if audio is None or audio.tags is None:
            return f"Unknown Title ({file_path})", "Unknown Artist"

        tag_map = get_tag_map()
        reverse_map = {}

        for canonical, keys in tag_map.items():
            for k in keys:
                reverse_map[k.lower()] = canonical

        def extract(canonical_name):
            for key, value in audio.tags.items():
                norm = reverse_map.get(key.lower())
                if norm != canonical_name:
                    continue
                if isinstance(value, (list, tuple)):
                    return str(value[0])
                return str(value)
            return None

        title = extract("title")
        artist = extract("artist")

        if not title:
            title = f"Unknown Title ({file_path})"
        if not artist:
            artist = "Unknown Artist"
        return title, artist

    except Exception as e:
        print(f"Metadata error: {e}")
        return f"Unknown Title ({file_path})", "Unknown Artist"

#get lrc data from the audio file
def get_lrc(file_path):
    try:
        audio = File(file_path)

        if audio is None or audio.tags is None:
            return None

        lrc_tag_names = ['SYLT', 'SYLT::eng', 'LYRICS', 'LYRICS:eng', 'LYRICS-ENG', 'LYRICS_EN', 'LYRICS_SYNCED', 'SYNCEDLYRICS']

        for tag in lrc_tag_names:
            if tag in audio.tags:

                value = audio.tags[tag]

                if tag.startswith("SYLT"):
                    try:
                        return "\n".join([t[2] for t in value[0].text])
                    except Exception:
                        return value[0]
                return value[0] if isinstance(value, list) else value
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