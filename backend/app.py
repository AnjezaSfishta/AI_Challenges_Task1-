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
    gen = SudokuGenerator()
    puzzle = gen.generate_sudoku(level, ensure_unique=ensure_unique, max_checks=50)

    return jsonify({"status": "ok", "level": level, "unique": ensure_unique, "puzzle": puzzle})

@app.post("/solve_sudoku")
@app.post("/solve_sudoku")
def sudoku_solve():
    try:
        data = request.get_json(force=True) or {}
        puzzle = data.get("puzzle")

        if (not puzzle or not isinstance(puzzle, list) or len(puzzle) != 9
            or any(not isinstance(r, list) or len(r) != 9 for r in puzzle)):
            return jsonify({
                "status": "error",
                "message": "Missing or invalid 'puzzle' (must be 9x9 list[list[int]])."
            }), 400

        solver = SudokuSolver(puzzle)
        klass = solver.classify_puzzle(puzzle, limit=2)

        if klass["status"] == "invalid":
            return jsonify({
                "status": "invalid",
                "message": "Invalid puzzle: duplicate values in row, column, or block."
            }), 200

        if klass["status"] == "unsolvable":
            return jsonify({
                "status": "unsolvable",
                "message": "This Sudoku has 0 valid solutions."
            }), 200

        if klass["status"] == "unique":
            return jsonify({
                "status": "unique",
                "message": "Unique solution found ✅",
                "solution": klass["solution"]
            }), 200

        if klass["status"] == "multiple":
            return jsonify({
                "status": "multiple",
                "message": "Multiple valid solutions exist ⚠️ (showing one).",
                "solution": klass["solution"]
            }), 200

        return jsonify({
            "status": "error",
            "message": "Unexpected solver state."
        }), 500

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal error: {e}"
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
