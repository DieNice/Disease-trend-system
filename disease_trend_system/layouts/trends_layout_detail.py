
from datetime import datetime
from typing import List

import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import dash_table, dcc, html
from dash.dash_table.Format import Format, Scheme

from disease_trend_system.config import (hostname_db, name_db, password_db,
                                         port, username_db)
from disease_trend_system.services.symptom_complexes_dao import SymptomsDAO

COLUMNS = [
    dict(id="symptom_complex_hash", name="ИД симмптомокомплекса"),
    dict(id="date", name="Дата симптомокомплекса"),
    dict(id="percent_people", name="Процент людей",
         type="numeric",
         format=Format(precision=2, scheme=Scheme.percentage)),
    dict(id="total_number", name="Общее число людей", type="numeric",
         format=Format(precision=0, scheme=Scheme.fixed)),
    dict(id="extra", name="Описание симптомокомлекса")]
MAX_PAGE_SIZE = 50


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


def get_cities() -> List[str]:
    symptom_dao = SymptomsDAO(
        username_db, password_db, hostname_db, port, name_db)
    return symptom_dao.get_cities()


fig = go.Figure(data=[])


def trends_layout_detail():
    return dbc.Container([
        dbc.Row(html.Br()),
        dbc.Row([
            dbc.Col([html.P("Введите количество дней для формирования тренда"),
                dbc.Input("id_threshold_input-2", type="number", min=1,
                          className="mb-10", size="sm",
                          pattern='\d*',
                          value=1,
                          placeholder="Порог тренда")]),
            dbc.Col([html.P("Выберите диапазон"),
                     dcc.DatePickerRange(id="date-range-2",
                    start_date=get_start_date(),
                    end_date=get_end_date())], width="auto"),
            dbc.Col([html.P("Выберите город"),
                     dcc.Dropdown(id="dropdown-city-2",
                     options=get_cities(),
                     placeholder="Выберите город",)]),
            dbc.Col([html.P("Выберите район"),
                     dcc.Dropdown(id="dropdown-region-2",
                     options=[],
                     placeholder="Выберите район",)])
        ]),
        dbc.Row([
            dbc.Col([html.P("Выберите учреждение"),
                     dcc.Dropdown(id="dropdown-hospital-2",
                                  options=[],
                                  placeholder="Выберите учреждение",)],
                    width=8),
            dbc.Col([html.P("designed by PDA", style={"color": "white"}),
                     dbc.Button("Обновить тренд", color="primary",
                                className="me-1", id="btn-2", size="sm",
                                outline=True)])]),
        dbc.Row(html.Br()),

        dbc.Row([dash_table.DataTable(data=[], id="table-1",
                                      columns=COLUMNS,
                                      filter_action="native",
                                      sort_action="native",
                                      sort_mode="multi",
                                      page_action="native",
                                      page_current=0,
                                      page_size=MAX_PAGE_SIZE,
                                      style_table={
                                          'height': '70vh', 'overflowY': 'auto'},
                                      style_header={
            'backgroundColor': '#6A5ACD',
            'fontWeight': 'bold',
            'color': "white"
        },
            style_data={
            'color': 'black',
            'backgroundColor': 'white',
            'whiteSpace': 'normal'
        },
            style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(220, 220, 220)',
            }
        ],
            style_as_list_view=True),
            dcc.Tooltip(id="graph-tooltip")]),
        dbc.Row(className="justify-content-md-center"),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
    ])
