import dash_bootstrap_components as dbc
import flask_admin as admin
import sqlalchemy.dialects
from dash_extensions.enrich import DashProxy, MultiplexerTransform
from flask import redirect
from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user
from flask_restful import Api
from sqlalchemy import MetaData
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy_utils import JSONType
from werkzeug.security import check_password_hash, generate_password_hash

from disease_trend_system.config import (SECRET_KEY, hostname_db, name_db,
                                         password_db, port, username_db)
from disease_trend_system.endpoints import SymptomsResource
from disease_trend_system.models import Base, User, create_admin_user


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


app = DashProxy(__name__, assets_folder='assets',
                external_stylesheets=[dbc.themes.MATERIA], transforms=[MultiplexerTransform(),])


app.title = "Disease trend system"


srv = app.server
srv.config['SECRET_KEY'] = SECRET_KEY
srv.config['FLASK_ADMIN_SWATCH'] = 'cosmo'


class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect('/desease-knowlege-base-dash/login')
        return super(MyAdminIndexView, self).index()


class DiseaseModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 1

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect('/desease-knowlege-base-dash/login')


admin = Admin(srv, name='trend system',
              index_view=MyAdminIndexView(), template_mode='bootstrap4')
admin.add_view(DiseaseModelView(User, create_session()))


api = Api(srv)


api.add_resource(SymptomsResource, '/symptoms')

app.config.suppress_callback_exceptions = True


login_manager = LoginManager()
login_manager.init_app(srv)
login_manager.login_view = '/login'
create_admin_user()


@ login_manager.user_loader
def load_user(user_id):
    ''' This function loads the user by user id
    '''
    session = create_session()

    with session:
        user = session.query(User).filter_by(id=user_id).first()
    session.close()
    del session
    return user
