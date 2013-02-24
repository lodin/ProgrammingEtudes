
"""
TODOS:
    - Add a draw screen function to print out statistics
    - Add infinite scroll
    - Do trajectory modifications (clear trajectory)
    - Actually write the game of life stuff
"""
import curses

from collections import namedtuple
from functools import wraps

Point = namedtuple("Point", ["row", "col"])
Vector = namedtuple("Vector", ["row", "col"])

CELL_CHAR = ord("o")


class Command:
    """
    Stores the valid user input commands
    """
    MOVE_KEYS = ['KEY_LEFT', 'KEY_RIGHT', 'KEY_UP', 'KEY_DOWN']
    TOGGLE_INSERT_MODE_KEY = ' '
    
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

class Mode:
    INSERT = 1
    NORMAL = 2

class Board:
    """ 
    A game board that tracks all living cells
    cell_positions is a map keyed by Point objects
    """
    def __init__(self, initial_positions=[]):
        self.cell_positions = {}
        for p in initial_positions:
           self.add_cell(p)
 
    def cell_at(self, point):
        return self.cell_positions.get(point, False)

    def add_cell(self, point) -> bool:
        """
        Add a cell at <point> :: Point.
        Returns:
            True on sucess
            False otherwise
        """
        if not self.cell_at(point):
            self.cell_positions[point] = True
            return True
        else:
            return False

    def remove_cell(self, point) -> bool:
        """
        Remove the cell at point :: Point.
        Returns:
            True on success
            False otherwise
        """
        if self.cell_at(point):
            del self.cell_positions[point]
            return True
        else:
            return False
   
    def get_cell_count(self):
        return len(self.cell_positions)
    cell_count = property(fget=get_cell_count)



class GameOfLife:
    """
    An instance of the game of life.
    """
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.mode = Mode.NORMAL
        origin = Point(row=0, col=0)
        self.insert_tranjectory = Vector(row=0, col=0)
        self.start()
        board = Board()

    # Declare cursor_position as a property
    def get_cursor_position(self) -> Point:
        row, column = self.stdscr.getyx()
        return Point(row=row, col=column)
    cursor_position = property(fget=get_cursor_position)

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
            try:
                self.stdscr.move(pos.row + transform.row, pos.col + transform.col)
            except curses.error as e:
                # We're probably just trying to move off the side of the screen
                pass
            if self.mode == Mode.INSERT:
                self.insert_cell(self.cursor_position)
            else:
                pass
        elif input_key == Command.TOGGLE_INSERT_MODE_KEY:
            if self.mode == Mode.INSERT:
                self.mode = Mode.NORMAL
            else:
                self.mode = Mode.INSERT
                pos = self.get_cursor_position()
                self.stdscr.addch(CELL_CHAR)
                self.stdscr.move(pos.row, pos.col)
        else:
            self.stdscr.addstr(input_key)

        return True

    def insert_cell(self, position):
        # Insert into our board
        self.board.add_cell(position)

        # Update the display
        old_position = self.cursor_position
        self.stdscr.move(position.row, position.col)
        self.stdscr.addch(CELL_CHAR)
        self.stdscr.move(old_position.row, old_position.col)

if __name__ == '__main__':
    #curses.wrapper(GameOfLife)
    initial_coordinates = [(1,1), (2,2), (3,3)]
    initial_positions = [Point(x,y) for x,y in initial_coordinates]
    b = Board(initial_positions)
    b.remove_cell(Point(1,1))
    print(b.cell_positions)

