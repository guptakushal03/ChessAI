import pygame
import sys
from engine.board import GameState
from engine.move_generator import MoveGenerator
from engine.ai import ChessAI

WIDTH = HEIGHT = 640
DIMENSION = 8
SQ = WIDTH // DIMENSION

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess AI")

IMAGES = {}

def load_images():
    mapping = {
        "P":"wp.png",
        "R":"wr.png",
        "N":"wn.png",
        "B":"wb.png",
        "Q":"wq.png",
        "K":"wk.png",

        "p":"bp.png",
        "r":"br.png",
        "n":"bn.png",
        "b":"bb.png",
        "q":"bq.png",
        "k":"bk.png"
    }

    for piece,file in mapping.items():
        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load(f"assets/{file}"),
            (SQ,SQ)
        )


def draw_board():
    colors = [(238,238,210),(118,150,86)]

    for r in range(8):
        for c in range(8):
            color = colors[(r+c)%2]
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(c*SQ,r*SQ,SQ,SQ)
            )


def draw_pieces(board, gs=None, mg=None):

    # Highlight checked king
    if gs and mg and mg.in_check():

        king = "K" if gs.white_to_move else "k"

        for rr in range(8):
            for cc in range(8):
                if board[rr][cc] == king:

                    glow = pygame.Surface((SQ,SQ))
                    glow.set_alpha(120)
                    glow.fill((255,60,60))   # red warning
                    screen.blit(
                        glow,
                        (cc*SQ, rr*SQ)
                    )

    # Draw pieces
    for r in range(8):
        for c in range(8):
            piece = board[r][c]

            if piece != ".":
                screen.blit(
                    IMAGES[piece],
                    pygame.Rect(
                        c*SQ,
                        r*SQ,
                        SQ,
                        SQ
                    )
                )


def highlight_square(selected, legal_moves=None):
    if not selected:
        return

    r,c = selected

    # selected piece square
    s = pygame.Surface((SQ,SQ))
    s.set_alpha(90)
    s.fill((50,150,255))
    screen.blit(s,(c*SQ,r*SQ))

    # legal destinations
    if legal_moves:
        dot = pygame.Surface((SQ,SQ))
        dot.set_alpha(90)
        dot.fill((255,215,0))

        for move in legal_moves:
            if move.start_row==r and move.start_col==c:
                screen.blit(
                    dot,
                    (move.end_col*SQ,
                     move.end_row*SQ)
                )


def draw_game(gs, selected, legal_moves, in_check=False):
    draw_board()
    highlight_square(selected, legal_moves)
    draw_pieces(gs.board)

    if in_check:
        font = pygame.font.SysFont("arial",36,True)

        text = font.render(
            "CHECK!",
            True,
            (220,30,30)
        )

        box = pygame.Surface((180,50))
        box.set_alpha(210)
        box.fill((255,240,240))

        screen.blit(box,(230,10))
        screen.blit(text,(270,18))

    pygame.display.flip()


def main():

    gs = GameState()
    mg = MoveGenerator(gs)
    ai = ChessAI(gs,mg)

    load_images()

    human_white = True

    selected_sq = ()
    player_clicks = []

    running = True

    while running:

        status = mg.get_game_status()

        if status == "checkmate":
            winner = "Black" if gs.white_to_move else "White"

            draw_game(gs, selected_sq, mg.get_legal_moves(), mg.in_check())
            draw_end_screen(f"{winner} Wins by Checkmate")

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        running = False

            continue


        if status == "stalemate":
            draw_game(gs, selected_sq, mg.get_legal_moves(), mg.in_check())
            draw_end_screen("Draw by Stalemate")

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        running = False

            continue

        if gs.white_to_move != human_white:
            move = ai.get_best_move(3)
            if move:
                gs.make_move(move)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:

                if gs.white_to_move == human_white:

                    x,y = pygame.mouse.get_pos()

                    col = x//SQ
                    row = y//SQ

                    if selected_sq==(row,col):
                        selected_sq=()
                        player_clicks=[]
                    else:
                        selected_sq=(row,col)
                        player_clicks.append(selected_sq)

                    if len(player_clicks)==2:

                        legal_moves = mg.get_legal_moves()

                        for move in legal_moves:
                            if (
                                move.start_row==player_clicks[0][0]
                                and
                                move.start_col==player_clicks[0][1]
                                and
                                move.end_row==player_clicks[1][0]
                                and
                                move.end_col==player_clicks[1][1]
                            ):
                                gs.make_move(move)
                                break

                        selected_sq=()
                        player_clicks=[]

        draw_game(gs, selected_sq, mg.get_legal_moves(), mg.in_check())

    pygame.quit()
    sys.exit()


def draw_end_screen(message):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0,0,0))
    screen.blit(overlay,(0,0))

    font_big = pygame.font.SysFont("arial",48,True)
    font_small = pygame.font.SysFont("arial",32)

    text = font_big.render(message, True, (255,255,255))
    sub  = font_small.render(
        "Close window to exit",
        True,
        (220,220,220)
    )

    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2-30))
    sub_rect  = sub.get_rect(center=(WIDTH//2, HEIGHT//2+35))

    screen.blit(text,text_rect)
    screen.blit(sub,sub_rect)

    pygame.display.flip()


if __name__=="__main__":
    main()