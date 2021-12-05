import curses
import time


class screen:
    def __init__(self):
        self.screen = None
        self.current_row_idx = None

    def __enter__(self):
        self.screen = curses.initscr()
        curses.noecho

        return self

    def __exit__(self, exc_type, exc_value, exc_tr):
        curses.echo()
        curses.endwin()
        
        if exc_type is not None:
            print(exc_tr)

    def display_strings(self, rows: list):
        self.screen.clear()
        self.current_row_idx = 0

        for row in rows:
            print(row)
            self.screen.addstr(self.current_row_idx, 0, row)
            self.current_row_idx += 1

        self.screen.refresh()


if __name__ == '__main__':
    with screen() as scr:
        rows = list()
        rows.append('Hello')
        rows.append('Hello 2')
        rows.append('Hello 3')

        scr.display_strings(rows)
        time.sleep(10)
