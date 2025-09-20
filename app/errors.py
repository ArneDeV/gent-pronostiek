from flask import redirect, url_for
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    return redirect(url_for("matches"))

@app.errorhandler(500)
def internal_error(error):
    return redirect(url_for("matches"))