
from datetime import date, datetime
from typing import List

import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import dcc, html

from disease_trend_system.config import (hostname_db, name_db, password_db,
                                         port, username_db)
from disease_trend_system.services.symptom_complexes_dao import SymptomsDAO


def get_start_date() -> datetime:
    """Получить дату на начало месяца

    Returns:
        datetime: дата
    """
    tmp_date = datetime.now()
    tmp_date = tmp_date.replace(day=1)
    return tmp_date


def get_end_date() -> datetime:
    """Получить текущую дату

    Returns:
        datetime: дата
    """
    return datetime.now()


fig = go.Figure(data=[])


def get_cities() -> List[str]:
    symptom_dao = SymptomsDAO(
        username_db, password_db, hostname_db, port, name_db)
    return symptom_dao.get_cities()


def trends_layout():
    return dbc.Container([
        dbc.Row(html.Br()),
        dbc.Row([
            dbc.Col([html.P("Введите количество дней для формирования тренда"),
                dbc.Input("id_threshold_input", type="number", min=1,
                          className="mb-10", size="sm",
                          pattern='\d*',
                          value=1,
                          placeholder="Порог тренда")]),
            dbc.Col([html.P("Выберите диапазон"),
                     dcc.DatePickerRange(id="date-range-1",
                    start_date=get_start_date(),
                    end_date=get_end_date())], width="auto"),
            dbc.Col([html.P("Выберите город"),
                     dcc.Dropdown(id="dropdown-city-1",
                     options=get_cities(),
                     placeholder="Выберите город",)]),
            dbc.Col([html.P("Выберите район"),
                     dcc.Dropdown(id="dropdown-region-1",
                     options=[],
                     placeholder="Выберите район",)])
        ]),
        dbc.Row([
            dbc.Col([html.P("Выберите учреждение"),
                     dcc.Dropdown(id="dropdown-hospital-1",
                                  options=[],
                                  placeholder="Выберите учреждение",)],
                    width=8),
            dbc.Col([html.P("designed by PDA",style={"color": "white"}),
                     dbc.Button("Обновить тренд", color="primary",
                                className="me-1", id="btn-1", size="sm",
                                outline=True)])]),
        dbc.Row(html.Br()),

        dbc.Row([dcc.Graph(id="graph-1", figure=fig,
                style={"width": "100vw", "height": "80vh"},
                clear_on_unhover=True),
            dcc.Tooltip(id="graph-tooltip")]),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
    ], class_name="container-xxl")
