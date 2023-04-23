
import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import date, datetime
import plotly.graph_objs as go


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


fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])])


def trends_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([html.P("Введите количество дней для формирования тренда"),
                dbc.Input("id_doorstep_input", type="number", min=3,
                          className="mb-10", size="sm",
                          placeholder="Порог тренда")]),
            dbc.Col([html.P("Выберите диапазон"),
                     dcc.DatePickerRange(id="date-range-1",
                    min_date_allowed=date(2000, 8, 5),
                    start_date=get_start_date(),
                    end_date=get_end_date())]),
            dbc.Col(),
            dbc.Col()
        ]),
        dbc.Row(html.Br()),
        dbc.Row(dcc.Graph(id="graph-1", figure=fig)),
        dbc.Row(dbc.Button("Построить тренд", color="primary",
                className="me-1 col-6", id="btn-1"), className="justify-content-md-center"),
    ])
