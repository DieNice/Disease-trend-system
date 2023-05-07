
from datetime import datetime

import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import dash_table
from dash import dcc, html


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


def trends_layout_detail():
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
                     dcc.DatePickerRange(id="date-range-2",
                    start_date=get_start_date(),
                    end_date=get_end_date())]),
            dbc.Col(dbc.Button("Обновить тренд", color="primary",
                className="me-1", id="btn-2")),
            dbc.Col()
        ]),
        dbc.Row(html.Br()),

        dbc.Row([dash_table.DataTable(id="table-1", sort_mode='multi'),
                 dcc.Tooltip(id="graph-tooltip")]),
        dbc.Row(className="justify-content-md-center"),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
        dbc.Row(html.Br()),
    ])
