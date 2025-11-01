def is_valid(board, row, col, num, n):
    for i in range(n):
        if board[row][i] == num or board[i][col] == num:
            return False
    return True

def latin_backtrack(board, n):
    for row in range(n):
        for col in range(n):
            if board[row][col] == 0:
                for num in range(1, n + 1):
                    if is_valid(board, row, col, num, n):
                        board[row][col] = num
                        if latin_backtrack(board, n):
                            return True
                        board[row][col] = 0
                return False
    return True

def find_empty_cell(board, n):
    for row in range(n):
        for col in range(n):
            if board[row][col] == 0:
                return row, col
    return None, None