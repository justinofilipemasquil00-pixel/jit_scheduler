from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager 
from flask_migrate import Migrate
from flask_mail import Mail  # ← ADICIONE ESTA LINHA
from config import Config 
 
db = SQLAlchemy() 
login_manager = LoginManager() 
migrate = Migrate()
mail = Mail()  # ← ADICIONE ESTA LINHA
 
@login_manager.user_loader 
def load_user(user_id): 
    from app.models import User 
    return User.query.get(int(user_id)) 
 
def create_app(): 
    app = Flask(__name__) 
    app.config.from_object(Config) 

    db.init_app(app) 
    login_manager.init_app(app) 
    migrate.init_app(app, db)
    mail.init_app(app)  # ← ADICIONE ESTA LINHA
    login_manager.login_view = 'auth.login' 

    from app.routes.main import main_bp 
    from app.routes.auth import auth_bp 
    from app.routes.usuario import usuario_bp 
    from app.routes.admin import admin_bp 

    app.register_blueprint(main_bp) 
    app.register_blueprint(auth_bp) 
    app.register_blueprint(usuario_bp, url_prefix='/usuario') 
    app.register_blueprint(admin_bp, url_prefix='/admin') 

    return app