from flask import make_response, render_template, send_from_directory
from flask import Blueprint
bp = Blueprint("common", __name__)

@bp.route("/", methods=["GET"])
def main_entry():
    return make_response(render_template("index.html"))
