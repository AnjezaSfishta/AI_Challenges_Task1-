import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from sudoku import SudokuGenerator, SudokuSolver

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "frontend", "static"),
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
)
CORS(app)

# ---------------- HOME PAGE ---------------- #
@app.route("/")
def home():
    return render_template("home.html")


# ---------------- SUDOKU ---------------- #
@app.route("/sudoku")
def sudoku_page():
    return render_template("sudoku.html")

@app.get("/generate")
def sudoku_generate():
    level = (request.args.get("level", "easy") or "easy").lower()
    if level not in {"easy", "medium", "hard"}:
        level = "easy"

    ensure_unique = request.args.get("unique", "0") in {"1", "true", "True"}

    # default timeout 30s
    timeout_ms = request.args.get("timeout_ms", type=int, default=30000)
    timeout_sec = (timeout_ms / 1000.0) if timeout_ms and timeout_ms > 0 else None

    gen = SudokuGenerator()
    puzzle = gen.generate_sudoku(level, ensure_unique=ensure_unique, max_checks=50, timeout_sec=timeout_sec)

    return jsonify({"status": "ok", "level": level, "unique": ensure_unique, "puzzle": puzzle})

@app.post("/solve_sudoku")
def sudoku_solve():
    data = request.get_json(force=True) or {}
    puzzle = data.get("puzzle")
    if not puzzle:
        return jsonify({"status": "error", "message": "Missing 'puzzle'."}), 400

    # default timeout 30s
    timeout_ms = data.get("timeout_ms", 30000)
    max_nodes  = data.get("max_nodes", 2_000_000)
    timeout_sec = (timeout_ms / 1000.0) if timeout_ms and timeout_ms > 0 else None

    solver = SudokuSolver(puzzle)
    ok, solution, stats = solver.solve_bfs_backtracking(max_time_sec=timeout_sec, max_nodes=max_nodes)

    payload = {
        "duration_ms": stats.get("duration_ms"),
        "timed_out":  stats.get("timed_out", False),
    }

    if ok and solution:
        payload.update({"status": "ok", "solution": solution})
        return jsonify(payload)
    else:
        payload.update({"status": "error", "message": "Timeout or no solution found"})
        return jsonify(payload), 200


if __name__ == "__main__":
    app.run(debug=True)
