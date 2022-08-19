from welcome_screen import animate
from main_menu import main_menu 

class Driver:
    def __init__(self):
        pass

    def main(self):
        animate()
        
        main_menu()

if __name__=='__main__':
    driver = Driver()
    driver.main()
