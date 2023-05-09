from datetime import datetime

import dash_bootstrap_components as dbc
import sqlalchemy
from dash_extensions.enrich import DashProxy, MultiplexerTransform
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin
from flask_restful import Api
from sqlalchemy import Column, DateTime, Integer, MetaData, String, event
from sqlalchemy.orm import Session, declarative_base
from werkzeug.security import check_password_hash, generate_password_hash

from disease_trend_system.config import (SECRET_KEY, hostname_db, name_db,
                                         password_db, port, username_db)
from disease_trend_system.endpoints import SymptomsResource

Base = declarative_base()


class User(Base, UserMixin):
    """Класс пользователя
    """

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(120), nullable=False)
    role = Column(Integer, nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def __repr__(self):
        return f"User {self.id}:{self.username}>"

    def set_password(self, password: str) -> None:
        """Установка пароля

        Args:
            password (str): пароль
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self,  password: str) -> bool:
        """Проверка пароля на соответствие

        Args:
            password (str): пароль

        Returns:
            bool: Да/Нет
        """
        return check_password_hash(self.password, password)


@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value != oldvalue:
        return generate_password_hash(value)
    return value


def create_session():
    usr = username_db
    pswd = password_db
    host = hostname_db
    db = name_db
    engine = sqlalchemy.create_engine(
        f"mysql+pymysql://{usr}:{pswd}@{host}:{port}/{db}")
    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata.create_all(bind=engine, checkfirst=True)
    Base.metadata.create_all(engine)
    return Session(engine)


session = create_session()

app = DashProxy(__name__, assets_folder='assets',
                external_stylesheets=[dbc.themes.MATERIA], transforms=[MultiplexerTransform(),])


app.title = "Disease trend system"


srv = app.server
srv.config['SECRET_KEY'] = SECRET_KEY
srv.config['FLASK_ADMIN_SWATCH'] = 'cosmo'
admin = Admin(srv, name='trend system', template_mode='bootstrap3')

admin.add_view(ModelView(User, session))


api = Api(srv)


api.add_resource(SymptomsResource, '/symptoms')

app.config.suppress_callback_exceptions = True


login_manager = LoginManager()
login_manager.init_app(srv)
login_manager.login_view = '/login'


@ login_manager.user_loader
def load_user(user_id):
    ''' This function loads the user by user id. Typically this looks up the user from a user database.
        We won't be registering or looking up users in this example, since we'll just login using LDAP server.
        So we'll simply return a User object with the passed in username.
    '''
    session = create_session()

    with session:
        user = session.query(User).filter_by(id=user_id).first()

    return user
