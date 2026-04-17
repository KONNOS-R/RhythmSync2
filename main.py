import pygame
import os

#clear the terminal
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

#main programme
def main():
    clear_screen()
    pygame.mixer.init()
    pygame.mixer.music.load("test.flac")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        current_time = pygame.mixer.music.get_pos()
        print(current_time)
        #clear_screen()


if __name__ == "__main__":
    main()