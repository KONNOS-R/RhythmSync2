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

---

## Installation and Usage

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

```
help - Lists all available commands.
clear - Clears the terminal.
```


### Playback

```
play {path} - Plays a single audio file once.
play -r {path} - Plays a single audio file in repeat mode until stopped (Ctrl+C).
play -d {directory} - Plays all supported audio files in alphabetical order.
play -dr {directory} - Plays all supported audio files in alphabetical order and loops around until stopped (Ctrl+C).
play -ds {directory} - Plays all supported audio files in shuffled order.
```


### Metadata

```
info {path} - Displays all available metadata.
info {path} [tags] - Displays only given metadata tags.
```

---

## Notes

- Paths containing spaces must be wrapped in quotes:

```
play "My Music/song.mp3"
```

- Use `Ctrl+C` to stop playback or exit the app