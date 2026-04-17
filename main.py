import pygame
import rich
import os

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

#main programme
def main():
    clear_screen()
    pygame.mixer.init()
    pygame.mixer.music.load("test.flac")
    pygame.mixer.music.play()

    total_length = int(pygame.mixer.Sound("test.flac").get_length()*1000)
    print(format_time(total_length))

    #while pygame.mixer.music.get_busy():
    #    current_time = pygame.mixer.music.get_pos()
    #    print(current_time)
        #clear_screen()


if __name__ == "__main__":
    main()