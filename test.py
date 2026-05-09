import rhythmsync.main as rs
import sys
import termios
import tty
import select

fd = sys.stdin.fileno()
old = termios.tcgetattr(fd)

try:
    tty.setcbreak(fd)

    while True:
        ready, _, _ = select.select([sys.stdin], [], [], 0)

        if ready:
            key = sys.stdin.read(1)

            if key == "q":
                break

            print(f"key: {repr(key)}")

        #rs.run_player("test.flac")
        print("⏸")

finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old)