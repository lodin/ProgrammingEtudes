import curses
from collections import namedtuple

Point = namedtuple("Point", ["row", "col"])
Vector = namedtuple("Vector", ["row", "col"])

class Command:
    """
    Stores the valid user input commands
    """
    MOVE_KEYS = ['KEY_LEFT', 'KEY_RIGHT', 'KEY_UP', 'KEY_DOWN']
    
    @staticmethod
    def cursor_transform_for_command(key):
        """
        Returns a Vector representing how the cursor should be transformed 
        """
        if key == 'KEY_LEFT':
            return Vector(row=0, col=-1)
        elif key == 'KEY_RIGHT':
            return Vector(row=0, col=1)
        elif key == 'KEY_UP':
            return Vector(row=-1, col=0)
        elif key == 'KEY_DOWN':
            return Vector(row=1, col=0)
        else:
            raise ValueError("{} is not a valid key".format(key))


class GameOfLife:
    """
    An instance of the game of life.
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr
        origin = Point(row=0, col=0)
        self.start()

    def get_cursor_position(self) -> Point:
        row, column = self.stdscr.getyx()
        return Point(row=row, col=column)

    def start(self):
        """
        Starts the Game of Life
        """
        continue_execution = True
        while continue_execution:
            input_key = self.stdscr.getkey()
            continue_execution = self.dispatch_user_command(input_key)

    def dispatch_user_command(self, input_key):
        """
        Takes a user input and decides what to do about it
        """
        if input_key == 'q':
            return False
        elif input_key in Command.MOVE_KEYS:
            transform = Command.cursor_transform_for_command(input_key)
            pos = self.get_cursor_position()
            self.stdscr.move(pos.row + transform.row, pos.col + transform.col)
        else:
            self.stdscr.addstr(input_key)

        return True



if __name__ == '__main__':
    curses.wrapper(GameOfLife)
       
