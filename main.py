import boinccmd_parser as parser
from screen_handler import screen
from boinc_manager import TaskManager
from time import sleep


if __name__ == '__main__':
    manager = TaskManager()

    with screen() as scr:
        for _ in range(100):
            manager.synchronise(parser)
            content = manager.get_screen_content()
            scr.display_strings(content)
            sleep(10)
