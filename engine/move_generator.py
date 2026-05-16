from engine.move import Move


class MoveGenerator:
    def __init__(self, game_state):
        self.gs = game_state
        self.board = game_state.board

        self.move_functions = {
            "p": self.get_pawn_moves,
            "r": self.get_rook_moves,
            "n": self.get_knight_moves,
            "b": self.get_bishop_moves,
            "q": self.get_queen_moves,
            "k": self.get_king_moves
        }


    def get_all_moves(self):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece == ".":
                    continue
                if (piece.isupper() and self.gs.white_to_move) or \
                   (piece.islower() and not self.gs.white_to_move):
                    self.move_functions[piece.lower()](row, col, moves)
        return moves


    def get_pawn_moves(self, row, col, moves):
        piece = self.board[row][col]
        is_white = piece.isupper()

        direction  = -1 if is_white else 1
        start_row  = 6  if is_white else 1
        promo_row  = 0  if is_white else 7
        enemy      = str.islower if is_white else str.isupper

        if 0 <= row + direction < 8 and self.board[row + direction][col] == ".":
            move = Move((row, col), (row + direction, col), self.board)
            if row + direction == promo_row:
                move.is_pawn_promotion = True
            moves.append(move)

            if row == start_row and self.board[row + 2 * direction][col] == ".":
                moves.append(Move((row, col), (row + 2 * direction, col), self.board))

        if 0 <= row + direction < 8:
            for dc in (-1, 1):
                if 0 <= col + dc < 8:
                    target = self.board[row + direction][col + dc]
                    if target != "." and enemy(target):
                        move = Move((row, col), (row + direction, col + dc), self.board)
                        if row + direction == promo_row:
                            move.is_pawn_promotion = True
                        moves.append(move)

        if self.gs.en_passant_square:
            ep_row, ep_col = self.gs.en_passant_square
            if row + direction == ep_row and abs(col - ep_col) == 1:
                ep_move = Move((row, col), (ep_row, ep_col), self.board)
                ep_move.is_en_passant = True
                ep_move.piece_captured = "p" if is_white else "P"
                moves.append(ep_move)


    def get_rook_moves(self, row, col, moves):
        self.get_sliding_moves(row, col, moves, [(-1, 0), (1, 0), (0, -1), (0, 1)])


    def get_knight_moves(self, row, col, moves):
        is_white = self.board[row][col].isupper()
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = self.board[r][c]
                if target == "." or target.isupper() != is_white:
                    moves.append(Move((row, col), (r, c), self.board))


    def get_bishop_moves(self, row, col, moves):
        self.get_sliding_moves(row, col, moves, [(-1,-1),(-1,1),(1,-1),(1,1)])


    def get_queen_moves(self, row, col, moves):
        self.get_sliding_moves(row, col, moves,
            [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)])


    def get_king_moves(self, row, col, moves):
        is_white = self.board[row][col].isupper()
        for dr, dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = self.board[r][c]
                if target == "." or target.isupper() != is_white:
                    moves.append(Move((row, col), (r, c), self.board))

    def get_castling_moves(self, row, col, moves):
        """
        Generate castling moves. Caller must already have verified the king is
        not in check (to avoid the infinite recursion: in_check → get_all_moves
        → get_castling_moves → in_check).

        Rules enforced here:
          - Squares between king and rook must be empty
          - Squares the king passes through must not be attacked
        """
        cr = self.gs.castling_rights

        if self.gs.white_to_move:
            if cr["wks"] and \
               self.board[row][5] == "." and self.board[row][6] == "." and \
               not self.is_square_attacked(row, 5) and not self.is_square_attacked(row, 6):
                m = Move((row, col), (row, 6), self.board)
                m.is_castle = True
                moves.append(m)
            if cr["wqs"] and \
               self.board[row][1] == "." and self.board[row][2] == "." and self.board[row][3] == "." and \
               not self.is_square_attacked(row, 3) and not self.is_square_attacked(row, 2):
                m = Move((row, col), (row, 2), self.board)
                m.is_castle = True
                moves.append(m)
        else:
            if cr["bks"] and \
               self.board[row][5] == "." and self.board[row][6] == "." and \
               not self.is_square_attacked(row, 5) and not self.is_square_attacked(row, 6):
                m = Move((row, col), (row, 6), self.board)
                m.is_castle = True
                moves.append(m)

            if cr["bqs"] and \
               self.board[row][1] == "." and self.board[row][2] == "." and self.board[row][3] == "." and \
               not self.is_square_attacked(row, 3) and not self.is_square_attacked(row, 2):
                m = Move((row, col), (row, 2), self.board)
                m.is_castle = True
                moves.append(m)


    def get_sliding_moves(self, row, col, moves, directions):
        is_white = self.board[row][col].isupper()
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = self.board[r][c]
                if target == ".":
                    moves.append(Move((row, col), (r, c), self.board))
                else:
                    if target.isupper() != is_white:
                        moves.append(Move((row, col), (r, c), self.board))
                    break
                r += dr
                c += dc


    def is_square_attacked(self, row, col):
        """Return True if the opponent can move to (row, col) on their next turn."""
        self.gs.white_to_move = not self.gs.white_to_move
        opponent_moves = self.get_all_moves()
        self.gs.white_to_move = not self.gs.white_to_move
        return any(m.end_row == row and m.end_col == col for m in opponent_moves)


    def in_check(self):
        """Return True if the side currently to move has their king in check."""
        if self.gs.white_to_move:
            r, c = self.gs.white_king_pos
        else:
            r, c = self.gs.black_king_pos
        return self.is_square_attacked(r, c)


    def get_legal_moves(self):
        """
        Return only moves that leave the moving side's king out of check.

        Castling is generated here (not in get_king_moves) to avoid the
        recursive loop: get_king_moves → get_castling_moves → in_check →
        is_square_attacked → get_all_moves → get_king_moves → ...

        Flow after make_move:
          white_to_move has already been flipped, so we flip it back temporarily
          to let in_check() evaluate the side that just moved.
        """
        moves = self.get_all_moves()

        if not self.in_check():
            if self.gs.white_to_move:
                king_row, king_col = self.gs.white_king_pos
            else:
                king_row, king_col = self.gs.black_king_pos
            self.get_castling_moves(king_row, king_col, moves)

        legal_moves = []
        for move in moves:
            self.gs.make_move(move)
            self.gs.white_to_move = not self.gs.white_to_move
            if not self.in_check():
                legal_moves.append(move)
            self.gs.white_to_move = not self.gs.white_to_move
            self.gs.undo_move()

        return legal_moves


    def get_game_status(self):
        """
        FIX 9: was completely missing.
        Returns 'checkmate', 'stalemate', or 'ongoing'.
        Must be called before the side to move makes their move.
        """
        if self.get_legal_moves():
            return "ongoing"
        return "checkmate" if self.in_check() else "stalemate"