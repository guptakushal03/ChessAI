import time
from engine.move_generator import MoveGenerator


class ChessAI:
    """
    Chess AI using negamax with alpha-beta pruning and move ordering.

    Architecture
    ────────────
    evaluate()        Static board evaluation (material + piece-square tables)
    score_move()      Assigns a priority to a move for ordering
    order_moves()     Sorts moves: captures (MVV-LVA) > promotions > quiet
    negamax()         Recursive negamax with alpha-beta pruning
    get_best_move()   Root call; returns the best Move object
    """

    PIECE_VALUES = {
        'p': 100,
        'n': 320,
        'b': 330,
        'r': 500,
        'q': 900,
        'k': 20_000
    }

    PAWN_TABLE = [
        [  0,   0,   0,   0,   0,   0,   0,   0],
        [ 50,  50,  50,  50,  50,  50,  50,  50],
        [ 10,  10,  20,  30,  30,  20,  10,  10],
        [  5,   5,  10,  25,  25,  10,   5,   5],
        [  0,   0,   0,  20,  20,   0,   0,   0],
        [  5,  -5, -10,   0,   0, -10,  -5,   5],
        [  5,  10,  10, -20, -20,  10,  10,   5],
        [  0,   0,   0,   0,   0,   0,   0,   0],
    ]

    KNIGHT_TABLE = [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20,   0,   0,   0,   0, -20, -40],
        [-30,   0,  10,  15,  15,  10,   0, -30],
        [-30,   5,  15,  20,  20,  15,   5, -30],
        [-30,   0,  15,  20,  20,  15,   0, -30],
        [-30,   5,  10,  15,  15,  10,   5, -30],
        [-40, -20,   0,   5,   5,   0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50],
    ]

    BISHOP_TABLE = [
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10,   0,   0,   0,   0,   0,   0, -10],
        [-10,   0,   5,  10,  10,   5,   0, -10],
        [-10,   5,   5,  10,  10,   5,   5, -10],
        [-10,   0,  10,  10,  10,  10,   0, -10],
        [-10,  10,  10,  10,  10,  10,  10, -10],
        [-10,   5,   0,   0,   0,   0,   5, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20],
    ]

    ROOK_TABLE = [
        [  0,   0,   0,   0,   0,   0,   0,   0],
        [  5,  10,  10,  10,  10,  10,  10,   5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [  0,   0,   0,   5,   5,   0,   0,   0],
    ]

    QUEEN_TABLE = [
        [-20, -10, -10,  -5,  -5, -10, -10, -20],
        [-10,   0,   0,   0,   0,   0,   0, -10],
        [-10,   0,   5,   5,   5,   5,   0, -10],
        [ -5,   0,   5,   5,   5,   5,   0,  -5],
        [  0,   0,   5,   5,   5,   5,   0,  -5],
        [-10,   5,   5,   5,   5,   5,   0, -10],
        [-10,   0,   5,   0,   0,   0,   0, -10],
        [-20, -10, -10,  -5,  -5, -10, -10, -20],
    ]

    KING_MID_TABLE = [
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [ 20,  20,   0,   0,   0,   0,  20,  20],
        [ 20,  30,  10,   0,   0,  10,  30,  20],
    ]

    KING_END_TABLE = [
        [-50, -40, -30, -20, -20, -30, -40, -50],
        [-30, -20, -10,   0,   0, -10, -20, -30],
        [-30, -10,  20,  30,  30,  20, -10, -30],
        [-30, -10,  30,  40,  40,  30, -10, -30],
        [-30, -10,  30,  40,  40,  30, -10, -30],
        [-30, -10,  20,  30,  30,  20, -10, -30],
        [-30, -30,   0,   0,   0,   0, -30, -30],
        [-50, -30, -30, -30, -30, -30, -30, -50],
    ]

    PIECE_TABLES = {
        'p': PAWN_TABLE,
        'n': KNIGHT_TABLE,
        'b': BISHOP_TABLE,
        'r': ROOK_TABLE,
        'q': QUEEN_TABLE,
    }

    MATE_SCORE = 100_000

    def __init__(self, game_state, move_generator):
        self.gs = game_state
        self.mg = move_generator
        self.nodes_searched = 0


    def _is_endgame(self):
        """Simple endgame heuristic: both sides have ≤ 1 minor/major piece."""
        queens = 0
        minors = 0
        for row in self.gs.board:
            for piece in row:
                if piece in ('Q', 'q'):
                    queens += 1
                elif piece in ('R', 'r', 'B', 'b', 'N', 'n'):
                    minors += 1
        return queens == 0 or (queens <= 2 and minors <= 2)

    def _king_table(self):
        return self.KING_END_TABLE if self._is_endgame() else self.KING_MID_TABLE

    def evaluate(self):
        """
        Returns the board score in centipawns from WHITE's perspective.
        Positive = white is better. Negative = black is better.
        Components: material + piece-square bonus.
        """
        score = 0
        king_table = self._king_table()

        for row in range(8):
            for col in range(8):
                piece = self.gs.board[row][col]
                if piece == '.':
                    continue

                piece_type = piece.lower()
                material = self.PIECE_VALUES[piece_type]

                if piece_type == 'k':
                    table = king_table
                else:
                    table = self.PIECE_TABLES[piece_type]

                if piece.isupper():
                    pos = table[row][col]
                    score += material + pos
                else:
                    pos = table[7 - row][col]
                    score -= material + pos

        return score

    def score_move(self, move):
        """
        Higher score = try this move earlier.

        Priority layers (non-overlapping value ranges):
          1. Promotions            +10_000
          2. Captures (MVV-LVA)    0..9_000  (most valuable victim, least valuable attacker)
          3. Quiet moves           0
        """
        score = 0

        if move.is_pawn_promotion:
            score += 10_000

        if move.piece_captured != '.':
            victim  = self.PIECE_VALUES.get(move.piece_captured.lower(), 0)
            attacker = self.PIECE_VALUES.get(move.piece_moved.lower(),   0)
            score += 10 * victim - attacker

        return score

    def order_moves(self, moves):
        return sorted(moves, key=self.score_move, reverse=True)

    def negamax(self, depth, alpha, beta):
        """
        Negamax search. Score is always from the CURRENT player's perspective:
          positive  → current player is ahead
          negative  → current player is behind

        Alpha-beta pruning: prune subtrees that cannot affect the result.
        """
        self.nodes_searched += 1

        if depth == 0:
            raw = self.evaluate()
            return raw if self.gs.white_to_move else -raw

        moves = self.mg.get_legal_moves()

        if not moves:
            if self.mg.in_check():
                return -(self.MATE_SCORE + depth)
            return 0

        moves = self.order_moves(moves)

        best = -float('inf')

        for move in moves:
            self.gs.make_move(move)
            score = -self.negamax(depth - 1, -beta, -alpha)
            self.gs.undo_move()

            if score > best:
                best = score
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break

        return best


    def get_best_move(self, depth=3):
        """
        Return the best Move for the current side at the given search depth.
        Also prints a brief diagnostic line.
        """
        self.nodes_searched = 0
        t0 = time.time()

        moves = self.mg.get_legal_moves()
        if not moves:
            return None

        moves = self.order_moves(moves)

        best_move  = moves[0]
        best_score = -float('inf')
        alpha = -float('inf')
        beta  =  float('inf')

        for move in moves:
            self.gs.make_move(move)
            score = -self.negamax(depth - 1, -beta, -alpha)
            self.gs.undo_move()

            if score > best_score:
                best_score = score
                best_move  = move

            if score > alpha:
                alpha = score

        elapsed = time.time() - t0
        side    = "White" if self.gs.white_to_move else "Black"
        files   = "abcdefgh"
        mv_str  = (f"{files[best_move.start_col]}{8 - best_move.start_row}"
                   f"{files[best_move.end_col]}{8 - best_move.end_row}")

        score_display = best_score if self.gs.white_to_move else -best_score
        print(f"  [{side} AI] depth={depth}  move={mv_str}  "
              f"score={score_display:+d}cp  "
              f"nodes={self.nodes_searched:,}  time={elapsed:.2f}s")

        return best_move