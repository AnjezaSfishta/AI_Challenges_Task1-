import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from socialgolfer import find_max_weeks

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

# ---------------- SOCIAL GOLFERS PROBLEM ---------------- #
@app.route("/golfers")
def golfers_page():
    return render_template("golfers.html")

@app.route("/solve", methods=["POST"])
def solve_golfers():
    data = request.get_json()
    num_players = int(data.get("num_players", 32))
    group_size = int(data.get("group_size", 4))
    algorithm = data.get("algorithm", "Depth-First Search (DFS)")
    depth_limit = data.get("depth_limit", None)
    if depth_limit:
        depth_limit = int(depth_limit)

    import time
    start = time.time()
    schedule, weeks = find_max_weeks(num_players, group_size, algorithm, depth_limit)
    elapsed = round(time.time() - start, 4)

    if not schedule:
        return jsonify({"success": False, "message": "No valid schedule found.", "elapsed_time": elapsed})

    return jsonify({"success": True, "weeks": weeks, "schedule": schedule, "elapsed_time": elapsed})

if __name__ == "__main__":
    app.run(debug=True)
