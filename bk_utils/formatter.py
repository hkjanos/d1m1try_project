import os

class Format:
    # This class is for formatting output - currently for the test environment.
    # Some formats are currently not used, but may be used later.
    # Big thanks for Blender for making this code available. :)
    # source: https://svn.blender.org/svnroot/bf-blender/trunk/blender/build_files/scons/tools/bcolors.py
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def passed(self, input):
        print(f"{self.OKGREEN}{str(input)}{self.ENDC}")

    def failed(self, input):
        print(f"{self.FAIL}{str(input)}{self.ENDC}")

    def bold(self, input):
        print(f"{self.BOLD}{str(input)}{self.ENDC}")

    def clear_screen(self):
        # for windows:
        if os.name == 'nt':
            os.system('cls')

        else:
            os.system('clear')

    def color_screen(self, onoff: bool):
        if onoff:
            os.system('color 02' if os.name == 'nt' else 'setterm --foreground green')
        else:
            os.system('color 08' if os.name == 'nt' else 'setterm --foreground white')
