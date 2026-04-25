RhythmSync
CLI audio player that plays music while displaying synchronized lyrics (LRC).

command list:
help - Lists all available commands.
clear - Clears the terminal.
play {par} {path} - Plays the audio file located at the specified {path}.
    If {par} is "-r", the audio file plays in repeat until stopped.
    If {par} is "-d" and {path} is a directory, the audio files of given directory play in alphabetic order.
    If {par} is "-ds" and {path} is a directory, the audio files of given directory play in shuffle.
    If {par} is omitted, the audio file plays once.
info {path} {tags} - Displays metadata for the file at {path}.
    If {tags} is provided (separate them with space for multiple tags), shows only those specific tags and their respective values.
    If {tags} is omitted, shows all available tags and their respective values.


Supported music formats:
mp3, flac, wav, ogg