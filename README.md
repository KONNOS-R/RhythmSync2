# RhythmSync

CLI audio player that plays music while displaying synchronized lyrics (LRC).

---

## Features

- Play single audio files:
  - Once
  - In loop (`-r`)
- Play all supported audio files in a directory:
  - Alphabetical order (`-d`)
  - Alphabetical loop (`-dr`)
  - Shuffle (`-ds`)
- Display synchronized lyrics during playback
- Show song metadata tags
- Styled terminal music player UI
- Convert audio files to other formats using ffmpeg
- Player controls
  - Pause (`SPACE`)
  - Next (`RIGHT Arrow`)
  - Previous (`LEFT Arrow`)

---

## Requirements

- Python 3.8+
- FFmpeg (optional, for conversion feature)

---

## Compatibility

RhythmSync is currently intended for UNIX-based systems (Linux/macOS).
All versions after **1.0.0** don't work with non-UNIX systems

---

## Installation and Usage

- PyPI page: [Click here](https://pypi.org/project/rhythmsync/)

<br>

- Install the CLI application
```
pip install rhythmsync
```

- Launch the CLI application:
```
rhythmsync
```

---

## Supported Audio Formats

- `.mp3`
- `.flac`
- `.wav`
- `.ogg`

### Notes

- Other audio formats might work, but full functionality is not guaranteed.

---

## Lyrics Sync

RhythmSync reads embedded lyric metadata from audio files.

Supported tags include:
- `SYLT`, `SYLT::eng`
- `LYRICS`, `LYRICS:eng`
- `LYRICS-ENG`, `LYRICS_EN`
- `LYRICS_SYNCED`, `SYNCEDLYRICS`

### LRC Format

```
[00:12.34] First line
[00:15.67] Second line
[00:18.90] Third line
```

- Format: `[mm:ss.xx] Line`

### Notes

- If no lyrics are found, a placeholder message is shown.

---

## Commands

### General

- `help` - Lists all available commands.
- `ls` - Lists all files and directories in the current working directory.
- `ls {path}` - Lists all files and directories in the specified directory.
- `cd {path}` - Changes the current working directory to the specified directory.
- `clear` - Clears the terminal.

### Playback

- `play {path}` - Plays a single audio file once.
- `play -r {path}` - Plays a single audio file in repeat mode until stopped (Ctrl+C).
- `play -d {directory}` - Plays all supported audio files in alphabetical order.
- `play -dr {directory}` - Plays all supported audio files in alphabetical order and loops until stopped (Ctrl+C).
- `play -ds {directory}` - Plays all supported audio files in shuffled order and loops until stopped (Ctrl+C).

### Metadata

- `info {path}` - Displays all available metadata.
- `info {path}` [tags] - Displays only given metadata tags.

### Converter

- `convert {input path} {output path}` - Converts an audio file to another format (FFmpeg required).

---

## Notes

- Paths containing spaces must be wrapped in quotes or escaped with backslashes:

```
play "My Music/song.mp3"
play My\ Music/song.mp3
```

- The **convert** command uses FFmpeg and may alter or corrupt metadata

- Use `Ctrl+C` to stop playback or exit the app