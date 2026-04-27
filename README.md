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






Supported audio formats:
- .mp3
- .flac
- .wav
- .ogg




#Command list:
help - Lists all available commands.
clear - Clears the terminal.
play {par} {path} - Plays the audio file located at the specified {path}.
    If {par} is "-r", the audio file plays in a loop until stopped.
    If {par} is "-d" and {path} is a directory, the audio files of given directory play in alphabetic order.
    If {par} is "-dr" and {path} is a directory, the audio files of given directory play in alphabetic order and loop around until stopped.
    If {par} is "-ds" and {path} is a directory, the audio files of given directory play in shuffle.
    If {par} is omitted, the audio file plays once.
info {path} {tags} - Displays metadata for the file at {path}.
    If {tags} is provided (separate them with space for multiple tags), shows only those specific tags and their respective values.
    If {tags} is omitted, shows all available tags and their respective values.