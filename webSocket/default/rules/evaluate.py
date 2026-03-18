WINNING_COMBINATIONS = [
    (0, 1, 2),  # filas
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),  # columnas
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),  # diagonales
    (2, 4, 6),
]

def evaluate_match(board):
    # chequear ganador
    for a, b, c in WINNING_COMBINATIONS:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]

    # chequear empate
    if all(cell != "" for cell in board):
        return "DRAW"

    # si no pasó nada de lo anterior
    return "CONTINUE"