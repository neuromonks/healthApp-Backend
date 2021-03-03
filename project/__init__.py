# init.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail, Message

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    # enter below your gmail credentials make sure less secure app feature is on in your gmail settings
    mail_settings = {
        "MAIL_SERVER": 'smtp.gmail.com',
        "MAIL_PORT": 587,
        "MAIL_USE_TLS": True,
        "MAIL_USE_SSL": False,
        "MAIL_USERNAME": 'yourgmail',
        "MAIL_PASSWORD": 'password'
    }

    app.config.update(mail_settings)


    app.config['SECRET_KEY'] = '6jvq5wrZ!LTGnPZGSAj9Z@m&VnPZGSA#j9Z2z8gO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['JSON_SORT_KEYS'] = False

    db.init_app(app)
    mail = Mail(app)
    migrate.init_app(app, db)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
