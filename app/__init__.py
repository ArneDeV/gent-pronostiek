from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
load_dotenv(dotenv_path="/home/ArneDeV/gent-pronostiek/.env")

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database and migration tools
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Login settings
login = LoginManager(app)
login.login_view = "login"


from app import routes, models
