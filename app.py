# app.py
from flask import Flask
from routes.main import main
from routes.entername import entername_bp
from routes.upload import upload
from routes.short import short
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


app = Flask(__name__)
app.register_blueprint(main)
app.register_blueprint(entername_bp)
app.register_blueprint(upload)
app.register_blueprint(short)

if __name__ == '__main__':
    app.run(debug=True)
