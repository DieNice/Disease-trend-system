import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashProxy, MultiplexerTransform
from flask import Flask
from flask_restful import Api

from disease_trend_system.endpoints import SymptomsResource

app = DashProxy(__name__, assets_folder='assets',
                external_stylesheets=[dbc.themes.MATERIA], transforms=[MultiplexerTransform()])

app.title = "Disease trend system"

srv = app.server

api = Api(srv)

api.add_resource(SymptomsResource, '/symptoms')

app.config.suppress_callback_exceptions = True
