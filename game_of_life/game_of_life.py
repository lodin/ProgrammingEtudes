"""
TODOS:
    - Add a draw screen function to print out statistics
    - Think of a better way to save/restore cursor
"""

from board import Board
from screen import Screen
from datastructures import Point, Vector


class Command:
    """
    Stores the valid user input commands
    """
    MOVE_KEYS = ['KEY_LEFT', 'KEY_RIGHT', 'KEY_UP', 'KEY_DOWN']

    INSERT_MODE = 'i'
    NORMAL_MODE = 'n'
    PAN_MODE = 'p'
    RECORD_MODE = 'r'

    INSERT_CELL= 'c'
    DELETE_CELL = 'x'
    QUIT = 'q'
    STEP = ' '
    SAVE_BOARD = 's'
    LOAD_BOARD = 'l'
    
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
    PAN = 3
    RECORD = 4


class GameOfLife:
    """
    An instance of the game of life.
    """
    SAVE_FILENAME = "saved_game.gol"
    RECORD_FILENAME = "recorded_game.gol"

    def __init__(self, stdscr):
        self.screen = Screen(stdscr)
        self.board = Board()
        self.mode = Mode.NORMAL
        self.origin = Point(row=0, col=0)
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
        elif input_key in Command.MOVE_KEYS and self.mode == Mode.NORMAL:
            transform = Command.cursor_transform_for_command(input_key)
            self.screen.move_cursor(row_delta=transform.row, col_delta=transform.col)
        elif input_key in Command.MOVE_KEYS and self.mode == Mode.INSERT:
            transform = Command.cursor_transform_for_command(input_key)
            self.add_cell(self.screen.cursor_position)
            self.screen.move_cursor(row_delta=transform.row, col_delta=transform.col)
        elif input_key in Command.MOVE_KEYS and self.mode == Mode.PAN:
            transform = Command.cursor_transform_for_command(input_key)
            self.screen.move_origin(transform.row, transform.col)
            self.refresh_screen()
        elif input_key == Command.INSERT_CELL:
            self.add_cell(self.screen.cursor_position)
        elif input_key == Command.DELETE_CELL:
            self.remove_cell(self.screen.cursor_position)
        elif input_key == Command.INSERT_MODE:
            self.mode = Mode.INSERT
        elif input_key == Command.NORMAL_MODE:
            self.mode = Mode.NORMAL
        elif input_key == Command.PAN_MODE:
            self.mode = Mode.PAN
        elif input_key == Command.RECORD_MODE:
            self.mode = Mode.RECORD
        elif input_key == Command.STEP and self.mode == Mode.RECORD:
            self.record()
            self.step()
        elif input_key == Command.STEP:
            self.step()
        elif input_key == Command.SAVE_BOARD:
            self.save()
        elif input_key == Command.LOAD_BOARD:
            self.load()
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
        self.screen.save_cursor()
        self.screen.clear()
        for point in self.board.cells:
            self.screen.add_cell(point)
        self.screen.restore_cursor()

    def step(self):
        self.board.step()
        self.refresh_screen()

    def save(self):
        with open(self.SAVE_FILENAME, mode='w') as save_fhandle:
            board_state = self.board.serialize_board()
            save_fhandle.write(board_state)

    def load(self):
        with open(self.SAVE_FILENAME) as save_fhandle:
            serialized_board_state = save_fhandle.readline()
            self.board.load_serialized_board(serialized_board_state)
        self.refresh_screen()

    def record(self):
       with open(self.RECORD_FILENAME, mode='a') as record_fhandle:
            board_state = self.board.serialize_board()
            record_fhandle.write(board_state + '\n')


if __name__ == '__main__':
    curses.wrapper(GameOfLife)
