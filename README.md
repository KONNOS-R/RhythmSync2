#RhythmSync
CLI audio player that plays music while displaying synchronized lyrics (LRC).


#Features:
- Play single audio files from the command line:
    -Once
    -In loop
- Plays all supported audio files inside a directory from the command line:
    -In alphabetical order
    -In alphabetical order loop
    -In shuffle
- Shows synced lyrics while music plays
- Displays song metadata tags
- Styled terminal music player UI


#Supported audio formats:
- .mp3
- .flac
- .wav
- .ogg

Note: other audio formats might work but full reliable functionality is not guaranteed.


#Lyrics sync feature:
RhythmSync reads the embedded lyric metadata of an audio file to display the lyrics.
For this feature to work properly the audio files must have one of the following metadata tags with the lyrics assigned to it:
-'USLT'
-'SYLT'
-'USLT::eng'
-'USLT::XXX'
-'SYLT::eng'
-'LYRICS'
-'LYRICS:eng'
-'LYRICS:XXX'
-'LYRICS-ENG'
-'LYRICS-XXX'
-'LYRICS_EN'
-'LYRICS_UNSYNCED'
-'LYRICS_SYNCED'
-'UNSYNCEDLYRICS'
-'SYNCEDLYRICS'
-'©lyr'

Synced lyrics should use timestamped lines like:
[00:12.34] First line
[00:15.67] Second line
[00:18.90] Third line

Note: if no lyrics are found, RhythmSync shows a placeholder message.


#Command list:
help - Lists all available commands.
clear - Clears the terminal.
play {path} - Plays a single audio file once.
play -r {path} - Plays a single audio file in repeat mode until stopped (Ctrl+C).
play -d {directory} - Plays all supported audio files in the directory in alphabetical order.
play -dr {directory} - Plays all supported audio files in alphabetical order and loops around until stopped (Ctrl+C).
play -ds {directory} - Plays all supported audio files in the directory in shuffled order.
info {path} - Displays all available metadata for a file.
info {path} [tags] - Displays only given metadata tags for a file.


#Other notes:
-Paths containing spaces should be wrapped in quotes
-Use Ctrl+C to stop playback gracefully or to exit the cli app.