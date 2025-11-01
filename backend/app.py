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
    """Generate a Sudoku puzzle by level."""
    level = (request.args.get("level", "easy") or "easy").lower()
    if level not in {"easy", "medium", "hard"}:
        level = "easy"
    gen = SudokuGenerator()
    puzzle = gen.generate_sudoku(level)
    return jsonify({"status": "ok", "level": level, "puzzle": puzzle})

@app.post("/solve_sudoku")
def sudoku_solve():
    """Solve a Sudoku puzzle posted as JSON."""
    data = request.get_json(force=True) or {}
    puzzle = data.get("puzzle")
    if not puzzle:
        return jsonify({"status": "error", "message": "Missing 'puzzle'."}), 400

    solver = SudokuSolver(puzzle)
    ok, solution = solver.solve_bfs_backtracking()
    if ok and solution:
        return jsonify({"status": "ok", "solution": solution})
    else:
        return jsonify({"status": "error", "message": "No solution found."}), 400

if __name__ == "__main__":
    app.run(debug=True)
