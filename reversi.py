import random
import dearpygui.dearpygui as dpg

# Constants
BOARD_SIZE = 8
WHITE = 1
BLACK = -1
EMPTY = 0
CELL_SIZE = 60
WINDOW_PADDING = 20
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

class ReversiGame:
    def __init__(self):
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_turn = BLACK
        self.pvc_mode = False

        # Initialize starting pieces
        self.board[3][3], self.board[4][4] = WHITE, WHITE
        self.board[3][4], self.board[4][3] = BLACK, BLACK

        # Dear PyGui Setup
        dpg.create_context()
        dpg.create_viewport(title="Reversi Game", width=BOARD_SIZE * CELL_SIZE + 200, height=BOARD_SIZE * CELL_SIZE + 160)  # Increased height

        # Main drawing area for the game board
        with dpg.window(label="Game Board", width=BOARD_SIZE * CELL_SIZE, height=BOARD_SIZE * CELL_SIZE, pos=(WINDOW_PADDING, WINDOW_PADDING), tag="game_board_window"):
            with dpg.drawlist(width=BOARD_SIZE * CELL_SIZE, height=BOARD_SIZE * CELL_SIZE, tag="board"):
                self.draw_board()

        # Control Panel (made taller)
        with dpg.window(label="Control Panel", width=200, height=160, pos=(BOARD_SIZE * CELL_SIZE + WINDOW_PADDING, WINDOW_PADDING)):  # Increased height
            dpg.add_button(label="Player vs Computer", callback=self.start_pvc)
            dpg.add_button(label="Player vs Player", callback=self.start_pvp)
            dpg.add_button(label="Reset Game", callback=self.reset_game)
            dpg.add_text("Current Player:", tag="current_player_label")
            dpg.add_text("Black", color=(0, 0, 0), tag="current_player")  # This text will be updated dynamically

        # Handler Registry for mouse clicks
        with dpg.handler_registry():
            dpg.add_mouse_click_handler(callback=self.handle_click)  # Register global click handler

        # Set the game board as the primary window
        dpg.set_primary_window("game_board_window", True)

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def start_pvc(self):
        self.pvc_mode = True
        self.reset_game()

    def start_pvp(self):
        self.pvc_mode = False
        self.reset_game()

    def reset_game(self):
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.board[3][3], self.board[4][4] = WHITE, WHITE
        self.board[3][4], self.board[4][3] = BLACK, BLACK
        self.current_turn = BLACK
        self.draw_board()
        self.update_current_player_label()

    def draw_board(self):
        dpg.delete_item("board", children_only=True)

        # Draw grid and pieces
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                color = (0, 128, 0) if (x + y) % 2 == 0 else (34, 139, 34)
                dpg.draw_rectangle((x * CELL_SIZE, y * CELL_SIZE), ((x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE),
                                   fill=color, parent="board")

                if self.board[x][y] == BLACK:
                    dpg.draw_circle((x * CELL_SIZE + CELL_SIZE / 2, y * CELL_SIZE + CELL_SIZE / 2),
                                    CELL_SIZE / 2 - 5, color=(0, 0, 0), fill=(0, 0, 0), parent="board")
                elif self.board[x][y] == WHITE:
                    dpg.draw_circle((x * CELL_SIZE + CELL_SIZE / 2, y * CELL_SIZE + CELL_SIZE / 2),
                                    CELL_SIZE / 2 - 5, color=(255, 255, 255), fill=(255, 255, 255), parent="board")

    def handle_click(self, sender, app_data):
        # Get the mouse position
        mouse_x, mouse_y = dpg.get_mouse_pos()
        x, y = int(mouse_x // CELL_SIZE), int(mouse_y // CELL_SIZE)

        # Only handle clicks within the board
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:  # Ensure clicks are within the board bounds
            if self.is_valid_move(x, y, self.current_turn):
                self.place_piece(x, y, self.current_turn)
                self.switch_turn()
                self.draw_board()
                self.update_current_player_label()

                # Check if game is over
                if not self.has_valid_move(self.current_turn) and not self.has_valid_move(-self.current_turn):
                    self.end_game()
                elif self.pvc_mode and self.current_turn == WHITE:
                    self.computer_move()
                    self.switch_turn()
                    self.draw_board()
                    self.update_current_player_label()

    def is_valid_move(self, x, y, color):
        if self.board[x][y] != EMPTY:
            return False
        for dx, dy in DIRECTIONS:
            if self.can_flip(x, y, dx, dy, color):
                return True
        return False

    def has_valid_move(self, color):
        return any(self.is_valid_move(x, y, color) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE))

    def can_flip(self, x, y, dx, dy, color):
        nx, ny = x + dx, y + dy
        has_opponent_piece = False
        while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
            if self.board[nx][ny] == -color:
                has_opponent_piece = True
            elif self.board[nx][ny] == color:
                return has_opponent_piece
            else:
                break
            nx += dx
            ny += dy
        return False

    def place_piece(self, x, y, color):
        self.board[x][y] = color
        for dx, dy in DIRECTIONS:
            if self.can_flip(x, y, dx, dy, color):
                self.flip_pieces(x, y, dx, dy, color)

    def flip_pieces(self, x, y, dx, dy, color):
        nx, ny = x + dx, y + dy
        while self.board[nx][ny] == -color:
            self.board[nx][ny] = color
            nx += dx
            ny += dy

    def switch_turn(self):
        self.current_turn = WHITE if self.current_turn == BLACK else BLACK

    def computer_move(self):
        valid_moves = [(x, y) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE) if self.is_valid_move(x, y, WHITE)]
        if valid_moves:
            x, y = random.choice(valid_moves)
            self.place_piece(x, y, WHITE)

    def update_current_player_label(self):
        # Determine the current player text and color
        player_text = "Black's turn" if self.current_turn == BLACK else "White's turn"
        player_color = (0, 0, 0) if self.current_turn == BLACK else (255, 255, 255)
        background_color = (255, 255, 255) if self.current_turn == BLACK else (0, 0, 0)

        # Update the text of the current player label
        dpg.set_value("current_player", player_text)

        # Update the color of the label text
        dpg.configure_item("current_player", color=player_color)

        # Change the background color of the current player text for better contrast
        dpg.configure_item("current_player", fill=background_color)

    def end_game(self):
        black_count = sum(row.count(BLACK) for row in self.board)
        white_count = sum(row.count(WHITE) for row in self.board)
        if black_count > white_count:
            winner = "Black wins!"
        elif white_count > black_count:
            winner = "White wins!"
        else:
            winner = "It's a tie!"
        dpg.set_value("current_player", f"Game Over: {winner}")

if __name__ == "__main__":
    game = ReversiGame()
