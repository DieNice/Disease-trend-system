
from datetime import datetime

import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import dash_table, dcc, html
from dash.dash_table.Format import Format, Scheme


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
                    end_date=get_end_date())]),
            dbc.Col(dbc.Button("Обновить тренд", color="primary",
                className="me-1", id="btn-2")),
            dbc.Col()
        ]),
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
