def is_valid(board, row, col, num, n):
    for i in range(n):
        if board[row][i] == num or board[i][col] == num:
            return False
    return True

def find_empty_cell(board, n):
    for r in range(n):
        for c in range(n):
            if board[r][c] == 0:
                return r, c
    return None, None

def latin_backtrack(board, n):
    row, col = find_empty_cell(board, n)
    if row is None:  # board is full
        return True

    for num in range(1, n + 1):
        if is_valid(board, row, col, num, n):
            board[row][col] = num
            if latin_backtrack(board, n):
                return True
            board[row][col] = 0
    return False

def dfs_limited(board, n, depth, max_depth):
    row, col = find_empty_cell(board, n)
    if row is None:
        return True
    if depth >= max_depth:
        return False
    for num in range(1, n + 1):
        if is_valid(board, row, col, num, n):
            board[row][col] = num
            if dfs_limited(board, n, depth + 1, max_depth):
                return True
            board[row][col] = 0
    return False

def iddfs(board, n, max_depth=200):
    for limit in range(1, max_depth + 1):
        test_board = [row[:] for row in board]  # fresh copy for each depth
        if dfs_limited(test_board, n, 0, limit):
            return test_board
    return None

def latin_square_solver(input_board, algorithm="Backtracking", depth_limit=None):
    n = len(input_board)

    # Use a fresh copy
    board_for_solver = [row[:] for row in input_board]

    if algorithm == "Backtracking":
        solution_board = [row[:] for row in board_for_solver]
        success = latin_backtrack(solution_board, n)
        return solution_board if success else None
    elif algorithm == "IDDFS":
        max_depth = depth_limit or (n * n)
        solution_board = iddfs([row[:] for row in board_for_solver], n, max_depth)
        return solution_board
    else:
        raise ValueError("Unsupported algorithm: choose 'Backtracking' or 'IDDFS'")
