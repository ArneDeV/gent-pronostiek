from flask import render_template, redirect, url_for
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    return render_template('500.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return redirect(url_for("matches"))