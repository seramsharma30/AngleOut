import os
from flask import Flask
from app.firebase_db import init_firebase_db
from dotenv import load_dotenv
from datetime import timedelta


dotenv_path = 'config.env'
load_dotenv(dotenv_path)

app = Flask(__name__)


app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)


firebase_db = init_firebase_db()
if firebase_db is None:
    print("Failed to connect to database")






from app.routes import default_routes, gsc_api_auth, db_apis

