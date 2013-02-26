
"""
TODOS:
    - Add a draw screen function to print out statistics
    - Add infinite scroll
    - Actually write the game of life stuff
"""
import curses

from collections import namedtuple
from functools import wraps

Point = namedtuple("Point", ["row", "col"])
Vector = namedtuple("Vector", ["row", "col"])

CELL_CHAR = ord("o")
BLANK_CHAR= ord(" ")


class Command:
    """
    Stores the valid user input commands
    """
    MOVE_KEYS = ['KEY_LEFT', 'KEY_RIGHT', 'KEY_UP', 'KEY_DOWN']
    TOGGLE_INSERT_MODE_KEY = 't'
    INSERT_CELL= 'c'
    DELETE_CELL = 'x'
    QUIT = 'q'
    REFRESH = 'r'
    STEP = ' '
    
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
            raise ValueError("{} does not map to a transformation".format(key))

class Mode:
    INSERT = 1
    NORMAL = 2

class Board:
    """ 
    A game board that tracks all living cells
    cell_positions is a map keyed by Point objects
    """
    NEIGHBOUR_TRANFORMS = [Vector(-1, -1), Vector(-1, 0), Vector(-1, 1), 
                           Vector(0, -1), Vector(0, 1),
                           Vector(1, -1),  Vector(1, 0), Vector(1, 1)]

    def __init__(self, initial_positions=[]):
        self.cell_positions = {}
        for p in initial_positions:
           self.add_cell(p)

    @property
    def cells(self):
        return self.cell_positions.keys()

    @property
    def cell_count(self):
        return len(self.cell_positions)
 
    @property
    def empty_neighbour_set(self):
        all_neighbours = [Point(p.row+v.row, p.col+v.col) for p in self.cells for v in Board.NEIGHBOUR_TRANFORMS] 
        return set([n for n in all_neighbours if not self.cell_at(n)])

    def cell_at(self, point):
        return self.cell_positions.get(point, False)

    def add_cell(self, point) -> bool:
        """
        Add a cell at <point> :: Point.
        Returns:
            True on success
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

    def live_neighbours_count(self, point):
        all_neighbours = [Point(point.row+v.row, point.col+v.col) for v in Board.NEIGHBOUR_TRANFORMS] 
        return len([n for n in all_neighbours if self.cell_at(n)])
   
    def step(self):
        # Create a new empty board
        next_cell_positions = {}
        # For each live cell: 2/3 neighbours = live. Else die.
        for cell_position in self.cells:
            neighbour_count = self.live_neighbours_count(cell_position)
            if neighbour_count == 2 or neighbour_count == 3:
                next_cell_positions[cell_position] = True
        # For each empty plot: 3 live neighbours = live. Else same.
        for empty_position in self.empty_neighbour_set:
            neighbour_count = self.live_neighbours_count(empty_position)
            if neighbour_count == 3:
                next_cell_positions[empty_position] = True

        self.cell_positions = next_cell_positions

class Screen:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.max_row, self.max_col = self.stdscr.getmaxyx()
        self.max_row -= 1
        self.max_col -= 1
        self.origin = Point(0,0)

    # Declare cursor_position as a property
    @property
    def cursor_position(self) -> Point:
        row, column = self.stdscr.getyx()
        return Point(row=row, col=column)

    def get_input_key(self):
        return self.stdscr.getkey()

    def move_cursor(self, row_delta, col_delta):
        """ 
        Move the cursor
        """
        pos = self.cursor_position
        try:
            self.stdscr.move(pos.row + row_delta, pos.col + col_delta)
        except curses.error:
            return False

        return True

    def add_cell(self, point):
        if point.row > self.max_row or point.col > self.max_col or point.row < 0 or point.col < 0:
            return
        old_position = self.cursor_position
        self.stdscr.move(point.row, point.col)
        self.stdscr.addch(CELL_CHAR)
        self.stdscr.move(old_position.row, old_position.col)

    def remove_cell(self, point):
        old_position = self.cursor_position
        self.stdscr.move(point.row, point.col)
        self.stdscr.addch(BLANK_CHAR)
        self.stdscr.move(old_position.row, old_position.col)

    def save_cursor(self):
        self.saved_cursor = self.cursor_position

    def restore_cursor(self):
        self.stdscr.move(self.saved_cursor.row, self.saved_cursor.col)

    def clear(self):
        self.stdscr.erase()

class GameOfLife:
    """
    An instance of the game of life.
    """
    def __init__(self, stdscr):
        # Do initializations
        self.screen = Screen(stdscr)
        self.board = Board([Point(1,1),Point(2,2)])
        self.mode = Mode.NORMAL
        self.origin = Point(row=0, col=0)
        # Start the game
        self.start()

    def start(self):
        """
        Starts the Game of Life
        """
        self.refresh_screen()
        continue_execution = True
        while continue_execution:
            input_key = self.screen.get_input_key()
            continue_execution = self.dispatch_user_command(input_key)

    def dispatch_user_command(self, input_key):
        """
        Takes a user input and decides what to do about it
        """
        if input_key == Command.QUIT:
            return False
        elif input_key in Command.MOVE_KEYS:
            transform = Command.cursor_transform_for_command(input_key)
            if self.mode == Mode.INSERT: self.add_cell(self.screen.cursor_position)
            self.screen.move_cursor(row_delta=transform.row, col_delta=transform.col)
        elif input_key == Command.INSERT_CELL:
            self.add_cell(self.screen.cursor_position)
        elif input_key == Command.DELETE_CELL:
            self.remove_cell(self.screen.cursor_position)
        elif input_key == Command.REFRESH:
            self.screen.redraw()
        elif input_key == Command.TOGGLE_INSERT_MODE_KEY:
            self.mode = Mode.INSERT if self.mode == Mode.NORMAL else Mode.NORMAL
        elif input_key == Command.STEP:
            self.step()
        else:
            pass

        return True

    def add_cell(self, position):
        self.board.add_cell(position)
        self.screen.add_cell(position)

    def remove_cell(self, position):
        self.board.remove_cell(position)
        self.screen.remove_cell(position)

    def refresh_screen(self):
        pos = self.screen.save_cursor()
        self.screen.clear()
        for point in self.board.cells:
            self.screen.add_cell(point)
        self.screen.restore_cursor()

    def step(self):
        self.board.step()
        self.refresh_screen()

if __name__ == '__main__':
    curses.wrapper(GameOfLife)
