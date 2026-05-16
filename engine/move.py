class Move:
    def __init__(self, start, end, board):
        self.start_row, self.start_col = start
        self.end_row, self.end_col = end

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        self.is_pawn_promotion = False
        self.is_en_passant = False
        self.is_castle = False

        self.prev_castling_rights = None
        self.prev_en_passant_square = None

        self.promotion_piece = None