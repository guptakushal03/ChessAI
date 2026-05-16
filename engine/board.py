from engine.move import Move


class GameState:
    def __init__(self):
        # Uppercase = white, lowercase = black
        # r=rook, n=knight, b=bishop, q=queen, k=king, p=pawn
        self.board = [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]

        self.white_to_move = True

        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)

        self.en_passant_square = None
        self.castling_rights = {
            "wks": True,
            "wqs": True,
            "bks": True,
            "bqs": True
        }

        self.move_log = []


    def make_move(self, move):
        move.prev_castling_rights = self.castling_rights.copy()
        move.prev_en_passant_square = self.en_passant_square

        self.board[move.start_row][move.start_col] = "."
        self.board[move.end_row][move.end_col] = move.piece_moved

        self.move_log.append(move)

        if move.piece_moved == "K":
            self.white_king_pos = (move.end_row, move.end_col)
            self.castling_rights["wks"] = False
            self.castling_rights["wqs"] = False
        elif move.piece_moved == "k":
            self.black_king_pos = (move.end_row, move.end_col)
            self.castling_rights["bks"] = False
            self.castling_rights["bqs"] = False

        elif move.piece_moved == "R":
            if move.start_row == 7:
                if move.start_col == 0:
                    self.castling_rights["wqs"] = False
                elif move.start_col == 7:
                    self.castling_rights["wks"] = False
        elif move.piece_moved == "r":
            if move.start_row == 0:
                if move.start_col == 0:
                    self.castling_rights["bqs"] = False
                elif move.start_col == 7:
                    self.castling_rights["bks"] = False

        if move.piece_captured == "R":
            if move.end_row == 7:
                if move.end_col == 0:
                    self.castling_rights["wqs"] = False
                elif move.end_col == 7:
                    self.castling_rights["wks"] = False
        elif move.piece_captured == "r":
            if move.end_row == 0:
                if move.end_col == 0:
                    self.castling_rights["bqs"] = False
                elif move.end_col == 7:
                    self.castling_rights["bks"] = False

        if move.is_castle:
            if move.end_col == 6:
                self.board[move.end_row][5] = self.board[move.end_row][7]
                self.board[move.end_row][7] = "."
            else:
                self.board[move.end_row][3] = self.board[move.end_row][0]
                self.board[move.end_row][0] = "."

        if move.is_en_passant:
            self.board[move.start_row][move.end_col] = "."

        if move.piece_moved in ("P", "p") and abs(move.end_row - move.start_row) == 2:
            self.en_passant_square = ((move.start_row + move.end_row) // 2, move.end_col)
        else:
            self.en_passant_square = None

        if move.is_pawn_promotion:
            if move.promotion_piece:
                self.board[move.end_row][move.end_col] = move.promotion_piece
            else:
                self.board[move.end_row][move.end_col] = "Q" if move.piece_moved == "P" else "q"

        self.white_to_move = not self.white_to_move


    def undo_move(self):
        if not self.move_log:
            return

        move = self.move_log.pop()

        self.board[move.start_row][move.start_col] = move.piece_moved

        if move.is_en_passant:
            self.board[move.end_row][move.end_col] = "."
            self.board[move.start_row][move.end_col] = move.piece_captured
        else:
            self.board[move.end_row][move.end_col] = move.piece_captured

        if move.piece_moved == "K":
            self.white_king_pos = (move.start_row, move.start_col)
        elif move.piece_moved == "k":
            self.black_king_pos = (move.start_row, move.start_col)

        if move.is_castle:
            if move.end_col == 6:
                self.board[move.end_row][7] = self.board[move.end_row][5]
                self.board[move.end_row][5] = "."
            else:
                self.board[move.end_row][0] = self.board[move.end_row][3]
                self.board[move.end_row][3] = "."

        self.castling_rights = move.prev_castling_rights
        self.en_passant_square = move.prev_en_passant_square

        self.white_to_move = not self.white_to_move