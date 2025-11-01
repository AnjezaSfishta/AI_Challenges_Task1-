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