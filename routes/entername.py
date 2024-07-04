# routes/entername.py
from flask import Blueprint, render_template, request

entername_bp = Blueprint('entername', __name__)

@entername_bp.route('/entername', methods=['GET', 'POST'])
def entername():
    if request.method == 'POST':
        name = request.form['name']
        return render_template('entername.html', name=name)
    else:
        return render_template('entername.html')
