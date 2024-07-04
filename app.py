# app.py
from flask import Flask
from routes.main import main
from routes.entername import entername_bp
from routes.upload import upload


app = Flask(__name__)
app.register_blueprint(main)
app.register_blueprint(entername_bp)
app.register_blueprint(upload)

if __name__ == '__main__':
    app.run(debug=True)
